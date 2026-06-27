"""
Builds a FAISS index from embeddings.
Benchmarks retrieval latency (must hit sub-50ms).
Saves ml/code_index.faiss

Index type: IndexFlatIP (exact inner product / cosine after normalisation)
At 50K vectors of dim 768 this is fast enough on CPU for sub-50ms.
"""

import numpy as np
import faiss
import time
import json
from pathlib import Path

EMB_FILE   = Path("ml/embeddings.npy")
INDEX_FILE = Path("ml/code_index.faiss")
META_FILE  = Path("ml/metadata.jsonl")

def benchmark(index, embeddings, n_queries=100, top_k=10):
    print(f"\nBenchmarking retrieval ({n_queries} random queries, top-{top_k})...")
    query_idx = np.random.choice(len(embeddings), n_queries, replace=False)
    queries   = embeddings[query_idx]
    latencies = []
    for q in queries:
        q_vec = q.reshape(1, -1).copy()
        t0    = time.perf_counter()
        _D, _I = index.search(q_vec, top_k)
        t1    = time.perf_counter()
        latencies.append((t1 - t0) * 1000)  # ms

    latencies.sort()
    print(f"  Min latency:    {min(latencies):.2f} ms")
    print(f"  Median latency: {np.median(latencies):.2f} ms")
    print(f"  P95 latency:    {np.percentile(latencies, 95):.2f} ms")
    print(f"  Max latency:    {max(latencies):.2f} ms")

    p95 = np.percentile(latencies, 95)
    if p95 < 50:
        print(f"  ✅ P95 < 50ms — sub-50ms retrieval CONFIRMED")
    else:
        print(f"  ⚠️  P95 = {p95:.1f}ms — consider IVF index (see notes below)")
    return latencies

def main():
    print("Loading embeddings...")
    embeddings = np.load(EMB_FILE).astype("float32")
    print(f"  Shape: {embeddings.shape}")

    # L2-normalise so inner product = cosine similarity
    print("Normalising embeddings...")
    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]  # 768

    print("Building FAISS IndexFlatIP (exact cosine)...")
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print(f"  Index size: {index.ntotal} vectors")

    benchmark(index, embeddings)

    print(f"\nSaving index → {INDEX_FILE}")
    faiss.write_index(index, str(INDEX_FILE))
    print("Done. FAISS index ready.")

    # Quick sanity-check search
    print("\nSanity check — top-3 for first snippet:")
    q = embeddings[0].reshape(1, -1)
    D, I = index.search(q, 4)
    metadata = []
    with open(META_FILE, encoding="utf-8") as f:
        for line in f:
            metadata.append(json.loads(line))
    for rank, (score, idx) in enumerate(zip(D[0], I[0])):
        if idx == 0 and rank == 0:
            continue  # skip self
        print(f"  #{rank}: idx={idx}, score={score:.4f}, func={metadata[idx]['func_name']}")

if __name__ == "__main__":
    main()