import json

import numpy as np
from sentence_transformers import SentenceTransformer


IN_SCOPE_CASES_PATH = "data_pipeline/evaluation/dryer_retrieval_cases.json"
OUT_OF_SCOPE_CASES_PATH = "data_pipeline/evaluation/dryer_out_of_scope_cases.json"
MODEL_NAME = "all-MiniLM-L6-v2"

# These are short descriptions of the supported domain, not repair guides.
DRYER_PROTOTYPES = [
    "A household clothes dryer repair problem.",
    "A tumble dryer that is not heating, spinning, starting, or drying clothes.",
    "Troubleshooting a clothes dryer drum, dryer cycle, or dryer airflow problem.",
]

# A transparent deterministic baseline. It recognizes only appliance words the
# application explicitly does not support today.
UNSUPPORTED_APPLIANCE_TERMS = [
    "refrigerator",
    "freezer",
    "dishwasher",
    "oven",
    "stove",
    "washing machine",
    "washer",
    "microwave",
    "air conditioner",
    "water heater",
    "vacuum",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def contains_dryer_word(query):
    return "dryer" in query.lower()


def has_known_unsupported_appliance(query):
    lowered = query.lower()
    return any(term in lowered for term in UNSUPPORTED_APPLIANCE_TERMS)


def prototype_scores(model, queries):
    prototype_embeddings = model.encode(DRYER_PROTOTYPES)
    query_embeddings = model.encode(queries)

    prototype_embeddings /= np.linalg.norm(prototype_embeddings, axis=1, keepdims=True)
    query_embeddings /= np.linalg.norm(query_embeddings, axis=1, keepdims=True)
    return (query_embeddings @ prototype_embeddings.T).max(axis=1)


def accuracy(predictions, expected):
    return sum(prediction == label for prediction, label in zip(predictions, expected)) / len(expected)


def print_method_result(name, predictions, expected):
    print(f"{name}: {accuracy(predictions, expected):.0%} correct")
    for prediction, label, case in zip(predictions, expected, ALL_CASES):
        if prediction != label:
            expected_text = "accept dryer query" if label else "reject non-dryer query"
            actual_text = "accepted" if prediction else "rejected"
            print(f"  [{actual_text}] {case['query']} (should {expected_text})")


def main():
    global ALL_CASES
    in_scope = load_json(IN_SCOPE_CASES_PATH)
    out_of_scope = load_json(OUT_OF_SCOPE_CASES_PATH)
    ALL_CASES = in_scope + out_of_scope
    expected = [True] * len(in_scope) + [False] * len(out_of_scope)
    queries = [case["query"] for case in ALL_CASES]

    print(f"Loading model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    print("\n=== Domain-routing baselines ===")
    print("Accept means: send the query to the dryer-guide retriever.")
    print("Reject means: tell the user that the current prototype supports dryers only.\n")

    dryer_word_predictions = [contains_dryer_word(query) for query in queries]
    print_method_result("Word 'dryer' required", dryer_word_predictions, expected)

    appliance_guard_predictions = [
        not has_known_unsupported_appliance(query) for query in queries
    ]
    print_method_result("Known non-dryer appliance-word guard", appliance_guard_predictions, expected)

    scores = prototype_scores(model, queries)
    print("\n=== Semantic dryer-intent prototype ===")
    print("The score is similarity to short descriptions of a clothes-dryer problem.")
    print("\nScore   Expected                 Query")
    for score, label, case in zip(scores, expected, ALL_CASES):
        expected_text = "dryer" if label else "reject"
        print(f"{score:.3f}   {expected_text:<22} {case['query']}")

    print("\nThreshold  Valid dryer queries rejected  Non-dryer queries accepted  Overall correct")
    measurements = []
    for threshold in [round(value, 2) for value in np.arange(0.25, 0.81, 0.05)]:
        predictions = [score >= threshold for score in scores]
        false_rejections = sum(not prediction for prediction in predictions[: len(in_scope)])
        false_acceptances = sum(predictions[len(in_scope) :])
        result = accuracy(predictions, expected)
        measurements.append((threshold, false_rejections, false_acceptances, result))
        print(f"{threshold:>8.2f}  {false_rejections:>27}  {false_acceptances:>26}  {result:>14.0%}")

    best = max(measurements, key=lambda measurement: measurement[3])
    print(
        f"\nBest tested semantic threshold: {best[0]:.2f} "
        f"({best[1]} valid dryer queries rejected; {best[2]} non-dryer queries accepted)."
    )
    print("This is an exploratory comparison on 32 labeled examples, not a production deployment decision.")


if __name__ == "__main__":
    main()
