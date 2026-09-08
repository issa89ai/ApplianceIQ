# Retrieval Representation Experiment

## Goal

Improve ApplianceIQ's first troubleshooting-guide recommendation by testing how each guide is represented before semantic retrieval.

## Problem observed

The initial retrieval system embedded each guide using:

    title + description + possible-cause titles

On a 20-case labeled evaluation set, some first recommendations were wrong.

Examples:

- “the drum tumbles normally but the dryer never gets hot” returned `Dryer Squeaking` first; a heating guide was ranked third.
- “there is a high-pitched squeal every time the dryer runs” returned `Dryer Making Loud Noise` first; `Dryer Squeaking` was ranked second.
- “I smell hot plastic coming from the dryer” returned `Dryer Smells Like Gas` first; `Dryer Smells Like Burning` was ranked second.

## Hypothesis

Possible-cause titles may add unrelated terms to a guide-level embedding and distract retrieval from the technician's main symptom.

For example, the `Dryer Squeaking` guide includes cause titles about drum rollers, belts, and bearings. A heating query that mentions the drum can therefore be pulled toward the squeaking guide.

## Experimental setup

The experiment held the following constant:

- 18 processed dryer troubleshooting guides
- 20 human-labeled retrieval test cases
- `all-MiniLM-L6-v2` sentence-transformer model
- 384-dimensional embeddings
- cosine-similarity ranking

Only the text used to create each guide embedding changed.

## Representations tested

1. Full guide text — initial production baseline

       title + description + cause or branch titles

2. Symptom-focused text

       title + description

3. Weighted symptom text

       title + description + title + description + cause titles

## Results

| Representation | Top-1 accuracy | Top-3 accuracy | MRR |
|---|---:|---:|---:|
| Full guide text | 85% | 100% | 0.917 |
| Symptom-focused text | 100% | 100% | 1.000 |
| Weighted symptom text | 95% | 95% | 0.963 |

## Decision

Use symptom-focused text for production guide embeddings:

    title + description

The cause titles remain in the structured decision-tree data and continue to be shown to technicians after a guide is retrieved. They are excluded only from the guide-level embedding input.

After applying the change and rebuilding the production embeddings, the fixed 20-case evaluation produced:

    Top-1 accuracy: 20/20 (100%)
    Top-3 accuracy: 20/20 (100%)
    MRR: 1.000

The FastAPI backend was restarted and verified with the previously failing heating query. It now returns `Dryer Not Heating` as rank 1.

## Known limitations

- The evaluation set is still small and human-labeled.
- The current dataset covers dryers only.
- Out-of-scope appliance queries can still retrieve incorrect dryer guides.
- Similarity scores are not probabilities and should not be used alone as confidence thresholds.
- This project uses semantic retrieval with a pre-trained embedding model; the model was not fine-tuned on ApplianceIQ data.

## Reproducibility

Baseline evaluation:

    .\data_pipeline\venv\Scripts\python.exe data_pipeline\evaluate_retrieval.py

Representation comparison:

    .\data_pipeline\venv\Scripts\python.exe data_pipeline\compare_retrieval_representations.py

## Related files

- `data_pipeline/evaluation/dryer_retrieval_cases.json`
- `data_pipeline/evaluate_retrieval.py`
- `data_pipeline/compare_retrieval_representations.py`
- `data_pipeline/build_embeddings.py`

## Relevant Git commits

- `4db8958` — Measure retrieval ranking quality with MRR
- `685fc5c` — Separate retrieval evaluation data from code
- `202844b` — Expand retrieval evaluation with challenge cases
- `1906135` — Compare guide embedding representations
- `3bcf861` — Use symptom-focused guide embeddings
