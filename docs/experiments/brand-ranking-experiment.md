# Brand-score adjustment experiment

## Question

Would adding a small brand bonus or penalty improve hybrid ranking for generic and brand-specific queries?

`evaluate_brand_aware_ranking.py` compares adjustments 0.00, 0.02, 0.05, 0.08, and 0.12 on 11 labeled queries in `dryer_brand_ranking_cases.json`. It is an exploratory scorer, not the current backend filter.

## Recorded result and decision

The recorded run returned 100% Top-1, 100% Top-3, MRR 1.000, and 100% top-result brand accuracy for every adjustment, including zero. The examples did not demonstrate a benefit from a brand score adjustment. They do not establish correctness for all brand-related queries.

The subsequent requirement was explicit eligibility: generic queries should not receive brand-specific guides. That became the [brand-filter policy](../features/brand-filter-policy.md), independent of whether an additive bonus improved these metrics.

## Reproduce and interpret

```powershell
.\data_pipeline\venv\Scripts\python.exe data_pipeline\evaluate_brand_aware_ranking.py
```

Run from the repository root. The historical experiment recognizes five brands and omits Maytag; its D80 detector uses substring matching. These are limitations of that experiment, not descriptions of the current backend implementation. Preserve it as evidence of the exploratory work, not as the definitive policy test. Use `python -m data_pipeline.test_brand_filter_policy` for the deployed filter's three regression cases.
