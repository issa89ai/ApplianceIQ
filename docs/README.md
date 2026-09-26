# Documentation

Start with the root [project overview](../README.md). This folder separates current instructions from historical experiments.

## Current project

| Document | Read it to… |
| --- | --- |
| [Setup](setup.md) | Run the backend, Android app, and checks |
| [Architecture](architecture.md) | Follow a query through embeddings, scores, filters, and the UI |
| [Evaluation](evaluation.md) | Understand the labels, metrics, results, and limitations |
| [Demo](demo.md) | Record a short demonstration and explain decisions |
| [Repository map](repository-map.md) | Find files and understand retention decisions |
| [Data provenance](data-provenance.md) | Understand the source snapshot and attribution |
| [Brand filtering](features/brand-filter-policy.md) | Review the deployed brand eligibility rule |
| [Dryer type selection](features/dryer-type-selection.md) | Review exact branch navigation and phone checks |

## Experiment records

These are historical investigations, not a claim that every method is deployed. Keep rejected methods: they demonstrate testing and judgment.

| Report | Outcome |
| --- | --- |
| [Embedding representation](experiments/retrieval-representation-experiment.md) | Adopted title + description for semantic embeddings |
| [Held-out dryer challenge](experiments/held-out-dryer-retrieval-challenge.md) | Exposed errors in the semantic baseline |
| [Hybrid retrieval and cause re-ranking](experiments/hybrid-retrieval-experiment.md) | Rejected cause re-ranking; adopted 20% lexical weight |
| [Out-of-scope threshold](experiments/out-of-scope-rejection-baseline.md) | Rejected score-only rejection |
| [Domain-routing baselines](experiments/domain-routing-baselines.md) | Explored rules and semantic intent descriptions |
| [Domain-routing challenge](experiments/domain-routing-held-out-challenge.md) | Word guard failed to generalize; not deployed |
| [Dataset audit](experiments/dryer-dataset-audit.md) | Checked source coverage and metadata |
| [Targeted source search](experiments/targeted-ifixit-search-coverage.md) | No new pages in the recorded search |
| [Brand adjustment](experiments/brand-ranking-experiment.md) | No measured gain on the small fixture set; not deployed |
