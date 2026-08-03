import { useState, useRef, useEffect, useCallback } from "react";
import { api } from "../utils/api";

/**
 * Lightweight Markdown renderer — no external dependencies.
 * Handles: **bold**, *italic*, `inline code`, ```code blocks```,
 * bullet lists (- or *), numbered lists, and headings (#, ##, ###).
 */
function renderMarkdown(text) {
  if (!text) return [];

  const lines = text.split("\n");
  const elements = [];
  let i = 0;
  let keyCounter = 0;
  const key = () => `md-${keyCounter++}`;

  while (i < lines.length) {
    const line = lines[i];

    // Fenced code block
    if (line.trimStart().startsWith("```")) {
      const codeLines = [];
      i++;
      while (i < lines.length && !lines[i].trimStart().startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      elements.push(
        <pre key={key()} className="md-code-block">
          <code>{codeLines.join("\n")}</code>
        </pre>
      );
      i++;
      continue;
    }

    // Headings
    const h3 = line.match(/^### (.+)/);
    const h2 = line.match(/^## (.+)/);
    const h1 = line.match(/^# (.+)/);
    if (h1) { elements.push(<h3 key={key()} className="md-h1">{inlineFormat(h1[1])}</h3>); i++; continue; }
    if (h2) { elements.push(<h4 key={key()} className="md-h2">{inlineFormat(h2[1])}</h4>); i++; continue; }
    if (h3) { elements.push(<h5 key={key()} className="md-h3">{inlineFormat(h3[1])}</h5>); i++; continue; }

    // Bullet list group
    if (/^(\s*[-*+]\s)/.test(line)) {
      const items = [];
      while (i < lines.length && /^(\s*[-*+]\s)/.test(lines[i])) {
        items.push(<li key={key()}>{inlineFormat(lines[i].replace(/^\s*[-*+]\s/, ""))}</li>);
        i++;
      }
      elements.push(<ul key={key()} className="md-ul">{items}</ul>);
      continue;
    }

    // Numbered list group
    if (/^\d+\.\s/.test(line)) {
      const items = [];
      while (i < lines.length && /^\d+\.\s/.test(lines[i])) {
        items.push(<li key={key()}>{inlineFormat(lines[i].replace(/^\d+\.\s/, ""))}</li>);
        i++;
      }
      elements.push(<ol key={key()} className="md-ol">{items}</ol>);
      continue;
    }

    // Horizontal rule
    if (/^(-{3,}|\*{3,}|_{3,})$/.test(line.trim())) {
      elements.push(<hr key={key()} className="md-hr" />);
      i++;
      continue;
    }

    // Empty line
    if (!line.trim()) {
      elements.push(<div key={key()} className="md-spacer" />);
      i++;
      continue;
    }

    // Regular paragraph
    elements.push(<p key={key()} className="md-p">{inlineFormat(line)}</p>);
    i++;
  }

  return elements;
}

/** Apply inline formatting: **bold**, *italic*, `code` */
function inlineFormat(text) {
  const parts = [];
  // Split on bold, italic, inline code
  const regex = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  let lastIdx = 0;
  let match;
  let k = 0;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIdx) {
      parts.push(text.slice(lastIdx, match.index));
    }
    const token = match[0];
    if (token.startsWith("**")) {
      parts.push(<strong key={k++}>{token.slice(2, -2)}</strong>);
    } else if (token.startsWith("*")) {
      parts.push(<em key={k++}>{token.slice(1, -1)}</em>);
    } else if (token.startsWith("`")) {
      parts.push(<code key={k++} className="md-inline-code">{token.slice(1, -1)}</code>);
    }
    lastIdx = match.index + token.length;
  }
  if (lastIdx < text.length) {
    parts.push(text.slice(lastIdx));
  }
  return parts.length === 1 && typeof parts[0] === "string" ? parts[0] : parts;
}

function Message({ msg }) {
  const [showSources, setShowSources] = useState(false);
  const isUser = msg.role === "user";

  return (
    <div className={`message ${isUser ? "user" : "ai"}`}>
      <div className="msg-avatar">{isUser ? "👤" : "🤖"}</div>
      <div className="msg-content-wrapper">
        <div className="msg-bubble">
          {msg.loading ? (
            <div className="typing-dots">
              <span /><span /><span />
            </div>
          ) : (
            <div className="markdown-content">
              {isUser ? msg.content : renderMarkdown(msg.content)}
            </div>
          )}
        </div>

        {!isUser && msg.sources && msg.sources.length > 0 && !msg.loading && (
          <>
            <button
              className="sources-toggle"
              onClick={() => setShowSources((s) => !s)}
            >
              📚 {msg.sources.length} source{msg.sources.length > 1 ? "s" : ""} cited {showSources ? "▲" : "▼"}
            </button>
            {showSources && (
              <div className="sources-list">
                {msg.sources.map((s, i) => (
                  <div key={i} className="source-chip">
                    <span className="source-chip-meta">
                      <strong>{s.filename}</strong> · Page {s.page} · {(s.similarity * 100).toFixed(0)}% match
                    </span>
                    <div className="source-chip-preview">{s.preview}</div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {!isUser && msg.model_used && !msg.loading && (
          <div className="msg-model-tag">via {msg.model_used}</div>
        )}
      </div>
    </div>
  );
}

export default function ChatPage({ doc, hasDocs, messages, setMessages }) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [directSearch, setDirectSearch] = useState(false);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 180)}px`;
  }, [input]);

  const send = useCallback(async () => {
    const q = input.trim();
    if (!q || loading) return;

    setInput("");
    setMessages((m) => [
      ...m,
      { role: "user", content: q },
      { role: "ai", content: "", loading: true },
    ]);
    setLoading(true);

    try {
      const res = await api.askQuestion(q, doc?.document_id, 5, directSearch);
      setMessages((m) => {
        const updated = [...m];
        updated[updated.length - 1] = {
          role: "ai",
          content: res.answer,
          sources: res.sources,
          model_used: res.model_used,
          loading: false,
        };
        return updated;
      });
    } catch (e) {
      setMessages((m) => {
        const updated = [...m];
        updated[updated.length - 1] = {
          role: "ai",
          content: `**Error:** ${e.message || "Failed to communicate with server."}`,
          loading: false,
        };
        return updated;
      });
    } finally {
      setLoading(false);
    }
  }, [input, loading, doc, directSearch, setMessages]);

  const focusText = doc
    ? `Focused on: ${doc.filename}`
    : hasDocs
    ? "Searching all uploaded materials"
    : "Upload a document to get started";

  const placeholder = hasDocs
    ? doc
      ? `Ask a question about "${doc.filename}"...`
      : "Ask a question across all study materials..."
    : "Upload a PDF first to start asking questions...";

  return (
    <div className="chat-container">
      <div className="page-header">
        <div className="page-header-info">
          <h2>Ask Questions</h2>
          <p>Get answers with direct page references</p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          {hasDocs && (
            <label
              className="direct-search-toggle"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                fontSize: 12,
                color: "var(--text-secondary)",
                cursor: "pointer",
                fontWeight: 600,
                background: "rgba(255,255,255,0.03)",
                padding: "6px 12px",
                borderRadius: "var(--radius-pill)",
                border: "1px solid var(--border-color)",
              }}
            >
              <input
                type="checkbox"
                checked={directSearch}
                onChange={(e) => setDirectSearch(e.target.checked)}
                style={{ accentColor: "var(--accent)", cursor: "pointer" }}
              />
              ⚡ Fast Mode
            </label>
          )}
          <div
            className={`focus-badge ${
              doc ? "focus-doc" : hasDocs ? "focus-all" : "focus-none"
            }`}
          >
            <span className="dot" />
            <span className="focus-label">{focusText}</span>
          </div>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty-state">
            <div className="chat-empty-icon">🤖</div>
            <h3>Ready to help you study</h3>
            <p>Upload a PDF and ask me anything about it.</p>
          </div>
        )}
        {messages.map((m, i) => (
          <Message key={i} msg={m} />
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-area">
        <div className="chat-input-row">
          <textarea
            ref={textareaRef}
            rows={1}
            placeholder={placeholder}
            value={input}
            disabled={!hasDocs || loading}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
          />
          <button
            className="send-btn"
            onClick={send}
            disabled={!hasDocs || loading || !input.trim()}
            title="Send (Enter)"
          >
            {loading ? (
              <div className="spinner" style={{ width: 14, height: 14 }} />
            ) : (
              "➤"
            )}
          </button>
        </div>
        <div className="chat-input-hint">
          Press Enter to send · Shift+Enter for new line
          {directSearch && " · ⚡ Fast Mode: direct retrieval (no AI synthesis)"}
        </div>
      </div>
    </div>
  );
}
