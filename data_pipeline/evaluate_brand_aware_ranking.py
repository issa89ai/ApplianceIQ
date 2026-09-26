import json
import re

import numpy as np
from sentence_transformers import SentenceTransformer

from compare_hybrid_retrieval import (
    MODEL_NAME,
    build_tfidf_documents,
    lexical_scores,
    normalize,
)

EMBEDDINGS_PATH = "data_pipeline/processed/dryer_embeddings.npz"
NODES_PATH = "data_pipeline/processed/dryer_decision_trees.json"
TEST_CASES_PATH = "data_pipeline/evaluation/dryer_brand_ranking_cases.json"

SEMANTIC_WEIGHT = 0.80
LEXICAL_WEIGHT = 0.20

BRANDS = ["Whirlpool", "Samsung", "Kenmore", "GE", "LG"]
BRAND_ADJUSTMENTS = [0.00, 0.02, 0.05, 0.08, 0.12]

ERROR_CODE_BRANDS = {
    "d80": "LG",
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def guide_brand(title):
    for brand in BRANDS:
        if re.search(rf"\b{re.escape(brand)}\b", title, re.IGNORECASE):
            return brand

    return "generic"


def query_brand(query):
    lowered = query.lower()

    for error_code, brand in ERROR_CODE_BRANDS.items():
        if error_code in lowered:
            return brand

    for brand in BRANDS:
        if re.search(rf"\b{re.escape(brand.lower())}\b", lowered):
            return brand

    return "generic"


def apply_brand_adjustment(scores, metadata, detected_brand, adjustment):
    adjusted_scores = scores.copy()

    for index, item in enumerate(metadata):
        item_brand = guide_brand(item["title"])

        if detected_brand == "generic":
            if item_brand == "generic":
                adjusted_scores[index] += adjustment
            else:
                adjusted_scores[index] -= adjustment

        elif item_brand == detected_brand:
            adjusted_scores[index] += adjustment

        elif item_brand != "generic":
            adjusted_scores[index] -= adjustment

    return adjusted_scores


def evaluate(
    cases,
    model,
    guide_embeddings,
    metadata,
    idf,
    document_vectors,
    brand_adjustment,
):
    normalized_guides = normalize(guide_embeddings)

    top1_correct = 0
    top3_correct = 0
    reciprocal_ranks = []
    brand_correct = 0
    failures = []

    for case in cases:
        query_embedding = model.encode(case["query"])
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        semantic_score_values = normalized_guides @ query_embedding
        lexical_score_values = lexical_scores(
            case["query"],
            idf,
            document_vectors,
        )

        hybrid_score_values = (
            SEMANTIC_WEIGHT * semantic_score_values
            + LEXICAL_WEIGHT * lexical_score_values
        )

        detected_brand = query_brand(case["query"])

        final_scores = apply_brand_adjustment(
            hybrid_score_values,
            metadata,
            detected_brand,
            brand_adjustment,
        )

        ranked_indices = np.argsort(-final_scores)
        ranked_titles = [metadata[index]["title"] for index in ranked_indices]

        first_acceptable_rank = next(
            (
                rank
                for rank, title in enumerate(ranked_titles, start=1)
                if title in case["acceptable"]
            ),
            None,
        )

        is_top1 = first_acceptable_rank == 1
        is_top3 = (
            first_acceptable_rank is not None
            and first_acceptable_rank <= 3
        )

        top1_correct += is_top1
        top3_correct += is_top3
        reciprocal_ranks.append(
            1 / first_acceptable_rank if first_acceptable_rank else 0
        )

        top_brand = guide_brand(ranked_titles[0])

        if top_brand == case["expected_brand"]:
            brand_correct += 1

        if not is_top1:
            failures.append(
                {
                    "query": case["query"],
                    "detected_brand": detected_brand,
                    "expected_brand": case["expected_brand"],
                    "top_title": ranked_titles[0],
                    "top_brand": top_brand,
                    "acceptable_rank": first_acceptable_rank,
                }
            )

    total = len(cases)

    return {
        "top1": top1_correct / total,
        "top3": top3_correct / total,
        "mrr": sum(reciprocal_ranks) / total,
        "brand_accuracy": brand_correct / total,
        "failures": failures,
    }


def print_result(adjustment, result):
    print("\n==============================")
    print(f"Brand adjustment: {adjustment:.2f}")
    print(f"Top-1 guide accuracy: {result['top1']:.0%}")
    print(f"Top-3 guide accuracy: {result['top3']:.0%}")
    print(f"MRR: {result['mrr']:.3f}")
    print(f"Top-result brand accuracy: {result['brand_accuracy']:.0%}")

    if result["failures"]:
        print("Not ranked first:")

        for failure in result["failures"]:
            print(f'  "{failure["query"]}"')
            print(
                f'      query brand: {failure["detected_brand"]}; '
                f'expected: {failure["expected_brand"]}'
            )
            print(
                f'      top result: {failure["top_title"]} '
                f'({failure["top_brand"]})'
            )
            print(f'      acceptable rank: {failure["acceptable_rank"]}')


def main():
    cases = load_json(TEST_CASES_PATH)
    nodes = load_json(NODES_PATH)

    data = np.load(EMBEDDINGS_PATH, allow_pickle=True)
    guide_embeddings = data["embeddings"]
    metadata = json.loads(str(data["metadata"]))

    print(f"Loading model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    print("Building lexical TF-IDF index...")
    idf, document_vectors = build_tfidf_documents(nodes)

    print("\n=== Brand-aware hybrid ranking experiment ===")
    print("Brand adjustment 0.00 means current hybrid ranking.")
    print("Higher adjustments prefer generic or matching-brand guides.")

    for adjustment in BRAND_ADJUSTMENTS:
        result = evaluate(
            cases,
            model,
            guide_embeddings,
            metadata,
            idf,
            document_vectors,
            adjustment,
        )

        print_result(adjustment, result)


if __name__ == "__main__":
    main()