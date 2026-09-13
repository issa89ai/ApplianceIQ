# Domain-Routing Held-Out Challenge

## Purpose

The appliance-word guard scored 100% on the first 32 labeled cases. That result could be misleading because every non-dryer example explicitly used an appliance word already included in the guard.

This follow-up creates a separate 10-case challenge set after the guard was defined. The guard is not edited before this evaluation.

## Guard under test

Reject only when a query contains one of these known terms: `refrigerator`, `freezer`, `dishwasher`, `oven`, `stove`, `washing machine`, `washer`, `microwave`, `air conditioner`, `water heater`, or `vacuum`. Otherwise accept it for dryer retrieval.

## Results

The guard achieved **4/10 (40%)** on the held-out challenge set.

| Query | Expected | Guard result | Interpretation |
| --- | --- | --- | --- |
| `my fridge is not getting cold` | reject | accepted | `fridge` was not in the term list. |
| `the ice maker stopped making ice` | reject | accepted | No explicit appliance term was recognized. |
| `my dish washer leaves water in the bottom` | reject | rejected | It matched `washer` as a substring, not because the guard understood `dish washer`. |
| `the cooktop burner will not ignite` | reject | accepted | `cooktop` was not recognized as a stove synonym. |
| `my range is not heating properly` | reject | accepted | `range` was not recognized as an oven/stove synonym. |
| `the AC is blowing warm air` | reject | accepted | `AC` was not recognized as an air-conditioner abbreviation. |
| `my tumble dryer runs but the clothes stay damp` | accept | accepted | Correct valid dryer case. |
| `dryer isnt heatng after a full cycle` | accept | accepted | Correct valid dryer case with informal spelling. |
| `my dryer has lint around the vent and takes too long` | accept | accepted | Correct valid dryer airflow case. |
| `the machine makes a loud bang during the cycle` | clarify | accepted | The appliance is unknown, so a clarification is safer than retrieval. |

## Conclusion

The earlier 100% score was not generalizable. A hand-written appliance-word list has brittle coverage: synonyms, abbreviations, missing context, and new appliance names cause failures.

Do not add this guard to the app as if it were comprehensive. The correct product behavior for an unidentified appliance is to ask the technician which appliance they are working on. A future multi-appliance version should use that explicit selection as structured context instead of trying to infer the appliance only from a short symptom sentence.

## Interview value

This is an example of avoiding metric overconfidence. The team first measured a promising baseline, then evaluated it on intentionally different held-out queries, found performance dropped from 100% to 40%, and documented the limitation instead of deploying it.

## Reproduce

```powershell
.\data_pipeline\venv\Scripts\python.exe data_pipeline\evaluate_domain_routing_challenges.py
```

Relevant files:

- `data_pipeline/evaluation/dryer_domain_routing_challenge_cases.json`
- `data_pipeline/evaluate_domain_routing_challenges.py`
