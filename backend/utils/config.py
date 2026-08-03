"""
Central configuration module.

All environment-sensitive values are read from environment variables with
sensible cross-platform defaults. This file is the single source of truth —
no other module should call os.getenv() directly.
"""

import os
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
CHROMA_DIR = BASE_DIR / "chroma_db"
UPLOAD_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)

# ── OCR / PDF ─────────────────────────────────────────────────────────────────
# On Linux (Docker), tesseract is on PATH so no explicit path is needed.
# On Windows local dev, set TESSERACT_PATH in your .env file.
TESSERACT_PATH = os.getenv(
    "TESSERACT_PATH",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe" if os.name == "nt" else "",
)
POPPLER_PATH = os.getenv(
    "POPPLER_PATH",
    r"C:\poppler\poppler-26.02.0\Library\bin" if os.name == "nt" else "",
)

# ── Upload Limits ─────────────────────────────────────────────────────────────
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "25"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

# ── Embeddings ────────────────────────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# ── ChromaDB ──────────────────────────────────────────────────────────────────
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "documents")

# ── LLM ───────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── Auth ──────────────────────────────────────────────────────────────────────
_jwt_secret = os.getenv("JWT_SECRET", "")
if not _jwt_secret:
    import warnings
    warnings.warn(
        "JWT_SECRET environment variable is not set. "
        "Using an insecure default — set this in production!",
        stacklevel=2,
    )
    _jwt_secret = "ai-learning-assistant-dev-only-secret-change-me"
JWT_SECRET = _jwt_secret

# ── RAG ───────────────────────────────────────────────────────────────────────
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

# ── CORS ──────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
)
