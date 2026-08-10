import json
import numpy as np
from sentence_transformers import SentenceTransformer

EMBEDDINGS_PATH = "data_pipeline/processed/dryer_embeddings.npz"
MODEL_NAME = "all-MiniLM-L6-v2"


def load_embeddings():
    data = np.load(EMBEDDINGS_PATH, allow_pickle=True)
    embeddings = data["embeddings"]
    metadata = json.loads(str(data["metadata"]))
    return embeddings, metadata


def cosine_similarity(a, b):
    a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b)
    return a_norm @ b_norm


def search(query, model, embeddings, metadata, top_k=5):
    query_embedding = model.encode(query)
    scores = cosine_similarity(embeddings, query_embedding)
    ranked_indices = np.argsort(-scores)[:top_k]

    results = []
    for idx in ranked_indices:
        results.append({
            "title": metadata[idx]["title"],
            "type": metadata[idx]["type"],
            "score": float(scores[idx]),
        })
    return results


def main():
    embeddings, metadata = load_embeddings()
    model = SentenceTransformer(MODEL_NAME)

    test_queries = [
        "it makes a loud noise when spinning",
        "clothes come out still wet",
        "won't turn on at all",
        "smells like it's burning",
    ]

    for query in test_queries:
        print(f"\nQuery: \"{query}\"")
        results = search(query, model, embeddings, metadata)
        for r in results[:3]:
            print(f"  {r['score']:.3f}  [{r['type']:7}] {r['title']}")


if __name__ == "__main__":
    main()