"""
FastAPI application entry point.

Startup order:
1. CORS middleware (must be first)
2. API routers (all prefixed /api)
3. Static frontend serving (production only)
4. Health + root endpoints
"""

import logging
import os
from contextlib import asynccontextmanager

from api.ask import router as ask_router
from api.auth import router as auth_router
from api.documents import router as documents_router
from api.flashcards import router as flashcards_router
from api.quiz import router as quiz_router
from api.studyplan import router as studyplan_router
from api.summary import router as summary_router
from api.upload import router as upload_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm up the embedding model on startup so the first request is fast."""
    logger.info("🚀 AI Learning Assistant starting up...")
    try:
        from services.embedding_service import get_model
        get_model()
        logger.info("✅ Embedding model loaded and ready")
    except Exception as exc:
        logger.warning("⚠️  Could not pre-load embedding model: %s", exc)
    yield
    logger.info("🛑 AI Learning Assistant shutting down")


app = FastAPI(
    title="AI Learning Assistant",
    description=(
        "A production-quality RAG-powered study platform. "
        "Upload PDFs and instantly generate flashcards, quizzes, summaries, "
        "and AI-powered answers grounded in your study materials."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Read allowed origins from the environment (comma-separated).
# In development the frontend runs on localhost:5173.
# In production on HuggingFace Spaces, the backend serves the frontend directly,
# so no cross-origin requests occur.
_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
)
allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# ── API Routers ───────────────────────────────────────────────────────────────
app.include_router(auth_router,      prefix="/api", tags=["Authentication"])
app.include_router(upload_router,    prefix="/api", tags=["Documents"])
app.include_router(documents_router, prefix="/api", tags=["Documents"])
app.include_router(ask_router,       prefix="/api", tags=["Chat / Ask"])
app.include_router(quiz_router,      prefix="/api", tags=["Quiz"])
app.include_router(flashcards_router,prefix="/api", tags=["Flashcards"])
app.include_router(summary_router,   prefix="/api", tags=["Summary"])
app.include_router(studyplan_router, prefix="/api", tags=["Study Plan"])


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"], summary="Health check")
def health():
    """Returns 200 OK when the service is running. Used by deployment platforms."""
    return {"status": "ok", "version": "2.0.0"}


# ── Static Frontend (production) ──────────────────────────────────────────────
# In Docker / HuggingFace Spaces the React build is copied to frontend/dist.
# The backend serves it directly so no separate frontend server is needed.
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.isdir(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        # Let FastAPI handle API, docs, and openapi routes normally.
        # This catch-all only handles unknown paths → SPA fallback.
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

else:
    @app.get("/", tags=["System"], summary="Root")
    def root():
        return JSONResponse({
            "message": "AI Learning Assistant v2.0 — API only mode",
            "docs": "/docs",
            "health": "/health",
            "status": "running",
        })
