"""
Summary endpoint.

Generates a structured document summary using extractive summarization:
- Scores sentences by term frequency (TF) weighted by position and length
- Returns the top N sentences as a coherent summary
- Extracts bullet-point key concepts from definition patterns
"""

import logging
import re
from collections import Counter

from fastapi import APIRouter, HTTPException
from models.schemas import SummaryRequest, SummaryResponse
from rag.retriever import retrieve_all_document_chunks, retrieve_chunks

logger = logging.getLogger(__name__)
router = APIRouter()

# Common English stop words to ignore in TF scoring
_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "it", "its", "this", "that", "these", "those",
    "we", "our", "you", "your", "he", "she", "they", "their", "as", "if",
    "so", "not", "no", "can", "than", "then", "also", "just", "more",
}


def _tokenize(text: str) -> list[str]:
    return [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", text) if w.lower() not in _STOP_WORDS]


def _extractive_summary(sentences: list[str], target_sentences: int) -> str:
    """
    Score each sentence by TF of its content words, weighted by:
    - Sentence position (earlier = slightly more important)
    - Length (very short or very long sentences penalized)
    Returns the top N sentences in their original order.
    """
    if not sentences:
        return ""

    # Build term frequencies across all sentences
    all_words = _tokenize(" ".join(sentences))
    tf = Counter(all_words)
    max_freq = max(tf.values()) if tf else 1

    scored = []
    for idx, sent in enumerate(sentences):
        words = _tokenize(sent)
        if not words:
            continue
        # TF score: normalized sum of word frequencies
        score = sum(tf[w] / max_freq for w in words) / len(words)
        # Position bonus: first 20% of sentences get a small boost
        if idx < max(1, len(sentences) * 0.2):
            score *= 1.15
        # Length penalty: sentences with 5–40 words are ideal
        word_count = len(sent.split())
        if word_count < 5 or word_count > 60:
            score *= 0.6
        scored.append((idx, score, sent))

    # Pick top N by score, then re-sort by original position
    scored.sort(key=lambda x: x[1], reverse=True)
    top = sorted(scored[:target_sentences], key=lambda x: x[0])
    return " ".join(s for _, _, s in top)


def _extract_key_points(chunks: list[dict], limit: int = 6) -> list[str]:
    """
    Extract key bullet points from definition/concept sentences.
    """
    indicators = [" refers to ", " is defined as ", " is a ", " means ", " are ", " is the "]
    key_points = []
    seen = set()

    for c in chunks:
        text = c.get("text") or ""
        sentences = [s.strip() for s in text.split(".") if 20 < len(s.strip()) < 200]
        for s in sentences:
            s_lower = s.lower()
            for ind in indicators:
                if ind in s_lower:
                    normalized = re.sub(r"\s+", " ", s.strip().lower())
                    if normalized not in seen:
                        seen.add(normalized)
                        point = s.strip()
                        if point and not point[-1] in ".!?":
                            point += "."
                        key_points.append(point[0].upper() + point[1:])
                    break
            if len(key_points) >= limit:
                return key_points

    # Fallback: first sentence of each chunk
    for c in chunks:
        if len(key_points) >= limit:
            break
        text = c.get("text") or ""
        first = next((s.strip() for s in text.split(".") if len(s.strip()) > 25), None)
        if first:
            normalized = re.sub(r"\s+", " ", first.lower())
            if normalized not in seen:
                seen.add(normalized)
                point = first.strip()
                if not point[-1] in ".!?":
                    point += "."
                key_points.append(point[0].upper() + point[1:])

    return key_points


@router.post("/summary", response_model=SummaryResponse, summary="Generate document summary")
async def generate_summary(request: SummaryRequest):
    """
    Generate an extractive summary of uploaded study material.

    Uses TF-weighted sentence scoring to select the most informative sentences.
    Also returns a list of key bullet-point concepts.
    """
    if request.document_id:
        chunks = retrieve_all_document_chunks(request.document_id)
        chunks = chunks[:20]
    else:
        chunks = retrieve_chunks(
            query="overview introduction main topics key concepts",
            top_k=12,
        )

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No study content found. Please upload a PDF first.",
        )

    # Collect all sentences from chunks
    all_sentences: list[str] = []
    for c in chunks:
        text = c.get("text") or ""
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 20]
        all_sentences.extend(sentences)

    # Determine summary length
    target_map = {"short": 4, "medium": 8, "long": 14}
    target_sentences = target_map.get(request.length, 8)

    summary_text = _extractive_summary(all_sentences, target_sentences)
    if not summary_text:
        summary_text = " ".join(all_sentences[:target_sentences])

    key_points = _extract_key_points(chunks, limit=6)

    return SummaryResponse(
        summary=summary_text,
        key_points=key_points,
        word_count=len(summary_text.split()),
    )
