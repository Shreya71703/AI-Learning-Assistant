import { useState } from "react";
import { api } from "../utils/api";

function Flashcard({ card }) {
  const [flipped, setFlipped] = useState(false);
  return (
    <div 
      className={`flashcard ${flipped ? "flipped" : ""}`} 
      onClick={() => setFlipped(!flipped)}
    >
      <div className="flashcard-inner">
        <div className="flashcard-front">
          <div className="flashcard-label">Question</div>
          <div className="flashcard-text">{card.front}</div>
          <div className="flashcard-topic">{card.topic}</div>
          <div className="flashcard-flip-hint">Tap to reveal answer 🔄</div>
        </div>
        <div className="flashcard-back">
          <div className="flashcard-label">Answer</div>
          <div className="flashcard-text">{card.back}</div>
          <div className="flashcard-topic">{card.topic}</div>
          <div className="flashcard-flip-hint">Tap to see question 🔄</div>
        </div>
      </div>
    </div>
  );
}

export default function FlashcardsPage({ doc, hasDocs }) {
  const [numCards, setNumCards] = useState(10);
  const [cards, setCards] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function generate() {
    setLoading(true); 
    setError(""); 
    setCards(null);
    try {
      const res = await api.generateFlashcards(numCards, doc?.document_id);
      setCards(res);
    } catch (e) { 
      setError(e.message || "Failed to generate flashcards."); 
    } finally { 
      setLoading(false); 
    }
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-header-info">
          <h2>Flashcards</h2>
          <p>Generate interactive study cards and flip to test your recall</p>
        </div>
        {hasDocs && (
          <div className={`focus-badge ${doc ? "focus-doc" : "focus-all"}`}>
            <span className="dot"></span>
            <span className="focus-label">
              Focus: {doc ? doc.filename : "All files"}
            </span>
          </div>
        )}
      </div>

      <div className="page-content">
        {!hasDocs && (
          <div className="error-box">
            Please upload a PDF document in the sidebar to generate flashcards.
          </div>
        )}

        {hasDocs && (
          <div className="card">
            <div className="card-header">
              <span className="card-title">⚙️ Settings</span>
            </div>
            <div className="form-group" style={{ marginBottom: 16 }}>
              <label className="form-label">Number of flashcards</label>
              <select 
                className="form-select" 
                style={{ maxWidth: 200 }} 
                value={numCards} 
                onChange={(e) => setNumCards(+e.target.value)}
              >
                {[5, 10, 15, 20].map((n) => <option key={n} value={n}>{n} cards</option>)}
              </select>
            </div>
            <button className="btn btn-primary" onClick={generate} disabled={loading}>
              {loading ? (
                <>
                  <div className="spinner" style={{ marginRight: 6 }} /> Generating...
                </>
              ) : (
                "🃏 Generate Flashcards"
              )}
            </button>
          </div>
        )}

        {error && <div className="error-box">{error}</div>}

        {cards && (
          <>
            <div style={{ marginBottom: 16, fontSize: 13, color: "var(--text2)", fontWeight: 500 }}>
              {cards.total} Flashcards generated · click on any card to flip it
            </div>
            <div className="flashcard-grid">
              {cards.flashcards.map((c, i) => <Flashcard key={i} card={c} />)}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
