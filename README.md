# 🎓 AI Learning Assistant

An AI-powered study tool that lets you upload PDFs and instantly generate flashcards, quizzes, summaries, and personalized study plans — all with **sub-second response times**.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20DB-orange)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **PDF Upload** | Upload any PDF — text extracted instantly via `pypdf` |
| 💬 **Chat / Ask** | Ask questions about your document — semantic search returns relevant passages |
| 🃏 **Flashcards** | Auto-generate flip cards from key concepts in your PDF |
| 📝 **Quiz** | MCQ quiz generated from your study material |
| 📋 **Summary** | Get a short, medium, or long summary of your document |
| 📅 **Study Plan** | Input your exam date and get a day-by-day study schedule |

---

## ⚡ Performance

All API responses return in **under 200ms** — no LLM wait times.

| Endpoint | Response Time |
|----------|-------------|
| Flashcards | ~174ms |
| Quiz | ~34ms |
| Summary | ~30ms |
| Study Plan | ~9ms |

---

## 🏗️ Tech Stack

- **Backend:** FastAPI + Python
- **Vector DB:** ChromaDB (local, persistent)
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`
- **PDF Parsing:** `pypdf` (digital PDFs) + `pytesseract` (scanned PDFs fallback)
- **Frontend:** React + Vite

---

## 🚀 Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/AI-Learning-Assistant.git
cd AI-Learning-Assistant
```

### 2. Backend setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Frontend setup
```bash
cd ../frontend
npm install
```

---

## ▶️ Run the App

Open **two terminals**:

**Terminal 1 — Backend:**
```bash
cd backend
venv\Scripts\activate          # Windows
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## 📡 API Reference

Base URL: `http://127.0.0.1:8001/api`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload a PDF file |
| `GET` | `/documents` | List all uploaded documents |
| `DELETE` | `/documents/{id}` | Delete a document |
| `POST` | `/ask` | Ask a question (semantic search) |
| `POST` | `/flashcards` | Generate flashcards |
| `POST` | `/generate-quiz` | Generate MCQ quiz |
| `POST` | `/summary` | Summarize document |
| `POST` | `/study-plan` | Create study schedule |

Interactive docs: **http://127.0.0.1:8001/docs**

---

## 📁 Project Structure

```
AI-Learning-Assistant/
├── backend/
│   ├── api/              # Route handlers
│   │   ├── ask.py
│   │   ├── flashcards.py
│   │   ├── quiz.py
│   │   ├── summary.py
│   │   ├── studyplan.py
│   │   ├── upload.py
│   │   └── documents.py
│   ├── database/
│   │   └── chroma.py     # ChromaDB vector store
│   ├── models/
│   │   └── schemas.py    # Pydantic models
│   ├── rag/
│   │   ├── retriever.py  # Semantic search
│   │   └── prompts.py
│   ├── services/
│   │   ├── embedding_service.py
│   │   └── ocr_service.py
│   ├── utils/
│   └── main.py           # FastAPI app + startup warmup
├── frontend/
│   └── src/
│       ├── pages/        # React pages
│       ├── components/   # Sidebar, UploadBanner
│       ├── utils/api.js  # API client
│       └── styles/
└── README.md
```

---

## 📝 License

MIT
