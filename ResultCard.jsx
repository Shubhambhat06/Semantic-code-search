import { useState } from "react";

const LANG_COLORS = {
  python: { bg: "#fef9c3", text: "#854d0e", border: "#fde047" },
  java:   { bg: "#fee2e2", text: "#991b1b", border: "#fca5a5" },
  cpp:    { bg: "#dcfce7", text: "#166534", border: "#86efac" },
};

export default function ResultCard({ result, rank }) {
  const [expanded, setExpanded] = useState(false);
  const lang   = result.language;
  const colors = LANG_COLORS[lang] || { bg: "#f3f4f6", text: "#374151", border: "#d1d5db" };
  const score  = (result.score * 100).toFixed(1);

  return (
    <div style={styles.card}>
      {/* Header row */}
      <div style={styles.header}>
        <div style={styles.left}>
          <span style={styles.rank}>#{rank}</span>
          <span style={{ ...styles.langBadge,
            background: colors.bg, color: colors.text,
            border: `1px solid ${colors.border}` }}>
            {lang}
          </span>
          <span style={styles.funcName}>
            {result.func_name || "anonymous"}
          </span>
        </div>
        <div style={styles.right}>
          <span style={styles.score}>
            {score}% match
          </span>
          <div style={styles.scoreBar}>
            <div style={{
              ...styles.scoreBarFill,
              width: `${Math.min(score, 100)}%`,
              background: score > 70 ? "#22c55e" : score > 40 ? "#f59e0b" : "#ef4444"
            }} />
          </div>
        </div>
      </div>

      {/* Docstring */}
      {result.docstring && (
        <p style={styles.docstring}>{result.docstring}</p>
      )}

      {/* Code preview */}
      <div style={styles.codeWrapper}>
        <pre style={styles.code}>
          {expanded
            ? result.code_preview
            : result.code_preview.slice(0, 300) + (result.code_preview.length > 300 ? "..." : "")
          }
        </pre>
        {result.code_preview.length > 300 && (
          <button style={styles.expandBtn}
            onClick={() => setExpanded(!expanded)}>
            {expanded ? "Show less ▲" : "Show more ▼"}
          </button>
        )}
      </div>

      {/* Footer */}
      {result.url && (
        <div style={styles.footer}>
          <a href={result.url} target="_blank" rel="noreferrer"
             style={styles.link}>
            View on GitHub →
          </a>
        </div>
      )}
    </div>
  );
}

const styles = {
  card: {
    border: "1px solid #e5e7eb", borderRadius: 10, padding: 16,
    marginBottom: 12, background: "white",
    boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
  },
  header: { display: "flex", justifyContent: "space-between",
    alignItems: "center", marginBottom: 8 },
  left: { display: "flex", alignItems: "center", gap: 8 },
  right: { display: "flex", alignItems: "center", gap: 8 },
  rank: { color: "#9ca3af", fontSize: 13, fontWeight: 600 },
  langBadge: {
    fontSize: 12, fontWeight: 700, padding: "2px 8px",
    borderRadius: 20,
  },
  funcName: { fontWeight: 600, fontSize: 14, color: "#1a56db" },
  score: { fontSize: 13, fontWeight: 600, color: "#374151" },
  scoreBar: {
    width: 80, height: 6, background: "#e5e7eb",
    borderRadius: 3, overflow: "hidden",
  },
  scoreBarFill: { height: "100%", borderRadius: 3, transition: "width 0.3s" },
  docstring: {
    color: "#4b5563", fontSize: 13, margin: "6px 0 10px",
    fontStyle: "italic", lineHeight: 1.5,
  },
  codeWrapper: { position: "relative" },
  code: {
    background: "#f8fafc", border: "1px solid #e5e7eb",
    borderRadius: 6, padding: "10px 12px", fontSize: 12,
    overflowX: "auto", margin: 0, color: "#1e2533",
    fontFamily: "'Consolas', 'Fira Code', monospace",
    whiteSpace: "pre-wrap", wordBreak: "break-word",
  },
  expandBtn: {
    background: "none", border: "none", color: "#1a56db",
    cursor: "pointer", fontSize: 12, padding: "4px 0",
  },
  footer: { marginTop: 8 },
  link: { color: "#6b7280", fontSize: 12, textDecoration: "none" },
};