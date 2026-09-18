import json
import numpy as np
from sentence_transformers import SentenceTransformer

from compare_hybrid_retrieval import (
    MODEL_NAME,
    build_tfidf_documents,
    evaluate,
    print_result,
)

EMBEDDINGS_PATH = "data_pipeline/processed/dryer_embeddings.npz"
NODES_PATH = "data_pipeline/processed/dryer_decision_trees.json"
FINAL_CASES_PATH = (
    "data_pipeline/evaluation/dryer_retrieval_final_validation_cases.json"
)


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    final_cases = load_json(FINAL_CASES_PATH)
    nodes = load_json(NODES_PATH)

    data = np.load(EMBEDDINGS_PATH, allow_pickle=True)
    guide_embeddings = data["embeddings"]
    metadata = json.loads(str(data["metadata"]))

    print(f"Loading model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    print("Building lexical TF-IDF index...")
    idf, document_vectors = build_tfidf_documents(nodes)

    print("\n=== Final validation: semantic vs hybrid retrieval ===")
    print("These 12 cases were created after choosing the 20% hybrid setting.")

    for lexical_weight, label in [
        (0.00, "Current semantic-only system"),
        (0.20, "Hybrid candidate: 20% lexical"),
    ]:
        print("\n==============================")
        print(label)

        result = evaluate(
            final_cases,
            model,
            guide_embeddings,
            metadata,
            idf,
            document_vectors,
            lexical_weight,
        )

        print_result("Final validation cases", result)


if __name__ == "__main__":
    main()