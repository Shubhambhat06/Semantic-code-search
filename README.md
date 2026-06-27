# Semantic Code Search Engine

Natural language search over 50K+ code snippets, powered by a fine-tuned CodeBERT bi-encoder and FAISS approximate nearest-neighbour retrieval — served through a FastAPI backend and a React.js frontend.

> Type what you want in plain English — *"read a file line by line"*, *"connect to a database"*, *"binary search"* — and get ranked, scored code matches in milliseconds.

---

## Features

- Natural language to code retrieval using dense embeddings instead of keyword matching
- Fine-tuned CodeBERT bi-encoder trained with an InfoNCE contrastive objective on NL-code pairs
- Sub-50ms retrieval at 50K+ snippet scale via a FAISS `IndexFlatIP` index
- Multi-language support across Python, Java, and Go (CodeSearchNet's available languages)
- Ranked results with similarity scores and inline code previews
- Language filtering, query suggestions, and expandable code cards on the frontend
- REST API with auto-generated Swagger docs (`/docs`)

---

## Architecture

```
CodeSearchNet (50K snippets: Python, Java, Go)
                ↓
   Fine-tuned CodeBERT bi-encoder  →  768-dim dense embeddings
                ↓
        FAISS IndexFlatIP  (cosine similarity, sub-50ms)
                ↓
   FastAPI backend  ←──────────→  React.js frontend
   /search /health /stats          search bar · filters · ranked cards
```

The model is fine-tuned and embeddings are generated on a GPU (Google Colab, free T4 tier); the trained artifacts are then loaded locally for fast CPU inference — encoding a single query takes a few hundred milliseconds, and FAISS retrieval is sub-50ms even on commodity hardware.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Embedding model | [`microsoft/codebert-base`](https://huggingface.co/microsoft/codebert-base), fine-tuned |
| Retrieval | FAISS (`faiss-cpu`, `IndexFlatIP`) |
| Backend | FastAPI, Uvicorn |
| Frontend | React.js, Axios |
| Training | PyTorch, HuggingFace Transformers, mixed-precision (fp16) on Colab T4 |
| Dataset | [CodeSearchNet](https://huggingface.co/datasets/code-search-net/code_search_net) |

---

## Dataset

Built on **CodeSearchNet**, loaded directly via the HuggingFace `datasets` library — no manual downloads required. 51,000 natural-language/code pairs are sampled across three languages:

| Language | Snippets |
|---|---|
| Python | 17,000 |
| Java | 17,000 |
| Go | 17,000 |

Each sample pairs a function's docstring (the natural language query) with its source code (the retrieval target).

---

## Metrics

Measured with `ml/evaluate.py` on the full 51K-snippet index:

```
==================================================
Total snippets indexed: 51,000
Languages: {
  "python": 17000,
  "java": 17000,
  "go": 17000
}
Retrieval latency (n=100):
  Median : 8.06 ms
  P95    : 9.76 ms
  Max    : 10.96 ms
  Sub-50ms retrieval confirmed (P95)

MRR@10 (200 held-out test pairs): 0.7972
==================================================
```

| Metric | Result |
|---|---|
| Snippets indexed | 51,000 |
| Languages covered | 3 (Python, Java, Go) |
| Median retrieval latency | 8.06 ms |
| P95 retrieval latency | 9.76 ms |
| Max retrieval latency | 10.96 ms |
| Embedding dimension | 768 |
| Fine-tuning objective | InfoNCE contrastive loss |
| MRR@10 (200 held-out pairs) | 0.7972 |

Re-run `ml/evaluate.py` after retraining to reproduce these numbers on your own machine.

---

## Project Structure

```
semantic-code-search/
├── data/
│   └── download.py            # pulls & samples CodeSearchNet via HuggingFace
├── ml/
│   ├── finetune.py             # fine-tunes CodeBERT (InfoNCE / bi-encoder)
│   ├── generate_embeddings.py  # encodes all snippets into dense vectors
│   ├── build_index.py          # builds + benchmarks the FAISS index
│   ├── evaluate.py             # measures latency & MRR@10
│   └── finetuned_model/        # saved fine-tuned weights (generated)
├── backend/
│   ├── main.py                 # FastAPI app (/search, /health, /stats)
│   ├── searcher.py             # loads model + index, runs queries
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── SearchBar.jsx
│   │   ├── ResultCard.jsx
│   │   └── Stats.jsx
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- (Optional) A GPU runtime such as Google Colab for fine-tuning — CPU works fine for inference

### 1. Clone & set up

```bash
git clone https://github.com/Shubhambhat06/semantic-code-search.git
cd semantic-code-search
```

### 2. Prepare the data

```bash
pip install datasets
python data/download.py
```

### 3. Train the model

Fine-tuning the bi-encoder is GPU-friendly and CPU-feasible. For speed, run `ml/finetune.py` on a free Colab GPU runtime, then move the resulting `finetuned_model/`, `embeddings.npy`, and `code_index.faiss` files into `ml/`.

```bash
pip install -r ml/requirements.txt
python ml/finetune.py
python ml/generate_embeddings.py
python ml/build_index.py
```

### 4. Run the backend

```bash
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for the interactive API explorer.

### 5. Run the frontend

```bash
cd frontend
npm install
npm start
```

Visit `http://localhost:3000`.

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/search?q=...&top_k=10&language=python` | GET | Natural language search, returns ranked + scored results |
| `/health` | GET | Liveness check + indexed vector count |
| `/stats` | GET | Index statistics (total snippets, per-language counts, embedding dim) |

Example:

```bash
curl "http://localhost:8000/search?q=read+a+file+line+by+line&language=python"
```

---

## Docker (optional)

```bash
docker-compose up --build
```

Spins up the backend on port `8000` and the frontend on port `3000`.

---

## Roadmap

- [ ] Add C++ and JavaScript corpora
- [ ] Swap `IndexFlatIP` for an IVF/HNSW index to scale past 1M+ snippets
- [ ] Add re-ranking with a cross-encoder for top-k results
- [ ] Deploy live demo

---

## Author

**Shubham Dattatraya Bhat**
[GitHub](https://github.com/Shubhambhat06) · [LinkedIn](https://linkedin.com/in/shubham-bhat-aab037344)

---

## License

MIT License — free to use, modify, and distribute.
