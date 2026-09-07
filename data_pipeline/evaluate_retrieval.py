import json
import numpy as np
from sentence_transformers import SentenceTransformer

EMBEDDINGS_PATH = "data_pipeline/processed/dryer_embeddings.npz"
TEST_CASES_PATH = "data_pipeline/evaluation/dryer_retrieval_cases.json"
MODEL_NAME = "all-MiniLM-L6-v2"

def load_test_cases():
    with open(TEST_CASES_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


TEST_CASES = load_test_cases()

OUT_OF_SCOPE_QUERIES = [
    "my refrigerator isn't cooling",
    "dishwasher won't drain",
    "oven not heating up",
    "washing machine leaking water",
]

AMBIGUOUS_QUERIES = [
    "dryer isn't working right",
    "cycle ends early and clothes are still wet",
]


def load_embeddings():
    data = np.load(EMBEDDINGS_PATH, allow_pickle=True)
    embeddings = data["embeddings"]
    metadata = json.loads(str(data["metadata"]))
    return embeddings, metadata


def cosine_similarity(a, b):
    a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b)
    return a_norm @ b_norm


def search(query, model, embeddings, metadata, top_k=3):
    query_embedding = model.encode(query)
    scores = cosine_similarity(embeddings, query_embedding)
    ranked_indices = np.argsort(-scores)[:top_k]
    return [(metadata[idx]["title"], float(scores[idx])) for idx in ranked_indices]


def run_accuracy_eval(model, embeddings, metadata):
    top1_correct = 0
    top3_correct = 0
    reciprocal_ranks = []
    correct_top1_scores = []

    for case in TEST_CASES:
        results = search(
            case["query"],
            model,
            embeddings,
            metadata,
            top_k=len(metadata),
        )

        titles = [title for title, score in results]
        

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
        reciprocal_ranks.append(
            1 / first_acceptable_rank if first_acceptable_rank is not None else 0
        )

        if is_top1:
            correct_top1_scores.append(results[0][1])

        status = "OK" if is_top1 else ("~" if is_top3 else "X")
        print(f"[{status}] \"{case['query']}\"")
        print(f"      got: {titles[0]} ({results[0][1]:.3f})")

        if first_acceptable_rank is not None:
            print(f"      first acceptable result rank: {first_acceptable_rank}")
        else:
            print(f"      expected one of: {case['acceptable']}")

    total = len(TEST_CASES)
    mrr = sum(reciprocal_ranks) / total

    print(f"\nTop-1 accuracy: {top1_correct}/{total} ({100 * top1_correct / total:.0f}%)")
    print(f"Top-3 accuracy: {top3_correct}/{total} ({100 * top3_correct / total:.0f}%)")
    print(f"MRR: {mrr:.3f}")

    return correct_top1_scores

def run_stress_tests(model, embeddings, metadata, correct_top1_scores):
    print("\n--- Out-of-scope queries (appliances we don't cover at all) ---")
    for query in OUT_OF_SCOPE_QUERIES:
        results = search(query, model, embeddings, metadata, top_k=1)
        title, score = results[0]
        print(f'  "{query}"')
        print(f"      best (wrong) match: {title} ({score:.3f})")

    print("\n--- Ambiguous queries (no single clearly-correct page) ---")
    for query in AMBIGUOUS_QUERIES:
        results = search(query, model, embeddings, metadata, top_k=3)
        print(f'  "{query}"')
        for title, score in results:
            print(f"      {score:.3f}  {title}")

    if correct_top1_scores:
        avg_correct = sum(correct_top1_scores) / len(correct_top1_scores)
        print(f"\nFor comparison: correct in-scope matches scored between "
              f"{min(correct_top1_scores):.3f} and {max(correct_top1_scores):.3f} "
              f"(average {avg_correct:.3f})")


def main():
    embeddings, metadata = load_embeddings()
    model = SentenceTransformer(MODEL_NAME)

    correct_top1_scores = run_accuracy_eval(model, embeddings, metadata)
    run_stress_tests(model, embeddings, metadata, correct_top1_scores)


if __name__ == "__main__":
    main()