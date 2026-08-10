import json
import numpy as np
from sentence_transformers import SentenceTransformer

EMBEDDINGS_PATH = "data_pipeline/processed/dryer_embeddings.npz"
MODEL_NAME = "all-MiniLM-L6-v2"

TEST_CASES = [
    {
        "query": "it makes a loud noise when spinning",
        "acceptable": ["Dryer Making Loud Noise", "Dryer Squeaking"],
    },
    {
        "query": "clothes come out still wet",
        "acceptable": [
            "Dryer Not Heating", "Gas Dryer Not Heating", "Electric Dryer Not Heating",
            "Kenmore Dryer Not Heating", "Samsung Dryer Not Heating", "Whirlpool Dryer Not Heating",
        ],
    },
    {
        "query": "won't turn on at all",
        "acceptable": ["Dryer Will Not Start", "Kenmore Dryer Won't Turn On or Power On"],
    },
    {
        "query": "smells like it's burning",
        "acceptable": ["Dryer Smells Like Burning"],
    },
    {
        "query": "I smell gas near the dryer",
        "acceptable": ["Dryer Smells Like Gas"],
    },
    {
        "query": "the drum isn't turning",
        "acceptable": [
            "Dryer Not Spinning", "GE Dryer Not Spinning", "Maytag Dryer Not Spinning",
            "Whirlpool Dryer Not Spinning",
        ],
    },
    {
        "query": "cycle stops halfway through",
        "acceptable": ["Dryer Stops Mid Cycle"],
    },
    {
        "query": "showing an error code D80",
        "acceptable": ["LG Dryer D80 Code"],
    },
    {
        "query": "squeaky sound while running",
        "acceptable": ["Dryer Squeaking"],
    },
    {
        "query": "dryer is completely dead, no lights, nothing",
        "acceptable": ["Kenmore Dryer Won't Turn On or Power On", "Dryer Will Not Start"],
    },
    {
        "query": "not warm at all after full cycle",
        "acceptable": [
            "Dryer Not Heating", "Gas Dryer Not Heating", "Electric Dryer Not Heating",
            "Kenmore Dryer Not Heating", "Samsung Dryer Not Heating", "Whirlpool Dryer Not Heating",
        ],
    },
    {
        "query": "loud banging noise during tumble",
        "acceptable": ["Dryer Making Loud Noise", "Dryer Squeaking"],
    },
]

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
    correct_top1_scores = []

    for case in TEST_CASES:
        results = search(case["query"], model, embeddings, metadata, top_k=3)
        titles = [r[0] for r in results]
        is_top1 = titles[0] in case["acceptable"]
        is_top3 = any(t in case["acceptable"] for t in titles)

        top1_correct += is_top1
        top3_correct += is_top3
        if is_top1:
            correct_top1_scores.append(results[0][1])

        status = "OK" if is_top1 else ("~" if is_top3 else "X")
        print(f"[{status}] \"{case['query']}\"")
        print(f"      got: {titles[0]} ({results[0][1]:.3f})")
        if not is_top1:
            print(f"      expected one of: {case['acceptable']}")

    total = len(TEST_CASES)
    print(f"\nTop-1 accuracy: {top1_correct}/{total} ({100*top1_correct/total:.0f}%)")
    print(f"Top-3 accuracy: {top3_correct}/{total} ({100*top3_correct/total:.0f}%)")

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