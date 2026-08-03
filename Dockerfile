# ── Stage 1: Build the React frontend ─────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --prefer-offline
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Production Python backend ────────────────────────────────────────
FROM python:3.11-slim

# System dependencies for OCR and PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Create a globally writable HuggingFace cache directory
RUN mkdir -p /app/hf_cache && chmod 777 /app/hf_cache
ENV HF_HOME=/app/hf_cache
ENV SENTENCE_TRANSFORMERS_HOME=/app/hf_cache

# Pre-download the sentence-transformers model at build time so startup is instant
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Ensure cached files are readable by the runtime user
RUN chmod -R 755 /app/hf_cache

# Copy backend source code
COPY backend/ ./backend/

# Copy the built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create writable runtime directories
RUN mkdir -p /app/backend/chroma_db /app/backend/uploads \
    && chmod 777 /app/backend/chroma_db /app/backend/uploads

# Set offline mode — use only the pre-downloaded model, never call network at runtime
ENV TRANSFORMERS_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1

# HuggingFace Spaces uses port 7860
EXPOSE 7860

WORKDIR /app/backend

# Run with a single worker (ChromaDB is not multi-process safe with shared state)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
