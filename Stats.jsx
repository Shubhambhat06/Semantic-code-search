import { useEffect, useState } from "react";
import axios from "axios";

export default function Stats({ api }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    axios.get(`${api}/stats`)
      .then(r => setStats(r.data))
      .catch(() => {});
  }, [api]);

  if (!stats) return null;

  return (
    <div style={styles.bar}>
      <span>📦 <strong>{stats.total_snippets?.toLocaleString()}</strong> snippets indexed</span>
      {Object.entries(stats.languages || {}).map(([lang, count]) => (
        <span key={lang}>· {lang}: <strong>{count.toLocaleString()}</strong></span>
      ))}
      <span>· dim: <strong>{stats.embedding_dim}</strong></span>
    </div>
  );
}

const styles = {
  bar: {
    display: "flex", gap: 12, flexWrap: "wrap",
    background: "#f0f4ff", border: "1px solid #bfdbfe",
    borderRadius: 8, padding: "8px 14px",
    fontSize: 13, color: "#374151", marginBottom: 8,
  },
};