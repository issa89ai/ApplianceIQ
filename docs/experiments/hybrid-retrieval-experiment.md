# Hybrid semantic and lexical retrieval experiment

## Question

Can lexical evidence improve guide ranking when semantic similarity underweights specific symptom words? This report records the historical comparison before brand filtering was added.

The semantic representation was already title + description using the local `all-MiniLM-L6-v2` encoder. The 12-case challenge exposed confusion between burning and gas smells, cold clothes and interrupted cycles, and noise versus a stationary drum.

## First experiment: cause-text semantic re-ranking

Retrieve five guides using symptom embeddings, then re-rank with similarity to detailed cause sections. Increasing cause influence reduced development Top-1 from 100% to 95%, 90%, and 85% across tested settings, while challenge Top-1 stayed at 67%. This method was rejected.

This finding does not mean cause text is useless. Its broad vocabulary was unhelpful for this semantic re-ranking setup; it remains useful as repair content and as lexical evidence.

## Second experiment: hybrid retrieval

The lexical index uses titles, descriptions, cause titles, detailed steps, and branch titles. Token counts are weighted with TF-IDF and normalized. The semantic and lexical similarities are combined:

```text
score = (1 - lexical_weight) * semantic_similarity
        + lexical_weight * lexical_similarity
```

| Lexical weight | Development Top-1 | Challenge Top-1 | Challenge Top-3 | Challenge MRR |
| --- | ---: | ---: | ---: | ---: |
| 0.00 | 100% | 67% | 92% | 0.799 |
| 0.10 | 100% | 67% | 92% | 0.799 |
| 0.20 | 100% | 75% | 100% | 0.861 |
| 0.30–0.50 | 100% | 75% | 100% | 0.861 |

Select 0.20, the smallest tested lexical weight achieving the improved result. The challenge set was used in this selection, so it became tuning data.

## Subsequent validation

Twelve additional manually authored queries were evaluated after choosing the weight.

| Method | Top-1 | Top-3 | MRR |
| --- | ---: | ---: | ---: |
| Semantic only | 83% | 100% | 0.889 |
| 80% semantic + 20% lexical | 100% | 100% | 1.000 |

These are small project-specific results, not proof of universal accuracy. No pretrained model weights were updated. The validation script evaluates guide ranking without the later brand filter.

## Integration

The backend loads existing symptom embeddings and builds the lexical index at startup. The chosen weights are 0.80 semantic and 0.20 lexical. API checks corrected the burning-rubber example, and the user confirmed the burning guide on the Android phone. Current product rules are documented separately under [features](../README.md#current-project).

## Reproduce

Run these historical experiments from the repository root:

```powershell
.\data_pipeline\venv\Scripts\python.exe data_pipeline\compare_cause_reranking.py
.\data_pipeline\venv\Scripts\python.exe data_pipeline\compare_hybrid_retrieval.py
.\data_pipeline\venv\Scripts\python.exe data_pipeline\evaluate_hybrid_final_validation.py
```

See [evaluation](../evaluation.md) for metric definitions and the distinction between ranking experiments and current backend regression tests.

