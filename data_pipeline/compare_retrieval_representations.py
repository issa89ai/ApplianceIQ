import json

import numpy as np
from sentence_transformers import SentenceTransformer

NODES_PATH = "data_pipeline/processed/dryer_decision_trees.json"
TEST_CASES_PATH = "data_pipeline/evaluation/dryer_retrieval_cases.json"
MODEL_NAME = "all-MiniLM-L6-v2"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def cause_or_branch_titles(node):
    if node["type"] == "leaf":
        return ", ".join(cause["title"] for cause in node["causes"])

    return ", ".join(branch["title"] for branch in node["branches"])


def full_guide_text(node):
    details = cause_or_branch_titles(node)

    if node["type"] == "leaf":
        return (
            f"{node['title']}. {node['description']} "
            f"Possible causes: {details}"
        )

    return (
        f"{node['title']}. {node['description']} "
        f"Related to: {details}"
    )


def symptom_focused_text(node):
    return f"{node['title']}. {node['description']}"


def weighted_symptom_text(node):
    symptom_text = f"{node['title']}. {node['description']}"
    details = cause_or_branch_titles(node)

    return f"{symptom_text} {symptom_text} Possible causes: {details}"


REPRESENTATIONS = {
    "Full guide text (historical baseline)": full_guide_text,
    "Symptom-focused text": symptom_focused_text,
    "Weighted symptom text": weighted_symptom_text,
}


def cosine_similarity(guide_embeddings, query_embedding):
    guide_norms = np.linalg.norm(guide_embeddings, axis=1)
    query_norm = np.linalg.norm(query_embedding)

    return (guide_embeddings @ query_embedding) / (guide_norms * query_norm)


def evaluate_representation(name, text_builder, model, nodes, test_cases):
    guide_texts = [text_builder(node) for node in nodes]
    guide_embeddings = model.encode(guide_texts)

    top1_correct = 0
    top3_correct = 0
    reciprocal_ranks = []
    failures = []

    for case in test_cases:
        query_embedding = model.encode(case["query"])
        scores = cosine_similarity(guide_embeddings, query_embedding)
        ranked_indices = np.argsort(-scores)
        ranked_titles = [nodes[index]["title"] for index in ranked_indices]

        first_acceptable_rank = next(
            (
                rank
                for rank, title in enumerate(ranked_titles, start=1)
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

        if not is_top1:
            failures.append(
                {
                    "query": case["query"],
                    "rank_1": ranked_titles[0],
                    "acceptable_rank": first_acceptable_rank,
                }
            )

    total = len(test_cases)
    mrr = sum(reciprocal_ranks) / total

    return {
        "name": name,
        "top1": top1_correct / total,
        "top3": top3_correct / total,
        "mrr": mrr,
        "failures": failures,
    }


def print_result(result):
    print(f"\n--- {result['name']} ---")
    print(f"Top-1 accuracy: {result['top1']:.0%}")
    print(f"Top-3 accuracy: {result['top3']:.0%}")
    print(f"MRR: {result['mrr']:.3f}")

    if result["failures"]:
        print("Not ranked first:")
        for failure in result["failures"]:
            print(f'  "{failure["query"]}"')
            print(f'      rank 1: {failure["rank_1"]}')
            print(f'      acceptable result rank: {failure["acceptable_rank"]}')


def main():
    nodes = load_json(NODES_PATH)
    test_cases = load_json(TEST_CASES_PATH)

    print(f"Loading model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    results = []

    for name, text_builder in REPRESENTATIONS.items():
        print(f"\nEvaluating: {name}")
        result = evaluate_representation(
            name,
            text_builder,
            model,
            nodes,
            test_cases,
        )
        results.append(result)

    print("\n=== Representation comparison ===")
    print(f"{'Representation':<38} {'Top-1':>8} {'Top-3':>8} {'MRR':>8}")

    for result in results:
        print(
            f"{result['name']:<38} "
            f"{result['top1']:>7.0%} "
            f"{result['top3']:>7.0%} "
            f"{result['mrr']:>8.3f}"
        )

    for result in results:
        print_result(result)


if __name__ == "__main__":
    main()
