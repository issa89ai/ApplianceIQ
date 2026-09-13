import json

import numpy as np
from sentence_transformers import SentenceTransformer


EMBEDDINGS_PATH = "data_pipeline/processed/dryer_embeddings.npz"
IN_SCOPE_CASES_PATH = "data_pipeline/evaluation/dryer_retrieval_cases.json"
OUT_OF_SCOPE_CASES_PATH = "data_pipeline/evaluation/dryer_out_of_scope_cases.json"
MODEL_NAME = "all-MiniLM-L6-v2"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_embeddings():
    data = np.load(EMBEDDINGS_PATH, allow_pickle=True)
    return data["embeddings"], json.loads(str(data["metadata"]))


def best_match(query, model, embeddings, metadata):
    query_embedding = model.encode(query)
    normalized_guides = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized_query = query_embedding / np.linalg.norm(query_embedding)
    scores = normalized_guides @ normalized_query
    best_index = int(np.argmax(scores))
    return metadata[best_index]["title"], float(scores[best_index])


def evaluate_threshold(threshold, in_scope, out_of_scope):
    false_rejections = sum(score < threshold for _, score in in_scope)
    false_acceptances = sum(score >= threshold for _, score in out_of_scope)
    correct = len(in_scope) - false_rejections + len(out_of_scope) - false_acceptances
    total = len(in_scope) + len(out_of_scope)
    return false_rejections, false_acceptances, correct / total


def main():
    in_scope_cases = load_json(IN_SCOPE_CASES_PATH)
    out_of_scope_cases = load_json(OUT_OF_SCOPE_CASES_PATH)
    embeddings, metadata = load_embeddings()

    print(f"Loading model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    in_scope = []
    print("\n--- In-scope dryer cases ---")
    for case in in_scope_cases:
        title, score = best_match(case["query"], model, embeddings, metadata)
        is_correct = title in case["acceptable"]
        if is_correct:
            in_scope.append((case["query"], score))
        status = "OK" if is_correct else "WRONG GUIDE"
        print(f"[{status}] {score:.3f}  {case['query']}")

    out_of_scope = []
    print("\n--- Out-of-scope cases that should be rejected ---")
    for case in out_of_scope_cases:
        title, score = best_match(case["query"], model, embeddings, metadata)
        out_of_scope.append((case["query"], score))
        print(f"[REJECT] {score:.3f}  {case['query']}")
        print(f"         best dryer match: {title}")

    print("\n=== Similarity-threshold experiment ===")
    print("A query is accepted as a dryer query when its best score is at least the threshold.")
    print(f"Correct in-scope retrievals: {len(in_scope)}/{len(in_scope_cases)}")
    print(f"In-scope score range: {min(score for _, score in in_scope):.3f} to {max(score for _, score in in_scope):.3f}")
    print(f"Out-of-scope score range: {min(score for _, score in out_of_scope):.3f} to {max(score for _, score in out_of_scope):.3f}")

    print("\nThreshold  False rejects  False accepts  Overall correct")
    candidates = [round(value, 2) for value in np.arange(0.35, 0.81, 0.05)]
    measurements = []
    for threshold in candidates:
        false_rejections, false_acceptances, accuracy = evaluate_threshold(
            threshold, in_scope, out_of_scope
        )
        measurements.append((threshold, false_rejections, false_acceptances, accuracy))
        print(
            f"{threshold:>8.2f}  {false_rejections:>13}  {false_acceptances:>13}  {accuracy:>14.0%}"
        )

    best = max(measurements, key=lambda item: item[3])
    print(
        f"\nBest tested threshold: {best[0]:.2f} "
        f"({best[1]} valid dryer queries rejected; {best[2]} out-of-scope queries accepted)."
    )
    if min(score for _, score in in_scope) <= max(score for _, score in out_of_scope):
        print("Conclusion: the score ranges overlap, so one threshold cannot perfectly separate these cases.")
    else:
        print("Conclusion: this small dataset has a score gap; validate with more realistic queries before using a threshold in the app.")


if __name__ == "__main__":
    main()
