import { useState } from "react";
import axios from "axios";
import SearchBar from "./SearchBar";
import ResultCard from "./ResultCard";
import Stats from "./Stats";

const API = "http://localhost:8000";

export default function App() {
  const [query, setQuery]       = useState("");
  const [language, setLanguage] = useState("");
  const [results, setResults]   = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const [latency, setLatency]   = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const params = { q: query, top_k: 10 };
      if (language) params.language = language;
      const { data } = await axios.get(`${API}/search`, { params });
      setResults(data.results);
      setLatency(data.latency_ms);
    } catch (e) {
      setError("Search failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSearch();
  };

  return (
    <div style={styles.app}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>🔍 Semantic Code Search</h1>
        <p style={styles.subtitle}>
          Search 50K+ code snippets with natural language · Powered by CodeBERT + FAISS
        </p>
      </div>

      {/* Search area */}
      <div style={styles.searchSection}>
        <SearchBar
          query={query}
          setQuery={setQuery}
          language={language}
          setLanguage={setLanguage}
          onSearch={handleSearch}
          onKeyDown={handleKeyDown}
          loading={loading}
        />
      </div>

      {/* Stats bar */}
      <Stats api={API} />

      {/* Latency badge */}
      {latency !== null && (
        <p style={styles.latency}>
          ⚡ Retrieved in <strong>{latency} ms</strong>
          {latency < 50 ? " ✅" : ""}
        </p>
      )}

      {/* Error */}
      {error && <p style={styles.error}>{error}</p>}

      {/* Loading */}
      {loading && <p style={styles.loading}>Searching...</p>}

      {/* Results */}
      {results && !loading && (
        <div style={styles.results}>
          <p style={styles.resultCount}>
            {results.length} result{results.length !== 1 ? "s" : ""}
          </p>
          {results.map((r, i) => (
            <ResultCard key={r.id} result={r} rank={i + 1} />
          ))}
          {results.length === 0 && (
            <p style={styles.noResults}>No results found. Try a different query.</p>
          )}
        </div>
      )}
    </div>
  );
}

const styles = {
  app: {
    maxWidth: 900, margin: "0 auto", padding: "24px 16px",
    fontFamily: "'Segoe UI', system-ui, sans-serif", color: "#1e2533",
  },
  header: { textAlign: "center", marginBottom: 32 },
  title: { fontSize: 32, fontWeight: 800, color: "#1a56db", margin: 0 },
  subtitle: { color: "#6b7280", fontSize: 15, marginTop: 8 },
  searchSection: { marginBottom: 16 },
  latency: { color: "#4b5563", fontSize: 13, textAlign: "center", margin: "8px 0" },
  error: { color: "#dc2626", textAlign: "center" },
  loading: { textAlign: "center", color: "#6b7280" },
  results: { marginTop: 24 },
  resultCount: { color: "#6b7280", fontSize: 13, marginBottom: 12 },
  noResults: { color: "#6b7280", textAlign: "center", padding: 40 },
};