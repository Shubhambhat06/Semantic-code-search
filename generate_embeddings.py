import json
import numpy as np
import torch
from transformers import RobertaTokenizer, RobertaModel
from pathlib import Path
from tqdm import tqdm

MODEL_DIR = Path("ml/finetuned_model")
DATA_FILE = Path("data/snippets.jsonl")
EMB_FILE = Path("ml/embeddings.npy")
META_FILE = Path("ml/metadata.jsonl")

BATCH_SIZE = 32
MAX_LEN = 256


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output.last_hidden_state
    input_mask_expanded = (
        attention_mask.unsqueeze(-1)
        .expand(token_embeddings.size())
        .float()
    )

    return torch.sum(
        token_embeddings * input_mask_expanded,
        dim=1
    ) / torch.clamp(
        input_mask_expanded.sum(dim=1),
        min=1e-9
    )


def encode_batch(model, tokenizer, texts):
    enc = tokenizer(
        texts,
        max_length=MAX_LEN,
        padding=True,
        truncation=True,
        return_tensors="pt"
    )

    with torch.no_grad():
        out = model(**enc)

    emb = mean_pooling(
        out,
        enc["attention_mask"]
    )

    return emb.numpy().astype("float32")


def main():
    print("Loading fine-tuned model...")
    tokenizer = RobertaTokenizer.from_pretrained(MODEL_DIR)
    model = RobertaModel.from_pretrained(MODEL_DIR)
    model.eval()

    print("Loading snippets...")
    snippets = []

    with open(DATA_FILE, encoding="utf-8") as f:
        for line in f:
            snippets.append(json.loads(line))

    print(f"{len(snippets)} snippets loaded")

    print("Generating embeddings...")

    all_embeddings = []

    for i in tqdm(range(0, len(snippets), BATCH_SIZE)):
        batch = snippets[i:i + BATCH_SIZE]

        texts = [
            f"{s.get('func_name','')} {s.get('docstring','')} {s['code']}"
            for s in batch
        ]

        emb = encode_batch(
            model,
            tokenizer,
            texts
        )

        all_embeddings.append(emb)

    embeddings = np.vstack(all_embeddings).astype("float32")

    print("Embedding matrix shape:", embeddings.shape)

    print("Saving embeddings...")
    np.save(EMB_FILE, embeddings)

    print("Saving metadata...")

    with open(META_FILE, "w", encoding="utf-8") as f:
        for s in snippets:
            meta = {
                "id": s["id"],
                "language": s["language"],
                "func_name": s.get("func_name", ""),
                "url": s.get("url", ""),
                "docstring": s.get("docstring", "")[:200],
                "code": s["code"][:400],
            }
            f.write(json.dumps(meta) + "\n")

    print("Done.")


if __name__ == "__main__":
    main()