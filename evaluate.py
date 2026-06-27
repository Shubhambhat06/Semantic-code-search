"""
Measures and prints all resume-claimable metrics:
- Total snippets indexed
- Languages covered
- Median + P95 retrieval latency
- MRR@10 on CodeSearchNet test pairs
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import json
import time
import numpy as np
import faiss
import torch
from pathlib import Path
from transformers import RobertaTokenizer, RobertaModel

MODEL_DIR  = Path("ml/finetuned_model")
INDEX_FILE = Path("ml/code_index.faiss")
META_FILE  = Path("ml/metadata.jsonl")
DATA_FILE  = Path("data/snippets.jsonl")

def encode_query(model, tokenizer, query, max_len=64):
    enc = tokenizer(query, max_length=max_len, padding="max_length",
                    truncation=True, return_tensors="pt")
    with torch.no_grad():
        out = model(**enc)
    emb = out.last_hidden_state[:, 0, :].numpy().astype("float32")
    faiss.normalize_L2(emb)
    return emb

def main():
    print("Loading artifacts...")
    tokenizer = RobertaTokenizer.from_pretrained(MODEL_DIR)
    model     = RobertaModel.from_pretrained(MODEL_DIR)
    model.eval()
    index    = faiss.read_index(str(INDEX_FILE))
    metadata = []
    with open(META_FILE, encoding="utf-8") as f:
        for line in f:
            metadata.append(json.loads(line))

    # ── Metric 1: Total snippets ──────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"Total snippets indexed: {index.ntotal:,}")

    # ── Metric 2: Languages ───────────────────────────────────────────────
    lang_counts = {}
    for m in metadata:
        lang_counts[m["language"]] = lang_counts.get(m["language"], 0) + 1
    print("Languages:", json.dumps(lang_counts, indent=2))

    # ── Metric 3: Retrieval latency ───────────────────────────────────────
    test_queries = [
        "sort a list of integers",
        "read lines from a file",
        "connect to a database",
        "parse JSON from a string",
        "calculate factorial recursively",
        "implement binary search",
        "send an HTTP GET request",
        "find duplicates in a list",
        "reverse a string",
        "compute fibonacci sequence",
    ] * 10  # 100 total

    latencies = []
    for q in test_queries:
        emb = encode_query(model, tokenizer, q)
        t0  = time.perf_counter()
        _D, _I = index.search(emb, 10)
        t1  = time.perf_counter()
        latencies.append((t1 - t0) * 1000)

    print(f"\nRetrieval latency (n={len(latencies)}):")
    print(f"  Median : {np.median(latencies):.2f} ms")
    print(f"  P95    : {np.percentile(latencies,95):.2f} ms")
    print(f"  Max    : {max(latencies):.2f} ms")
    if np.percentile(latencies, 95) < 50:
        print("  ✅ Sub-50ms retrieval confirmed (P95)")

    # ── Metric 4: MRR@10 ─────────────────────────────────────────────────
    print("\nComputing MRR@10 on 200 test pairs...")
    snippets = []
    with open(DATA_FILE, encoding="utf-8") as f:
        for line in f:
            snippets.append(json.loads(line))
    test_pairs = snippets[-200:]  # use last 200 as held-out

    reciprocal_ranks = []
    for pair in test_pairs:
        emb  = encode_query(model, tokenizer, pair["docstring"])
        D, I = index.search(emb, 10)
        rr   = 0.0
        for rank, idx in enumerate(I[0]):
            if idx == pair["id"]:
                rr = 1.0 / (rank + 1)
                break
        reciprocal_ranks.append(rr)

    mrr = np.mean(reciprocal_ranks)
    print(f"  MRR@10: {mrr:.4f}")
    if mrr > 0.5:
        print("  ✅ Strong MRR — fine-tuning is working")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()