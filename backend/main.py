import json
import numpy as np
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer

EMBEDDINGS_PATH = "data_pipeline/processed/dryer_embeddings.npz"
TREES_PATH = "data_pipeline/processed/dryer_decision_trees.json"
MODEL_NAME = "all-MiniLM-L6-v2"

app = FastAPI()

print("Loading model and data...")
model = SentenceTransformer(MODEL_NAME)

data = np.load(EMBEDDINGS_PATH, allow_pickle=True)
embeddings = data["embeddings"]
metadata = json.loads(str(data["metadata"]))

with open(TREES_PATH, "r", encoding="utf-8") as f:
    tree_nodes = json.load(f)
nodes_by_wikiid = {node["wikiid"]: node for node in tree_nodes}

print("Ready.")


def cosine_similarity(a, b):
    a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b)
    return a_norm @ b_norm


@app.get("/search")
def search(q: str, top_k: int = 3):
    query_embedding = model.encode(q)
    scores = cosine_similarity(embeddings, query_embedding)
    ranked_indices = np.argsort(-scores)[:top_k]

    results = []
    for idx in ranked_indices:
        wikiid = metadata[idx]["wikiid"]
        node = nodes_by_wikiid[wikiid]
        results.append({"score": float(scores[idx]), **node})

    return {"query": q, "results": results}


@app.get("/health")
def health():
    return {"status": "ok"}