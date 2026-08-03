"""
File upload endpoint with PDF validation, size limiting, and vector storage.

Processing pipeline:
  PDF → text extraction (pypdf / OCR fallback) → cleaning → chunking
  → deduplication → embedding → ChromaDB storage
"""

import logging
import os
import uuid

from database.chroma import store_document
from fastapi import APIRouter, File, HTTPException, UploadFile
from models.schemas import UploadResponse
from services.ocr_service import extract_text_from_pdf
from utils.config import MAX_UPLOAD_BYTES, MAX_UPLOAD_MB
from utils.text_processing import (
    chunk_text,
    clean_text,
    merge_short_chunks,
    remove_duplicates,
)

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_MIME_TYPES = {"application/pdf"}
ALLOWED_EXTENSIONS = {".pdf"}


def _validate_upload(file: UploadFile) -> None:
    """Validate file extension and content-type before processing."""
    filename = file.filename or ""
    ext = os.path.splitext(filename)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are supported. Received: '{ext or 'unknown'}'",
        )
    # Content-Type is client-provided and can be spoofed, but it's an extra signal.
    content_type = (file.content_type or "").lower()
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type '{content_type}'. Expected 'application/pdf'.",
        )


@router.post("/upload", response_model=UploadResponse, summary="Upload a PDF document")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file for processing.

    - Validates file type and size (max configurable via MAX_UPLOAD_MB env var)
    - Extracts text using pypdf (fast) with OCR fallback for scanned PDFs
    - Chunks, deduplicates, and embeds text into ChromaDB
    - Returns document ID, chunk count, and page count
    """
    _validate_upload(file)

    document_id = str(uuid.uuid4())
    # Sanitize filename: strip directory separators
    safe_name = os.path.basename(file.filename or "document.pdf").replace(" ", "_")
    save_path = os.path.join(UPLOAD_DIR, f"{document_id}_{safe_name}")

    # ── Save file with size limit ─────────────────────────────────────────────
    try:
        bytes_written = 0
        with open(save_path, "wb") as out_file:
            chunk_size = 1024 * 64  # 64 KB read chunks
            while True:
                data = await file.read(chunk_size)
                if not data:
                    break
                bytes_written += len(data)
                if bytes_written > MAX_UPLOAD_BYTES:
                    out_file.close()
                    os.remove(save_path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum allowed size is {MAX_UPLOAD_MB} MB.",
                    )
                out_file.write(data)
    except HTTPException:
        raise
    except Exception as exc:
        if os.path.exists(save_path):
            os.remove(save_path)
        logger.error("Failed to save uploaded file: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to save file: {exc}")

    # ── Extract text ──────────────────────────────────────────────────────────
    try:
        raw_text, page_count = extract_text_from_pdf(save_path)
    except Exception as exc:
        _cleanup(save_path)
        logger.error("Text extraction failed for %s: %s", safe_name, exc)
        raise HTTPException(status_code=500, detail=f"PDF text extraction failed: {exc}")

    # ── Process and store ─────────────────────────────────────────────────────
    cleaned = clean_text(raw_text)
    chunks = chunk_text(cleaned, chunk_size=500, overlap=50)
    chunks = remove_duplicates(chunks)
    chunks = merge_short_chunks(chunks)

    if not chunks:
        _cleanup(save_path)
        raise HTTPException(
            status_code=422,
            detail=(
                "No text could be extracted from this PDF. "
                "If it is a scanned document, ensure Tesseract OCR is installed."
            ),
        )

    try:
        stored_chunks = store_document(
            document_id=document_id,
            filename=file.filename or safe_name,
            chunks=chunks,
        )
    except Exception as exc:
        _cleanup(save_path)
        logger.error("ChromaDB storage failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Database storage failed: {exc}")

    logger.info(
        "Uploaded '%s': %d pages, %d chunks stored (doc_id=%s)",
        safe_name, page_count, stored_chunks, document_id,
    )

    return UploadResponse(
        message="PDF uploaded and processed successfully",
        document_id=document_id,
        filename=file.filename or safe_name,
        chunks=stored_chunks,
        pages=page_count,
    )


def _cleanup(path: str) -> None:
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
