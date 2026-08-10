import json
import numpy as np
from sentence_transformers import SentenceTransformer

INPUT_PATH = "data_pipeline/processed/dryer_decision_trees.json"
EMBEDDINGS_PATH = "data_pipeline/processed/dryer_embeddings.npz"

MODEL_NAME = "all-MiniLM-L6-v2"


def load_tree_nodes():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def node_to_text(node):
    description = node.get("description", "")
    if node["type"] == "leaf":
        cause_titles = ", ".join(c["title"] for c in node["causes"])
        return f"{node['title']}. {description} Possible causes: {cause_titles}"
    else:
        branch_titles = ", ".join(b["title"] for b in node["branches"])
        return f"{node['title']}. {description} Related to: {branch_titles}"


def main():
    nodes = load_tree_nodes()
    texts = [node_to_text(n) for n in nodes]

    print(f"Loading model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Embedding {len(texts)} nodes...")
    embeddings = model.encode(texts, show_progress_bar=True)

    metadata = [
        {"wikiid": n["wikiid"], "title": n["title"], "type": n["type"]}
        for n in nodes
    ]

    np.savez(
        EMBEDDINGS_PATH,
        embeddings=embeddings,
        metadata=json.dumps(metadata),
    )

    print(f"\nSaved {len(nodes)} embeddings to {EMBEDDINGS_PATH}")
    print(f"Embedding dimension: {embeddings.shape[1]}")


if __name__ == "__main__":
    main()