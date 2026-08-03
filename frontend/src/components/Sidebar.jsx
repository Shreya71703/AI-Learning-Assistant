import { useState, useRef } from "react";
import { api } from "../utils/api";

const NAV_ITEMS = [
  { id: "chat",      icon: "💬", label: "Ask Questions" },
  { id: "summary",   icon: "📄", label: "Summary" },
  { id: "quiz",      icon: "📝", label: "Quiz Generator" },
  { id: "flashcards",icon: "🃏", label: "Flashcards" },
  { id: "studyplan", icon: "📅", label: "Study Planner" },
];

export default function Sidebar({
  activePage,
  onNavigate,
  uploadedDoc,
  onSelectDoc,
  documents,
  onRefreshDocs,
  onDeleteDoc,
  username,
  onLogout,
}) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState("");
  const [error, setError] = useState("");
  const fileRef = useRef();

  async function handleFile(file) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are supported.");
      return;
    }
    const MAX_MB = 25;
    if (file.size > MAX_MB * 1024 * 1024) {
      setError(`File too large. Maximum size is ${MAX_MB} MB.`);
      return;
    }

    setUploading(true);
    setError("");
    setUploadProgress("Extracting text from PDF...");

    try {
      const result = await api.uploadPDF(file);
      setUploadProgress(`✅ ${result.chunks} chunks indexed across ${result.pages} pages`);
      await onRefreshDocs();
      onSelectDoc(result);
      setTimeout(() => setUploadProgress(""), 3000);
    } catch (e) {
      setError(e.message || "Upload failed. Please try again.");
      setUploadProgress("");
    } finally {
      setUploading(false);
      // Reset file input so the same file can be re-uploaded if needed
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  return (
    <aside className="sidebar" aria-label="Application sidebar">
      <div className="sidebar-logo">
        <h1>AI <span>Study Assistant</span></h1>
        <p>Analyze documents, generate quizzes &amp; plans</p>
      </div>

      {/* ── Upload Zone ─────────────────────────────────────────────── */}
      <div className="sidebar-upload">
        <div
          role="button"
          tabIndex={uploading ? -1 : 0}
          aria-label="Upload PDF — click or drag and drop"
          className={`upload-zone ${dragging ? "drag-over" : ""} ${uploading ? "uploading" : ""}`}
          onClick={() => !uploading && fileRef.current.click()}
          onKeyDown={(e) => e.key === "Enter" && !uploading && fileRef.current.click()}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            const f = e.dataTransfer.files[0];
            if (f) handleFile(f);
          }}
        >
          <div className="icon">{uploading ? "⏳" : "📂"}</div>
          <p>
            {uploading
              ? uploadProgress || "Processing..."
              : <><strong>Click or drag &amp; drop</strong><br />any PDF file here</>
            }
          </p>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf"
            aria-hidden="true"
            tabIndex={-1}
            onChange={(e) => handleFile(e.target.files[0])}
          />
        </div>
        {error && (
          <div className="error-box" role="alert" style={{ marginTop: 8, fontSize: 11 }}>
            ⚠️ {error}
          </div>
        )}
      </div>

      {/* ── Document Library ─────────────────────────────────────────── */}
      <div className="sidebar-library">
        <div className="nav-section-label">Study Library</div>
        <div className="library-list" role="list">
          {documents.length > 0 && (
            <button
              role="listitem"
              className={`library-item ${!uploadedDoc ? "active" : ""}`}
              onClick={() => onSelectDoc(null)}
              aria-pressed={!uploadedDoc}
            >
              <span className="library-icon">🔍</span>
              <span className="library-label">Search All Files</span>
            </button>
          )}

          {documents.map((doc) => {
            const isSelected = uploadedDoc && uploadedDoc.document_id === doc.document_id;
            return (
              <div
                key={doc.document_id}
                role="listitem"
                className={`library-item-wrapper ${isSelected ? "selected" : ""}`}
              >
                <button
                  className="library-item-btn"
                  onClick={() => onSelectDoc(doc)}
                  title={doc.filename}
                  aria-pressed={isSelected}
                >
                  <span className="library-icon">📋</span>
                  <span className="library-label">{doc.filename}</span>
                </button>
                <button
                  className="library-delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (window.confirm(`Delete "${doc.filename}"?`)) {
                      onDeleteDoc(doc.document_id);
                    }
                  }}
                  title={`Delete ${doc.filename}`}
                  aria-label={`Delete ${doc.filename}`}
                >
                  🗑️
                </button>
              </div>
            );
          })}

          {documents.length === 0 && (
            <div className="library-empty">
              No documents uploaded yet.
            </div>
          )}
        </div>
      </div>

      {/* ── Navigation ───────────────────────────────────────────────── */}
      <nav className="sidebar-nav" aria-label="Study tools navigation">
        <div className="nav-section-label">Tools</div>
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${activePage === item.id ? "active" : ""}`}
            onClick={() => onNavigate(item.id)}
            aria-current={activePage === item.id ? "page" : undefined}
          >
            <span className="nav-icon" aria-hidden="true">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      {/* ── Footer / User ─────────────────────────────────────────────── */}
      <div className="sidebar-footer">
        {username && (
          <div className="sidebar-user">
            <span className="sidebar-user-avatar" aria-hidden="true">
              {username[0].toUpperCase()}
            </span>
            <span className="sidebar-user-name">{username}</span>
            <button
              id="logout-btn"
              className="sidebar-logout-btn"
              onClick={onLogout}
              title="Sign out"
            >
              Sign out
            </button>
          </div>
        )}
        <div className="sidebar-powered">Powered by ChromaDB · FastAPI · Gemini</div>
      </div>
    </aside>
  );
}
