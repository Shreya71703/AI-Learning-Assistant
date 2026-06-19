from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.upload import router as upload_router
from api.ask import router as ask_router
from api.documents import router as documents_router
from api.quiz import router as quiz_router
from api.flashcards import router as flashcards_router
from api.summary import router as summary_router
from api.studyplan import router as studyplan_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm all expensive resources at startup so first request is instant."""
    import asyncio
    import concurrent.futures

    def _warm():
        try:
            # Pre-load embedding model into memory
            from services.embedding_service import get_model
            model = get_model()
            # Run a dummy encode so the model is fully JIT-compiled and cached
            model.encode(["warmup"], show_progress_bar=False)
            print("[startup] OK: Embedding model pre-loaded")
        except Exception as e:
            print(f"[startup] WARN: Embedding warmup failed: {e}")

        try:
            # Pre-open ChromaDB collection
            from database.chroma import get_collection
            get_collection()
            print("[startup] OK: ChromaDB collection pre-loaded")
        except Exception as e:
            print(f"[startup] WARN: ChromaDB warmup failed: {e}")

    # Run warmup in a thread so it doesn't block the event loop
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, _warm)

    yield  # Application runs here


app = FastAPI(
    title="AI Learning Assistant",
    description="Production-ready AI learning platform",
    version="2.0.0",
    lifespan=lifespan
)

# Allow React app (and potential local environments) to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(ask_router, prefix="/api", tags=["ask"])
app.include_router(documents_router, prefix="/api", tags=["documents"])
app.include_router(quiz_router, prefix="/api", tags=["quiz"])
app.include_router(flashcards_router, prefix="/api", tags=["flashcards"])
app.include_router(summary_router, prefix="/api", tags=["summary"])
app.include_router(studyplan_router, prefix="/api", tags=["studyplan"])


@app.get("/")
def root():
    return {
        "message": "AI Learning Assistant v2.0 Running",
        "docs": "/docs",
        "status": "healthy"
    }


@app.get("/health")
def health():
    return {"status": "ok"}

