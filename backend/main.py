import json
import math
import re
from collections import Counter

import numpy as np
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer


EMBEDDINGS_PATH = "data_pipeline/processed/dryer_embeddings.npz"
TREES_PATH = "data_pipeline/processed/dryer_decision_trees.json"
MODEL_NAME = "all-MiniLM-L6-v2"

SEMANTIC_WEIGHT = 0.80
LEXICAL_WEIGHT = 0.20

app = FastAPI()


def normalize_matrix(vectors):
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def normalize_vector(vector):
    return vector / np.linalg.norm(vector)


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


def build_tfidf_index(nodes):
    document_token_counts = []
    document_frequency = Counter()

    for node in nodes:
        token_counts = Counter(tokenize(node_to_lexical_text(node)))
        document_token_counts.append(token_counts)

        for token in token_counts:
            document_frequency[token] += 1

    total_documents = len(nodes)

    inverse_document_frequency = {
        token: math.log((total_documents + 1) / (count + 1)) + 1
        for token, count in document_frequency.items()
    }

    document_vectors = []

    for token_counts in document_token_counts:
        vector = {
            token: (1 + math.log(count)) * inverse_document_frequency[token]
            for token, count in token_counts.items()
        }

        vector_length = math.sqrt(
            sum(value * value for value in vector.values())
        )

        document_vectors.append(
            {
                token: value / vector_length
                for token, value in vector.items()
            }
        )

    return inverse_document_frequency, document_vectors


def query_tfidf_vector(query, inverse_document_frequency):
    token_counts = Counter(tokenize(query))

    vector = {
        token: (1 + math.log(count)) * inverse_document_frequency[token]
        for token, count in token_counts.items()
        if token in inverse_document_frequency
    }

    vector_length = math.sqrt(
        sum(value * value for value in vector.values())
    )

    if vector_length == 0:
        return {}

    return {
        token: value / vector_length
        for token, value in vector.items()
    }


def lexical_scores(query):
    query_vector = query_tfidf_vector(
        query,
        inverse_document_frequency,
    )

    return np.array(
        [
            sum(
                query_value * document_vector.get(token, 0)
                for token, query_value in query_vector.items()
            )
            for document_vector in lexical_document_vectors
        ]
    )


print("Loading model and data...")
model = SentenceTransformer(MODEL_NAME)

data = np.load(EMBEDDINGS_PATH, allow_pickle=True)
embeddings = data["embeddings"]
normalized_embeddings = normalize_matrix(embeddings)
metadata = json.loads(str(data["metadata"]))

with open(TREES_PATH, "r", encoding="utf-8") as file:
    tree_nodes = json.load(file)

nodes_by_wikiid = {
    node["wikiid"]: node
    for node in tree_nodes
}

print("Building lexical TF-IDF index...")
inverse_document_frequency, lexical_document_vectors = build_tfidf_index(
    tree_nodes
)

print(
    f"Ready. Hybrid ranking: "
    f"{SEMANTIC_WEIGHT:.0%} semantic, "
    f"{LEXICAL_WEIGHT:.0%} lexical."
)


@app.get("/search")
def search(q: str, top_k: int = 3):
    query_embedding = model.encode(q)
    normalized_query = normalize_vector(query_embedding)

    semantic_score_values = normalized_embeddings @ normalized_query
    lexical_score_values = lexical_scores(q)

    hybrid_score_values = (
        SEMANTIC_WEIGHT * semantic_score_values
        + LEXICAL_WEIGHT * lexical_score_values
    )

    ranked_indices = np.argsort(-hybrid_score_values)[:top_k]

    results = []

    for index in ranked_indices:
        wikiid = metadata[index]["wikiid"]
        node = nodes_by_wikiid[wikiid]

        results.append(
            {
                "score": float(hybrid_score_values[index]),
                **node,
            }
        )

    return {"query": q, "results": results}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "semantic_weight": SEMANTIC_WEIGHT,
        "lexical_weight": LEXICAL_WEIGHT,
    }