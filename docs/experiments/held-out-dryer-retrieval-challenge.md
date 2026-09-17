# Held-Out Dryer Retrieval Challenge

## Goal

Measure the production retriever on new realistic dryer descriptions that were not used in the earlier representation-selection experiment or the 20-case development evaluation.

The production setup was left unchanged:

- `all-MiniLM-L6-v2` local sentence-transformer;
- symptom-focused guide embeddings;
- cosine-similarity ranking across all 18 guides.

## Results

| Metric | Result |
| --- | ---: |
| Cases | 12 |
| Top-1 accuracy | 8/12 (67%) |
| Top-3 accuracy | 11/12 (92%) |
| MRR | 0.799 |

The lower Top-1 result compared with the 20-case development evaluation is expected and useful: it shows the original evaluation set was not sufficient to demonstrate generalization.

## Failure analysis

| Query | Top result | Correct guide rank | Interpretation |
| --- | --- | ---: | --- |
| `the clothes are still damp and cold when the cycle finishes` | Dryer Stops Mid Cycle | 2 | The model associated damp clothes with an incomplete cycle more strongly than the important “cold” heating signal. |
| `there is a burning rubber odor while the dryer operates` | Dryer Smells Like Gas | 2 | Both smell guides share broad safety-language meaning; “burning rubber” should favor the burning guide. |
| `my Kenmore dryer makes a noise but the drum does not move` | Dryer Making Loud Noise | 3 | The model over-weighted “noise” relative to the more diagnostic “drum does not move.” |
| `my electric dryer needs two cycles because the clothes stay wet` | Dryer Stops Mid Cycle | 4 | The model associated repeated cycles and wet clothes with a cycle issue rather than electric-dryer heating. |

## Interpretation

The retriever is useful for shortlist retrieval: 92% of these cases placed an acceptable guide in the top three. However, 67% Top-1 is not enough to present the first guide as a confident single diagnosis without a technician review step.

The application already supports moving through alternative checks and matching guides, which is appropriate for this uncertainty. The next retrieval improvement should be evaluated against this held-out challenge set, not only against the original development cases.

## Reproduce

```powershell
.\data_pipeline\venv\Scripts\python.exe data_pipeline\evaluate_retrieval_challenges.py
```

Relevant files:

- `data_pipeline/evaluation/dryer_retrieval_challenge_cases.json`
- `data_pipeline/evaluate_retrieval_challenges.py`
