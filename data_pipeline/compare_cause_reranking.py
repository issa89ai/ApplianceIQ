import json
import numpy as np
from sentence_transformers import SentenceTransformer

EMBEDDINGS_PATH = "data_pipeline/processed/dryer_embeddings.npz"
NODES_PATH = "data_pipeline/processed/dryer_decision_trees.json"
DEVELOPMENT_CASES_PATH = "data_pipeline/evaluation/dryer_retrieval_cases.json"
CHALLENGE_CASES_PATH = "data_pipeline/evaluation/dryer_retrieval_challenge_cases.json"
MODEL_NAME = "all-MiniLM-L6-v2"

CANDIDATE_COUNT = 5
CAUSE_WEIGHTS = [0.0, 0.10, 0.20, 0.30, 0.40]


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_production_embeddings():
    data = np.load(EMBEDDINGS_PATH, allow_pickle=True)
    return data["embeddings"], json.loads(str(data["metadata"]))


def normalize(vectors):
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def build_cause_embeddings(model, nodes):
    cause_embeddings = {}

    for node in nodes:
        cause_chunks = [
            f"{cause['title']}. {cause['steps']}"
            for cause in node.get("causes", [])
        ]

        if cause_chunks:
            embeddings = model.encode(cause_chunks)
            cause_embeddings[node["wikiid"]] = normalize(embeddings)

    return cause_embeddings


def rerank(query_embedding, symptom_scores, metadata, cause_embeddings, cause_weight):
    candidate_indices = np.argsort(-symptom_scores)[:CANDIDATE_COUNT]
    final_scores = np.full(len(metadata), -np.inf)

    for index in candidate_indices:
        wikiid = metadata[index]["wikiid"]
        cause_vectors = cause_embeddings.get(wikiid)

        if cause_vectors is None:
            cause_score = symptom_scores[index]
        else:
            cause_score = float(np.max(cause_vectors @ query_embedding))

        final_scores[index] = (
            (1 - cause_weight) * symptom_scores[index]
            + cause_weight * cause_score
        )

    return np.argsort(-final_scores)


def evaluate(cases, model, guide_embeddings, metadata, cause_embeddings, cause_weight):
    top1_correct = 0
    top3_correct = 0
    reciprocal_ranks = []
    failures = []

    normalized_guides = normalize(guide_embeddings)

    for case in cases:
        query_embedding = model.encode(case["query"])
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        symptom_scores = normalized_guides @ query_embedding
        ranked_indices = rerank(
            query_embedding,
            symptom_scores,
            metadata,
            cause_embeddings,
            cause_weight,
        )

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
        is_top3 = first_acceptable_rank is not None and first_acceptable_rank <= 3

        top1_correct += is_top1
        top3_correct += is_top3
        reciprocal_ranks.append(
            1 / first_acceptable_rank if first_acceptable_rank else 0
        )

        if not is_top1:
            failures.append(
                {
                    "query": case["query"],
                    "top_title": ranked_titles[0],
                    "acceptable_rank": first_acceptable_rank,
                }
            )

    total = len(cases)

    return {
        "top1": top1_correct / total,
        "top3": top3_correct / total,
        "mrr": sum(reciprocal_ranks) / total,
        "failures": failures,
    }


def print_result(name, result):
    print(f"\n--- {name} ---")
    print(f"Top-1: {result['top1']:.0%}")
    print(f"Top-3: {result['top3']:.0%}")
    print(f"MRR:   {result['mrr']:.3f}")

    if result["failures"]:
        print("Not ranked first:")
        for failure in result["failures"]:
            print(f'  "{failure["query"]}"')
            print(f'      top result: {failure["top_title"]}')
            print(f'      acceptable rank: {failure["acceptable_rank"]}')


def main():
    development_cases = load_json(DEVELOPMENT_CASES_PATH)
    challenge_cases = load_json(CHALLENGE_CASES_PATH)
    nodes = load_json(NODES_PATH)
    guide_embeddings, metadata = load_production_embeddings()

    print(f"Loading model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    print("Embedding detailed cause sections...")
    cause_embeddings = build_cause_embeddings(model, nodes)

    print("\n=== Two-stage cause re-ranking experiment ===")
    print(
        "Stage 1: retrieve the best 5 guides using current symptom-focused embeddings."
    )
    print(
        "Stage 2: use detailed cause text only to re-rank those 5 candidates."
    )

    for cause_weight in CAUSE_WEIGHTS:
        print(f"\n==============================")
        print(f"Cause-text weight: {cause_weight:.2f}")

        development_result = evaluate(
            development_cases,
            model,
            guide_embeddings,
            metadata,
            cause_embeddings,
            cause_weight,
        )

        challenge_result = evaluate(
            challenge_cases,
            model,
            guide_embeddings,
            metadata,
            cause_embeddings,
            cause_weight,
        )

        print_result("Development cases", development_result)
        print_result("Held-out challenge cases", challenge_result)


if __name__ == "__main__":
    main()