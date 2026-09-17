import json

import numpy as np
from sentence_transformers import SentenceTransformer


EMBEDDINGS_PATH = "data_pipeline/processed/dryer_embeddings.npz"
CHALLENGE_CASES_PATH = "data_pipeline/evaluation/dryer_retrieval_challenge_cases.json"
MODEL_NAME = "all-MiniLM-L6-v2"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_embeddings():
    data = np.load(EMBEDDINGS_PATH, allow_pickle=True)
    return data["embeddings"], json.loads(str(data["metadata"]))


def rank_guides(query, model, embeddings, metadata):
    query_embedding = model.encode(query)
    normalized_guides = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized_query = query_embedding / np.linalg.norm(query_embedding)
    scores = normalized_guides @ normalized_query
    ranked_indices = np.argsort(-scores)
    return [(metadata[index]["title"], float(scores[index])) for index in ranked_indices]


def main():
    cases = load_json(CHALLENGE_CASES_PATH)
    embeddings, metadata = load_embeddings()
    model = SentenceTransformer(MODEL_NAME)

    top1_correct = 0
    top3_correct = 0
    reciprocal_ranks = []

    print("=== Held-out dryer retrieval challenge ===")
    for case in cases:
        ranked = rank_guides(case["query"], model, embeddings, metadata)
        titles = [title for title, _ in ranked]
        first_acceptable_rank = next(
            (
                rank
                for rank, title in enumerate(titles, start=1)
                if title in case["acceptable"]
            ),
            None,
        )
        is_top1 = first_acceptable_rank == 1
        is_top3 = first_acceptable_rank is not None and first_acceptable_rank <= 3
        top1_correct += is_top1
        top3_correct += is_top3
        reciprocal_ranks.append(1 / first_acceptable_rank if first_acceptable_rank else 0)

        status = "OK" if is_top1 else ("~" if is_top3 else "MISS")
        print(f"[{status}] {case['query']}")
        print(f"      top result: {ranked[0][0]} ({ranked[0][1]:.3f})")
        print(f"      first acceptable rank: {first_acceptable_rank}")

    total = len(cases)
    print(f"\nTop-1 accuracy: {top1_correct}/{total} ({100 * top1_correct / total:.0f}%)")
    print(f"Top-3 accuracy: {top3_correct}/{total} ({100 * top3_correct / total:.0f}%)")
    print(f"MRR: {sum(reciprocal_ranks) / total:.3f}")
    print("These cases are held out from representation-selection experiments.")


if __name__ == "__main__":
    main()
