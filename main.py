"""
FastAPI backend for Semantic Code Search Engine.
Endpoints:
  GET  /health           — liveness check
  GET  /search           — main search endpoint
  GET  /stats            — index stats
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from searcher import Searcher
import time

searcher: Searcher = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global searcher
    print("Starting up — loading models...")
    searcher = Searcher()
    yield
    print("Shutting down.")

app = FastAPI(
    title="Semantic Code Search API",
    description="Natural language search over 50K+ code snippets using CodeBERT + FAISS",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "indexed_vectors": searcher.index.ntotal if searcher else 0,
        "timestamp": time.time(),
    }

@app.get("/search")
def search(
    q: str = Query(..., description="Natural language query", min_length=2),
    top_k: int = Query(10, ge=1, le=50),
    language: str = Query(None, description="Filter by language: python, java, cpp"),
):
    if not searcher:
        return {"error": "Model not loaded yet"}
    return searcher.search(query=q, top_k=top_k, language=language)

@app.get("/stats")
def stats():
    if not searcher:
        return {"error": "Model not loaded yet"}
    lang_counts = {}
    for m in searcher.metadata:
        lang = m["language"]
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
    return {
        "total_snippets": searcher.index.ntotal,
        "languages":      lang_counts,
        "embedding_dim":  searcher.index.d,
    }