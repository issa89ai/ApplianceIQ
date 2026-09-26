import json
import math
import re
from collections import Counter

import numpy as np
from sentence_transformers import SentenceTransformer

EMBEDDINGS_PATH = "data_pipeline/processed/dryer_embeddings.npz"
NODES_PATH = "data_pipeline/processed/dryer_decision_trees.json"
DEVELOPMENT_CASES_PATH = "data_pipeline/evaluation/dryer_retrieval_cases.json"
CHALLENGE_CASES_PATH = "data_pipeline/evaluation/dryer_retrieval_challenge_cases.json"
MODEL_NAME = "all-MiniLM-L6-v2"

LEXICAL_WEIGHTS = [0.0, 0.10, 0.20, 0.30, 0.40, 0.50]


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize(vectors):
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def node_to_lexical_text(node):
    parts = [node["title"], node.get("description", "")]

    for cause in node.get("causes", []):
        parts.append(cause["title"])
        parts.append(cause["steps"])

    for branch in node.get("branches", []):
        parts.append(branch["title"])

    return " ".join(parts)


def build_tfidf_documents(nodes):
    token_counts = []
    document_frequency = Counter()

    for node in nodes:
        counts = Counter(tokenize(node_to_lexical_text(node)))
        token_counts.append(counts)

        for token in counts:
            document_frequency[token] += 1

    total_documents = len(nodes)
    idf = {
        token: math.log((total_documents + 1) / (count + 1)) + 1
        for token, count in document_frequency.items()
    }

    document_vectors = []

    for counts in token_counts:
        vector = {
            token: (1 + math.log(count)) * idf[token]
            for token, count in counts.items()
        }

        vector_length = math.sqrt(sum(value * value for value in vector.values()))

        document_vectors.append(
            {
                token: value / vector_length
                for token, value in vector.items()
            }
        )

    return idf, document_vectors


def query_tfidf_vector(query, idf):
    counts = Counter(tokenize(query))

    vector = {
        token: (1 + math.log(count)) * idf[token]
        for token, count in counts.items()
        if token in idf
    }

    vector_length = math.sqrt(sum(value * value for value in vector.values()))

    if vector_length == 0:
        return {}

    return {
        token: value / vector_length
        for token, value in vector.items()
    }


def lexical_scores(query, idf, document_vectors):
    query_vector = query_tfidf_vector(query, idf)

    return np.array(
        [
            sum(
                query_value * document_vector.get(token, 0)
                for token, query_value in query_vector.items()
            )
            for document_vector in document_vectors
        ]
    )


def evaluate(
    cases,
    model,
    guide_embeddings,
    metadata,
    idf,
    document_vectors,
    lexical_weight,
):
    normalized_guides = normalize(guide_embeddings)

    top1_correct = 0
    top3_correct = 0
    reciprocal_ranks = []
    failures = []

    for case in cases:
        query_embedding = model.encode(case["query"])
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        semantic_scores = normalized_guides @ query_embedding
        lexical_score_values = lexical_scores(
            case["query"],
            idf,
            document_vectors,
        )

        final_scores = (
            (1 - lexical_weight) * semantic_scores
            + lexical_weight * lexical_score_values
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

    data = np.load(EMBEDDINGS_PATH, allow_pickle=True)
    guide_embeddings = data["embeddings"]
    metadata = json.loads(str(data["metadata"]))

    print(f"Loading model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    print("Building lexical TF-IDF index from guide titles, descriptions, and causes...")
    idf, document_vectors = build_tfidf_documents(nodes)

    print("\n=== Hybrid semantic + lexical retrieval experiment ===")
    print("Semantic score = sentence meaning.")
    print("Lexical score = exact important-word overlap.")
    print("A lexical weight of 0.00 is the historical semantic-only baseline.")
    print("This experiment does not apply the current backend brand filter.")

    for lexical_weight in LEXICAL_WEIGHTS:
        print("\n==============================")
        print(f"Lexical weight: {lexical_weight:.2f}")

        development_result = evaluate(
            development_cases,
            model,
            guide_embeddings,
            metadata,
            idf,
            document_vectors,
            lexical_weight,
        )

        challenge_result = evaluate(
            challenge_cases,
            model,
            guide_embeddings,
            metadata,
            idf,
            document_vectors,
            lexical_weight,
        )

        print_result("Development cases", development_result)
        print_result("Held-out challenge cases", challenge_result)


if __name__ == "__main__":
    main()
