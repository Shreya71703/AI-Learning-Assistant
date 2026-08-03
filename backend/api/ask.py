"""
Ask endpoint — Semantic search + Gemini-powered RAG answers.

Flow:
1. Embed the user question via sentence-transformers
2. Retrieve top-K relevant chunks from ChromaDB
3. Build a grounded context string with page citations
4. Call Google Gemini (if GEMINI_API_KEY is set) to synthesize an answer
5. Fall back to direct retrieval if Gemini is unavailable
"""

import logging
import os

from fastapi import APIRouter, HTTPException
from models.schemas import AnswerResponse, QuestionRequest
from rag.retriever import build_context, retrieve_chunks

logger = logging.getLogger(__name__)
router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def _gemini_answer(question: str, context: str) -> str:
    """
    Call Google Gemini Flash to synthesize a grounded answer.
    Returns the model's response string, or raises an exception on failure.
    """
    import google.generativeai as genai  # lazy import — only if key is present

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    system_prompt = (
        "You are an expert AI study assistant. "
        "Answer the student's question using ONLY the provided context excerpts. "
        "Be concise, accurate, and educational. "
        "If the context does not contain enough information to answer, say so honestly. "
        "Do NOT make up information not present in the context. "
        "Format your answer with clear paragraphs. Use bullet points for lists."
    )

    full_prompt = (
        f"{system_prompt}\n\n"
        f"## Context from study materials:\n{context}\n\n"
        f"## Student Question:\n{question}\n\n"
        f"## Answer:"
    )

    response = model.generate_content(full_prompt)
    return response.text.strip()


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    if len(question) > 2000:
        raise HTTPException(status_code=400, detail="Question is too long (max 2000 characters)")

    # --- Retrieve relevant chunks ---
    chunks = retrieve_chunks(
        query=question,
        top_k=request.top_k,
        document_id=request.document_id,
    )

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No relevant content found. Please upload a document first.",
        )

    # Build source citations list for the response
    sources = [
        {
            "filename": c["filename"],
            "page": c["page"],
            "similarity": c["similarity"],
            "preview": c["text"][:200] + "..." if len(c["text"]) > 200 else c["text"],
        }
        for c in chunks
    ]

    # --- Attempt Gemini RAG answer ---
    if GEMINI_API_KEY and not request.direct_retrieval:
        try:
            context = build_context(chunks, max_chars=4000)
            answer = _gemini_answer(question, context)
            return AnswerResponse(answer=answer, sources=sources, model_used="gemini-1.5-flash")
        except Exception as exc:
            logger.warning("Gemini call failed, falling back to direct retrieval: %s", exc)

    # --- Direct retrieval fallback ---
    top_chunks_text = "\n\n".join(
        [f"📄 **[{c['filename']}, Page {c['page']}]**\n{c['text']}" for c in chunks[:3]]
    )
    answer = (
        "Here is the most relevant content from your study materials:\n\n"
        + top_chunks_text
    )
    model_used = "direct-retrieval"

    return AnswerResponse(answer=answer, sources=sources, model_used=model_used)
