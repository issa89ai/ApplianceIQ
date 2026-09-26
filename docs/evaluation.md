# Evaluation and decisions

## What is measured

A labeled case contains a query and one or more acceptable guide titles. Labels are used for scoring, not provided to the embedding model. A title counts as correct if it matches the case's acceptable list.

- **Top-1:** fraction of queries whose first guide is acceptable.
- **Top-3:** fraction with an acceptable guide anywhere in the first three.
- **MRR:** mean of `1 / rank` for the first acceptable guide, or zero if absent.

For acceptable ranks 1, 2, and 4, Top-1 is 1/3, Top-3 is 2/3, and MRR is `(1 + 1/2 + 1/4) / 3 = 0.583`. These measure retrieval, not repair accuracy.

## Recorded progression

| Experiment / dataset | Top-1 | Top-3 | MRR | Decision |
| --- | ---: | ---: | ---: | --- |
| Full guide representation, 20 development cases | 85% | 100% | 0.917 | Compare a simpler representation |
| Title + description, same development cases | 100% | 100% | 1.000 | Adopt for semantic embeddings |
| Weighted symptom representation, same development cases | 95% | 95% | 0.963 | Not adopted |
| Semantic only, 12 new challenge cases | 67% | 92% | 0.799 | Investigate failure examples |
| 20% lexical hybrid, same challenge cases | 75% | 100% | 0.861 | Select as candidate |
| Semantic only, 12 subsequent validation cases | 83% | 100% | 0.889 | Validation baseline |
| 20% lexical hybrid, same validation cases | 100% | 100% | 1.000 | Integrate into backend |

The hybrid kept development results at 100%. Cause-text semantic re-ranking reduced development Top-1 without improving challenge Top-1 and was rejected. Full details: [representation](experiments/retrieval-representation-experiment.md), [challenge](experiments/held-out-dryer-retrieval-challenge.md), and [hybrid](experiments/hybrid-retrieval-experiment.md).

The 12 challenge cases became tuning data when they were used to compare hybrid weights. The subsequent 12 cases were created after selecting 20%; they were manually authored within the project, not an independent benchmark. The results are useful evidence for this prototype but do not establish generalization across appliances, technicians, or new guide collections.

## Failed approaches are part of the evidence

The score-threshold rejection experiment found overlapping valid/invalid query scores. A known-appliance word guard scored 100% on its initial 32 cases, then only 40% on a 10-case challenge. Neither was integrated as a complete domain gate. The [brand-score experiment](experiments/brand-ranking-experiment.md) showed no gain over zero adjustment on 11 cases; the eventual brand filter was a separate eligibility policy.

## Reproduce ranking comparisons

From the repository root, using the existing environment and stored data:

```powershell
.\data_pipeline\venv\Scripts\python.exe data_pipeline\compare_retrieval_representations.py
.\data_pipeline\venv\Scripts\python.exe data_pipeline\compare_hybrid_retrieval.py
.\data_pipeline\venv\Scripts\python.exe data_pipeline\evaluate_hybrid_final_validation.py
```

These scripts calculate metrics; they do not fail automatically if a metric falls. The validation script compares semantic and hybrid ranking across all guides without the later backend brand filter. Do not describe its 100% result as an accuracy measurement of the entire current app.

## Product regressions and manual verification

```powershell
.\data_pipeline\venv\Scripts\python.exe -m data_pipeline.test_brand_filter_policy
.\data_pipeline\venv\Scripts\python.exe -m unittest data_pipeline.test_guide_branches
```

The brand script exercises three fixtures, including matching-brand-first expectations for the two named cases. The branch tests check exact electric/gas guide content and 404 rejection of invalid selections. Both return a failure exit code when their checks fail. Neither runs the Android UI.

The Android debug build passed, and the user confirmed live search, Electric/Gas navigation, I'm not sure, and source display on a physical phone. Android's `ExampleUnitTest` and `ExampleInstrumentedTest` are template smoke tests, not evidence of diagnosis-flow coverage.

## Remaining uncertainty

Fresh, broader evaluation would be needed for new data, revised filters, unknown brands, vague symptoms, and unsupported appliances. Current scores are not calibrated confidence. End-to-end repair outcomes and clinical-style safety claims have not been evaluated. The portfolio should emphasize the method, measured improvements, rejected ideas, and clear boundaries.
