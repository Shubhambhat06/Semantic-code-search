import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import time
from pathlib import Path

import faiss
import numpy as np
import torch
from transformers import RobertaModel, RobertaTokenizer

MODEL_DIR = Path("../ml/finetuned_model")
INDEX_FILE = Path("../ml/code_index.faiss")
SNIPPETS_FILE = Path("../data/snippets.jsonl")
MAX_NL_LEN = 64


class Searcher:
    def __init__(self):
        print("Loading tokenizer...")
        self.tokenizer = RobertaTokenizer.from_pretrained(MODEL_DIR)

        print("Loading fine-tuned model...")
        self.model = RobertaModel.from_pretrained(MODEL_DIR)
        self.model.eval()

        print("Loading FAISS index...")
        self.index = faiss.read_index(str(INDEX_FILE))

        print("Loading snippets...")
        self.metadata = []
        with open(SNIPPETS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                self.metadata.append(json.loads(line))

        print(
            f"Searcher ready. "
            f"{self.index.ntotal} vectors indexed, "
            f"{len(self.metadata)} snippets loaded."
        )

    def encode_query(self, query: str) -> np.ndarray:
        enc = self.tokenizer(
            query,
            max_length=MAX_NL_LEN,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        with torch.no_grad():
            out = self.model(**enc)

            emb = (
                out.last_hidden_state[:, 0, :]
                .cpu()
                .numpy()
                .astype("float32")
            )

        faiss.normalize_L2(emb)
        return emb

    def search(
        self,
        query: str,
        top_k: int = 10,
        language: str | None = None,
    ):
        t0 = time.perf_counter()

        query_emb = self.encode_query(query)

        D, I = self.index.search(query_emb, top_k * 3)

        latency_ms = (time.perf_counter() - t0) * 1000

        results = []

        for score, idx in zip(D[0], I[0]):
            if idx < 0:
                continue

            if idx >= len(self.metadata):
                continue

            meta = self.metadata[idx]

            if language and meta["language"] != language:
                continue

            results.append(
                {
                    "id": meta.get("id", idx),
                    "language": meta.get("language", ""),
                    "func_name": meta.get("func_name", ""),
                    "url": meta.get("url", ""),
                    "docstring": meta.get("docstring", ""),
                    "code_preview": meta.get("code", ""),
                    "score": round(float(score), 4),
                }
            )

            if len(results) >= top_k:
                break

        return {
            "query": query,
            "latency_ms": round(latency_ms, 2),
            "total": len(results),
            "results": results,
        }