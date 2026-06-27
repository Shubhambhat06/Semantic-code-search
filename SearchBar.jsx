export default function SearchBar({
  query, setQuery, language, setLanguage,
  onSearch, onKeyDown, loading
}) {
  return (
    <div style={styles.container}>
      <div style={styles.row}>
        <input
          style={styles.input}
          type="text"
          placeholder='e.g. "sort a list of integers", "connect to a database", "parse JSON"'
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={onKeyDown}
        />
        <select
          style={styles.select}
          value={language}
          onChange={e => setLanguage(e.target.value)}
        >
          <option value="">All languages</option>
          <option value="python">Python</option>
          <option value="java">Java</option>
          <option value="cpp">Go / C++</option>
        </select>
        <button
          style={{ ...styles.button, opacity: loading ? 0.6 : 1 }}
          onClick={onSearch}
          disabled={loading}
        >
          {loading ? "..." : "Search"}
        </button>
      </div>
      <div style={styles.suggestions}>
        {["sort a list", "read file line by line", "connect to database",
          "parse JSON", "binary search", "HTTP GET request"].map(s => (
          <button key={s} style={styles.chip}
            onClick={() => { setQuery(s); }}>
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}

const styles = {
  container: { width: "100%" },
  row: { display: "flex", gap: 8 },
  input: {
    flex: 1, padding: "12px 16px", fontSize: 15,
    border: "2px solid #e5e7eb", borderRadius: 8, outline: "none",
  },
  select: {
    padding: "12px 10px", fontSize: 14,
    border: "2px solid #e5e7eb", borderRadius: 8,
    background: "white", cursor: "pointer",
  },
  button: {
    padding: "12px 24px", background: "#1a56db", color: "white",
    border: "none", borderRadius: 8, fontSize: 15,
    fontWeight: 600, cursor: "pointer",
  },
  suggestions: { display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10 },
  chip: {
    padding: "4px 12px", background: "#eef3fc", color: "#1a56db",
    border: "1px solid #bfdbfe", borderRadius: 20, fontSize: 13,
    cursor: "pointer",
  },
};