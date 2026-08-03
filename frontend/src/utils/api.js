/**
 * API client for AI Learning Assistant.
 *
 * BASE_URL resolution:
 * - In Docker/HuggingFace production: frontend is served by the backend,
 *   so relative "/api" works perfectly.
 * - In local dev (npm run dev): Vite proxies "/api" → backend port 8001
 *   OR use VITE_API_URL env var to point to a different backend.
 */
const BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : "/api";

function getAuthHeaders() {
  const token = localStorage.getItem("ai_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Generic JSON request with auth headers.
 * @param {string} endpoint - Path relative to BASE_URL (e.g. "/ask")
 * @param {RequestInit} options - fetch options
 * @returns {Promise<any>}
 */
async function request(endpoint, options = {}) {
  const isFormData = options.body instanceof FormData;
  const headers = {
    ...(!isFormData && { "Content-Type": "application/json" }),
    ...getAuthHeaders(),
    ...options.headers,
  };

  let res;
  try {
    res = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers });
  } catch (networkErr) {
    throw new Error(
      "Cannot reach the server. Make sure the backend is running."
    );
  }

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || body.message || detail;
    } catch {
      // Response body was not JSON
    }
    const err = new Error(detail);
    err.status = res.status;
    throw err;
  }

  return res.json();
}

export const api = {
  // ── Documents ────────────────────────────────────────────────────────────
  uploadPDF: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/upload", { method: "POST", body: form });
  },

  getDocuments: () => request("/documents"),

  deleteDocument: (documentId) =>
    request(`/documents/${documentId}`, { method: "DELETE" }),

  // ── Chat / Ask ───────────────────────────────────────────────────────────
  askQuestion: (question, documentId, topK = 5, directRetrieval = false) =>
    request("/ask", {
      method: "POST",
      body: JSON.stringify({
        question,
        document_id: documentId || null,
        top_k: topK,
        direct_retrieval: directRetrieval,
      }),
    }),

  // ── Study Tools ──────────────────────────────────────────────────────────
  generateQuiz: (numQuestions = 5, difficulty = "medium", documentId) =>
    request("/generate-quiz", {
      method: "POST",
      body: JSON.stringify({
        num_questions: numQuestions,
        difficulty,
        document_id: documentId || null,
      }),
    }),

  generateFlashcards: (numCards = 10, documentId) =>
    request("/flashcards", {
      method: "POST",
      body: JSON.stringify({
        num_cards: numCards,
        document_id: documentId || null,
      }),
    }),

  generateSummary: (length = "medium", documentId) =>
    request("/summary", {
      method: "POST",
      body: JSON.stringify({
        length,
        document_id: documentId || null,
      }),
    }),

  createStudyPlan: (examDate, hoursPerDay, subjects, difficultyLevel) =>
    request("/study-plan", {
      method: "POST",
      body: JSON.stringify({
        exam_date: examDate,
        hours_per_day: hoursPerDay,
        subjects,
        difficulty_level: difficultyLevel,
      }),
    }),

  // ── Auth ─────────────────────────────────────────────────────────────────
  register: (username, password) =>
    request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),

  login: (username, password) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),

  me: () => request("/auth/me"),
};
