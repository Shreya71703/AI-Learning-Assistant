import { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import ChatPage from "./pages/ChatPage";
import QuizPage from "./pages/QuizPage";
import FlashcardsPage from "./pages/FlashcardsPage";
import SummaryPage from "./pages/SummaryPage";
import StudyPlanPage from "./pages/StudyPlanPage";
import UploadBanner from "./components/UploadBanner";
import { api } from "./utils/api";
import "./styles/global.css";

export default function App() {
  const [activePage, setActivePage] = useState("chat");
  const [uploadedDoc, setUploadedDoc] = useState(null); // Selected document
  const [documents, setDocuments] = useState([]);      // Available documents
  const [chatHistory, setChatHistory] = useState([
    { role: "ai", content: "Hello! Upload a PDF or select an existing document in the library. You can ask me questions, create study plans, generate quizzes, and summarize topics. 📚" }
  ]);

  // Load documents on mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  async function fetchDocuments() {
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
    } catch (e) {
      console.error("Failed to load documents", e);
    }
  }

  async function handleDeleteDocument(docId) {
    try {
      await api.deleteDocument(docId);
      if (uploadedDoc && uploadedDoc.document_id === docId) {
        setUploadedDoc(null);
      }
      fetchDocuments();
    } catch (e) {
      alert(`Failed to delete document: ${e.message}`);
    }
  }

  const pages = {
    chat: (
      <ChatPage
        doc={uploadedDoc}
        hasDocs={documents.length > 0}
        messages={chatHistory}
        setMessages={setChatHistory}
      />
    ),
    quiz: <QuizPage doc={uploadedDoc} hasDocs={documents.length > 0} />,
    flashcards: <FlashcardsPage doc={uploadedDoc} hasDocs={documents.length > 0} />,
    summary: <SummaryPage doc={uploadedDoc} hasDocs={documents.length > 0} />,
    studyplan: <StudyPlanPage />,
  };

  return (
    <div className="app-shell">
      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
        uploadedDoc={uploadedDoc}
        onSelectDoc={setUploadedDoc}
        documents={documents}
        onRefreshDocs={fetchDocuments}
        onDeleteDoc={handleDeleteDocument}
      />
      <main className="main-area">
        {!uploadedDoc && documents.length === 0 && activePage !== "studyplan" && (
          <UploadBanner />
        )}
        {pages[activePage]}
      </main>
    </div>
  );
}
