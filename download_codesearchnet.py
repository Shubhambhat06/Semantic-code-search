"""
Downloads CodeSearchNet via HuggingFace datasets library.
No manual URLs needed — works reliably in 2025.
Samples 50K snippets: ~17K each from Python, Java, Go.
Saves to data/snippets.jsonl
"""

import json
import random
from pathlib import Path
from datasets import load_dataset

TARGET_PER_LANG = 17000
OUT_FILE = Path("data/snippets.jsonl")
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# CodeSearchNet has no C++ — we use Go as 3rd language
# (same benchmark, same paper, fully legitimate)
LANGUAGES = ["python", "java", "go"]

def main():
    all_snippets = []

    for lang in LANGUAGES:
        print(f"\nLoading {lang} from HuggingFace...")
        # loads only the train split to save disk space
        ds = load_dataset(
            "code-search-net/code_search_net",
            lang,
            split="train",
            trust_remote_code=True,
        )
        print(f"  Raw size: {len(ds)} samples")

        # shuffle and sample
        indices = list(range(len(ds)))
        random.seed(42)
        random.shuffle(indices)
        indices = indices[:TARGET_PER_LANG]

        count = 0
        for i in indices:
            row = ds[i]
            code = row.get("func_code_string", "").strip()
            doc  = row.get("func_documentation_string", "").strip()
            if not code or not doc or len(code) < 30:
                continue
            all_snippets.append({
                "id":        0,           # will re-assign below
                "language":  lang,
                "code":      code,
                "docstring": doc,
                "func_name": row.get("func_name", ""),
                "url":       row.get("func_code_url", ""),
            })
            count += 1

        print(f"  Kept {count} snippets for {lang}")

    # sequential IDs
    for i, s in enumerate(all_snippets):
        s["id"] = i

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        for s in all_snippets:
            f.write(json.dumps(s) + "\n")

    print(f"\nTotal saved: {len(all_snippets)} snippets → {OUT_FILE}")

if __name__ == "__main__":
    main()