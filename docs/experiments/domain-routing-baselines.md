# Domain-Routing Baselines

## Goal

Before dryer-guide retrieval, decide whether a technician's message is within the current dryer-only scope. This experiment compares simple routing approaches using 20 labeled dryer queries and 12 labeled non-dryer queries.

An accepted query would continue to dryer-guide retrieval. A rejected query would receive a message such as: “This prototype currently supports clothes dryers only.”

## Methods

### 1. Require the word `dryer`

Accept only when the query literally contains `dryer`.

This is deliberately a weak lexical baseline. It protects the appliance boundary but cannot handle shorthand such as `clothes come out still wet` or `the drum isn't turning`.

### 2. Known non-dryer appliance-word guard

Reject a query that names one of the appliance categories not currently supported: refrigerator, freezer, dishwasher, oven, stove, washing machine, washer, microwave, air conditioner, water heater, or vacuum. Accept all other queries.

This is a transparent deterministic rule, not a machine-learning model.

### 3. Semantic dryer-intent prototype

Embed each question and compare it with three short descriptions of dryer repair problems using the same local `all-MiniLM-L6-v2` sentence-transformer model. Accept only when the best cosine similarity is above a chosen threshold.

This is an exploratory zero-shot semantic-routing baseline. It was not trained or fine-tuned on this project’s data.

## Results

| Method | Best observed result on 32 labeled cases | Key weakness |
| --- | --- | --- |
| Require `dryer` word | 69% correct | Rejected 10 valid dryer queries that did not name the appliance. |
| Known non-dryer appliance-word guard | 100% correct | The test examples explicitly contain listed appliance names; unknown names, typos, and symptom-only queries remain untested. |
| Semantic dryer-intent prototype | 81% correct at threshold 0.25 | Rejected 2 valid dryer queries and accepted 4 non-dryer queries. |

## Concrete examples

- `clothes come out still wet` is a valid dryer query, but the literal-word rule rejects it because it does not contain `dryer`.
- `the washing machine does not spin during the cycle` should be rejected. The semantic dryer-intent score was 0.458 because “does not spin” resembles dryer symptom language.
- `my oven is not heating up` should be rejected, but it shares the generic “not heating” symptom with dryer problems.

## Decision

Do not add the semantic prototype threshold to the app. It has the same fundamental issue as guide-score thresholding: generic symptoms can be shared by different appliances.

The known appliance-word guard is useful as a transparent short-term safety baseline, but it must be expanded and tested with more realistic data before deployment. It should not be presented as a learned model or as complete appliance classification.

## Next work

Build a larger routing evaluation set that includes:

- appliance synonyms, such as `fridge`;
- typos and informal technician language;
- non-dryer messages without an explicit appliance name;
- ambiguous messages that should trigger a clarification question rather than an automatic rejection.

## Reproduce

```powershell
.\data_pipeline\venv\Scripts\python.exe data_pipeline\evaluate_domain_routing.py
```

Relevant files:

- `data_pipeline/evaluate_domain_routing.py`
- `data_pipeline/evaluation/dryer_retrieval_cases.json`
- `data_pipeline/evaluation/dryer_out_of_scope_cases.json`
