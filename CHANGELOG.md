# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] — 2024-08-04

### 🚀 Added
- **Gemini 1.5 Flash integration**: The `/ask` endpoint now synthesizes grounded, coherent answers using Google Gemini with RAG context — with graceful fallback to direct retrieval when no API key is configured
- **Extractive summarization**: `/summary` now uses TF-weighted sentence scoring instead of raw text truncation
- **File size enforcement**: Upload endpoint now enforces a configurable max file size (default 25 MB) via streaming read
- **MIME type validation**: Upload endpoint validates both file extension and Content-Type header
- **Filename sanitization**: Path traversal prevention on uploaded filenames
- **Startup model warmup**: Embedding model is pre-loaded on startup to eliminate first-request latency
- **Structured logging**: Backend now uses Python's `logging` module with timestamps and levels
- **`LICENSE`** file (MIT)
- **`CONTRIBUTING.md`** — full contributor guide
- **`SECURITY.md`** — vulnerability reporting process and security considerations
- **`CHANGELOG.md`** (this file)
- **`CODE_OF_CONDUCT.md`** — Contributor Covenant
- **`.github/ISSUE_TEMPLATE/bug_report.md`**
- **`.github/ISSUE_TEMPLATE/feature_request.md`**
- **`.github/PULL_REQUEST_TEMPLATE.md`**
- **`.github/workflows/ci.yml`** — GitHub Actions CI (lint + build)
- **`backend/.env.example`** — documented environment variable template
- **Markdown rendering in chat** — bold, italic, bullet lists, and code blocks are now rendered properly
- **Case-insensitive username matching** in authentication

### 🔧 Fixed
- **CORS wildcard bug**: `allow_origins=["*"]` with `allow_credentials=True` is blocked by browsers — replaced with explicit origin list from env var
- **Route ordering bug**: Catch-all `/{full_path:path}` was registered before specific routes, causing the root endpoint to be unreachable
- **Hardcoded JWT secret**: Now reads from `JWT_SECRET` env var with a warning in dev mode
- **Windows-only OCR paths** in config: replaced with cross-platform env-var overrides
- **Hardcoded fallback quiz questions**: Removed "Option A / Option B" garbage — now returns a proper error when content is insufficient
- **Deprecated `datetime.utcnow()`**: Replaced with timezone-aware `datetime.now(timezone.utc)`
- **Broken emoji rendering** in frontend source (garbled UTF-8 from encoding issues)
- **`users.json`** added to `.gitignore` (was previously committed)
- **`backend/uploads/`** added to `.gitignore`
- **Dockerfile** separated from `README.md` (was incorrectly concatenated)

### ⚡ Improved
- **Quiz question quality**: Added stop-word filter for candidate answers, better distractor generation
- **Upload error messages**: More informative errors for each failure mode
- **OpenAPI metadata**: Improved endpoint descriptions for `/docs`
- **`README.md`**: Professional rewrite with architecture diagram, API table, setup instructions

### 🔒 Security
- JWT secret now requires explicit env var
- File uploads: size limit, MIME validation, filename sanitization
- CORS: explicit origin list, no wildcard credentials

---

## [1.0.0] — 2024-06-19

### Added
- Initial release: PDF upload, semantic search Q&A, flashcards, quiz, summary, study plan
- ChromaDB vector storage with `all-MiniLM-L6-v2` embeddings
- React frontend with Vite
- JWT authentication with bcrypt password hashing
- Docker + HuggingFace Spaces deployment
- OCR fallback via pytesseract for scanned PDFs
