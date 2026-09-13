# Out-of-Scope Rejection Baseline

## Goal

Measure whether a simple cosine-similarity threshold can prevent a dryer-only retrieval system from returning a dryer guide for other appliances.

## Data

- 20 labeled in-scope dryer queries from `data_pipeline/evaluation/dryer_retrieval_cases.json`.
- 12 labeled out-of-scope queries from `data_pipeline/evaluation/dryer_out_of_scope_cases.json`.
- The same production retrieval setup: `all-MiniLM-L6-v2`, symptom-focused guide embeddings, and cosine similarity.

Each out-of-scope query has the label `expected: reject`. The model is not given those labels while retrieving; they are used only to measure the rule afterward.

## Baseline rule

Accept a query as a dryer query only when its highest guide similarity score is at least a chosen threshold. Otherwise, reject it.

## Results

| Threshold | Valid dryer queries rejected | Out-of-scope queries incorrectly accepted | Overall correct |
| --- | ---: | ---: | ---: |
| 0.35 | 0 | 9 | 72% |
| 0.40 | 0 | 7 | 78% |
| 0.45 | 2 | 4 | 81% |
| 0.50 | 5 | 2 | 78% |
| 0.60 | 9 | 1 | 69% |
| 0.70 | 13 | 0 | 59% |

The best tested threshold was 0.45, but it still rejected 2 valid dryer queries and accepted 4 non-dryer queries.

## Why a threshold fails

The in-scope score range was 0.430 to 0.782. The out-of-scope range was 0.143 to 0.693, so the ranges overlap.

For example:

- Valid dryer query: `not warm at all after full cycle` scored 0.430.
- Out-of-scope query: `the washing machine does not spin during the cycle` scored 0.693 and incorrectly matched `Whirlpool Dryer Not Spinning`.
- Out-of-scope query: `my oven is not heating up` scored 0.572 and incorrectly matched `Electric Dryer Not Heating`.

The model correctly sees shared symptom language such as “not spinning” and “not heating,” but cosine similarity alone does not understand the product boundary required by this dryer-only application.

## Decision

Do not add a global similarity-threshold rejection rule to the app. It would make the experience worse for legitimate dryer cases while still allowing several wrong-appliance matches.

The next experiment should compare safer domain-routing approaches against this threshold baseline, using the same labeled evaluation data.

## Reproduce

From the project root:

```powershell
.\data_pipeline\venv\Scripts\python.exe data_pipeline\evaluate_out_of_scope_rejection.py
```

Relevant files:

- `data_pipeline/evaluate_out_of_scope_rejection.py`
- `data_pipeline/evaluation/dryer_out_of_scope_cases.json`
- `data_pipeline/evaluation/dryer_retrieval_cases.json`
