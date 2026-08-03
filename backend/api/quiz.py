"""
Quiz generation endpoint.

Generates fill-in-the-blank MCQ questions from uploaded study material.
Tiered approach:
  Tier 1 — Sentences with definition patterns (highest quality)
  Tier 2 — Content-rich sentences from chunks
  Tier 3 — Reject with informative error (no hardcoded garbage)
"""

import random
import re
import logging
from fastapi import APIRouter, HTTPException
from rag.retriever import retrieve_chunks, retrieve_all_document_chunks
from models.schemas import QuizRequest, QuizResponse, QuizQuestion

logger = logging.getLogger(__name__)
router = APIRouter()

# Words too generic to be useful quiz answers
_SKIP_WORDS = {
    "the", "this", "that", "they", "them", "their", "there", "then", "than",
    "which", "what", "when", "where", "some", "such", "with", "from", "have",
    "been", "will", "also", "just", "more", "very", "each", "both", "many",
    "other", "these", "those", "into", "over", "after", "about",
}


def _is_meaningful_answer(word: str) -> bool:
    """Return True if a word makes a good quiz answer."""
    clean = re.sub(r"[^\w]", "", word)
    if len(clean) < 4:
        return False
    if clean.lower() in _SKIP_WORDS:
        return False
    if not clean.isalnum():
        return False
    return True


def _build_question_from_sentence(sentence: str) -> QuizQuestion | None:
    """
    Attempt to build one MCQ fill-in-the-blank from a sentence.
    Returns None if the sentence is not suitable.
    """
    words = sentence.split()
    if len(words) < 8:
        return None

    # Candidate answer words: meaningful nouns/terms from the middle of the sentence
    candidates = [
        w for w in words[2:-2]
        if _is_meaningful_answer(w)
    ]
    if not candidates:
        return None

    target = random.choice(candidates)
    clean_target = re.sub(r"[^\w]", "", target)
    if not clean_target:
        return None

    blanked = sentence.replace(target, "_______", 1)
    question_text = f'Fill in the blank:\n\n"{blanked}"'

    # Generate plausible distractors from other candidate words in the same sentence
    other_candidates = [
        re.sub(r"[^\w]", "", w) for w in candidates
        if re.sub(r"[^\w]", "", w).lower() != clean_target.lower()
    ]
    other_candidates = list(dict.fromkeys(other_candidates))  # deduplicate

    if len(other_candidates) >= 3:
        distractors = random.sample(other_candidates, 3)
    else:
        # Pad with realistic-sounding alternatives
        distractors = other_candidates + [
            f"{clean_target}s",
            f"non-{clean_target}",
            "None of the above",
        ]
        distractors = distractors[:3]

    options_raw = [clean_target] + distractors
    random.shuffle(options_raw)

    labels = ["A", "B", "C", "D"]
    formatted_options = [f"{labels[i]}) {opt}" for i, opt in enumerate(options_raw[:4])]
    correct_answer = next(
        f"{labels[i]}) {opt}"
        for i, opt in enumerate(options_raw[:4])
        if opt == clean_target
    )

    return QuizQuestion(
        question=question_text,
        options=formatted_options,
        correct_answer=correct_answer,
        explanation=f'The original sentence reads: "{sentence}"',
    )


@router.post("/generate-quiz", response_model=QuizResponse, summary="Generate MCQ quiz")
async def generate_quiz(request: QuizRequest):
    """
    Generate multiple-choice fill-in-the-blank questions from study material.

    Questions are derived directly from the uploaded document text.
    If not enough suitable sentences are found, returns however many could be generated.
    """
    if request.num_questions < 1 or request.num_questions > 20:
        raise HTTPException(status_code=400, detail="num_questions must be between 1 and 20")

    if request.document_id:
        chunks = retrieve_all_document_chunks(request.document_id)
        chunks = chunks[:15]
    else:
        chunks = retrieve_chunks(
            query="main concepts key topics important definitions facts",
            top_k=10,
        )

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No study content found. Please upload a PDF first.",
        )

    # Collect candidate sentences
    all_sentences: list[str] = []
    for c in chunks:
        text = c.get("text") or ""
        sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 40]
        all_sentences.extend(sentences)

    random.shuffle(all_sentences)

    questions: list[QuizQuestion] = []
    attempted_sentences = set()

    for sentence in all_sentences:
        if len(questions) >= request.num_questions:
            break
        normalized = sentence.lower().strip()
        if normalized in attempted_sentences:
            continue
        attempted_sentences.add(normalized)

        q = _build_question_from_sentence(sentence)
        if q:
            questions.append(q)

    if not questions:
        raise HTTPException(
            status_code=422,
            detail=(
                "Could not generate quiz questions from the uploaded content. "
                "The document may contain too little text or primarily scanned images. "
                "Try uploading a text-rich PDF."
            ),
        )

    logger.info("Generated %d quiz questions (requested %d)", len(questions), request.num_questions)

    return QuizResponse(
        questions=questions[: request.num_questions],
        total=len(questions[: request.num_questions]),
        difficulty=request.difficulty,
    )
