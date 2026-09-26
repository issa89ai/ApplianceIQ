# Repository map and retention decisions

The root is the project entry point. Put user-facing explanations under `docs`, Android code under `android`, API code under `backend`, and data/experiments under `data_pipeline`. No source data or experiments were deleted during this organization pass.

## Root folder

| Item | Needed? | Decision |
| --- | --- | --- |
| `README.md` | Yes | Main portfolio introduction; keep at root |
| `requirements.txt` | Yes | Existing Python package/version snapshot; keep at root |
| `.gitignore` | Yes | Exclude environments, caches, and local tools; keep at root |
| `android/` | Yes | App source, resources, Gradle wrapper and configuration |
| `backend/` | Yes | Search and guide-navigation API |
| `data_pipeline/` | Yes | Reproducible data work and experiments |
| `docs/` | Yes | Explanations, setup, evidence, and demonstration plan |
| `.git/` | Local Git infrastructure | Keep; do not move or manually clean |
| `.claude/` | Optional local tooling | Preserve locally and ignore in Git; not needed by the app |

There were no loose Word/PDF reports or other root documents in this checkout. The main missing root document was the README, now added. A future software license belongs at the root, but choosing one requires an explicit ownership/licensing decision.

## Documentation placement

| File | Why keep it / location |
| --- | --- |
| `docs/README.md` | Navigation index |
| `docs/setup.md` | Commands and troubleshooting in one place |
| `docs/architecture.md` | Data, scoring, API, and app explanation |
| `docs/evaluation.md` | Central metric definitions and results summary |
| `docs/demo.md` | Short recording script and interview talking points |
| `docs/data-provenance.md` | Source and attribution explanation |
| `docs/repository-map.md` | This file inventory and organization decisions |
| `docs/features/brand-filter-policy.md` | Current product behavior; moved out of experiments |
| `docs/features/dryer-type-selection.md` | Current product behavior; moved out of experiments |
| `docs/experiments/retrieval-representation-experiment.md` | Evidence for semantic text selection |
| `docs/experiments/held-out-dryer-retrieval-challenge.md` | Baseline failure analysis |
| `docs/experiments/hybrid-retrieval-experiment.md` | Cause re-ranking rejection and hybrid adoption; repaired malformed Markdown |
| `docs/experiments/out-of-scope-rejection-baseline.md` | Why a score threshold was rejected |
| `docs/experiments/domain-routing-baselines.md` | Candidate routing comparisons |
| `docs/experiments/domain-routing-held-out-challenge.md` | Why the initial word-guard result was misleading |
| `docs/experiments/dryer-dataset-audit.md` | Source coverage and field completeness |
| `docs/experiments/targeted-ifixit-search-coverage.md` | Historical search outcome, preventing duplicate effort |
| `docs/experiments/brand-ranking-experiment.md` | Context for the unused scoring experiment |

The summary documents link to detailed reports rather than replacing their evidence. Historical reports describe the system at the time; terms such as "production" in those reports mean the prototype's then-current backend.

## Backend and Android

`backend/main.py` is the current API. Its model/data load occurs at import time, so tests importing it also load the model.

| Android file / group | Role |
| --- | --- |
| `MainActivity.kt` | Search screen, diagnosis cards, and branch selection |
| `ApplianceIqApi.kt` | Retrofit API and local backend URL |
| `Models.kt` | API response data classes |
| `SearchCache.kt` | DataStore fallback for recent search responses |
| `ui/theme/`, `res/` | Theme, strings, icons, and Android resource files |
| `AndroidManifest.xml` | App declaration, internet access, development HTTP permission |
| Gradle files and wrapper | Required build configuration; do not move |
| `ExampleUnitTest.kt`, `ExampleInstrumentedTest.kt` | Optional generated smoke tests; retained, not counted as product coverage |
| `.idea/`, `.gradle/`, `.kotlin/`, `build/`, `local.properties` | Machine/generated state; keep local, exclude from portfolio commits |

An existing deletion of the tracked `android/.idea/.gitignore` was left untouched. The root ignore now covers Android Studio state; ignored files are not deleted. Local environments and caches can be large but are not project evidence.

## Data scripts

All paths below are relative to `data_pipeline/`. Scripts remain here to preserve existing imports and commands. The documentation provides logical grouping without a risky module reorganization.

| Script | Classification and decision |
| --- | --- |
| `fetch_ifixit.py` | Source collection; retain, optional network operation |
| `fetch_wiki_pages.py` | Source collection; retain, optional network operation |
| `analyze_wiki_pages.py` | Early source exploration; retain as research utility |
| `parse_page.py` | Early single-page parser demonstration; retain as historical utility, current builder has its own parser |
| `build_dataset.py` | Active data preparation; required for rebuilds |
| `build_embeddings.py` | Active vector generation; required after content/order changes |
| `audit_dataset.py` | Data inspection report; retain, not an assertion-based test suite |
| `search_symptoms.py` | Semantic-only command-line example; retain, not current hybrid backend |
| `evaluate_retrieval.py` | Semantic baseline development evaluation |
| `evaluate_retrieval_challenges.py` | Semantic challenge evaluation |
| `compare_retrieval_representations.py` | Historical text-representation comparison |
| `compare_cause_reranking.py` | Rejected semantic cause re-ranking experiment |
| `compare_hybrid_retrieval.py` | Hybrid comparison and helpers used by other experiments |
| `evaluate_hybrid_final_validation.py` | Subsequent 12-case hybrid/semantic comparison |
| `evaluate_out_of_scope_rejection.py` | Rejected similarity-threshold experiment |
| `evaluate_domain_routing.py` | Exploratory routing baselines |
| `evaluate_domain_routing_challenges.py` | Word-guard challenge evaluation |
| `evaluate_brand_aware_ranking.py` | Historical brand-score adjustment experiment, not deployed |
| `test_brand_filter_policy.py` | Current backend regression script; run as a module |
| `test_guide_branches.py` | Current backend unittest suite; run as a module |

Do not delete an experiment just because its hypothesis failed. It explains a decision and can be reproduced. Python requirements contain transitive dependencies as well as direct ones; keep the snapshot rather than pruning packages without a fresh-install check. Direct project imports include NumPy, sentence-transformers, FastAPI, Uvicorn, and requests.

## Data files

| Location | Decision |
| --- | --- |
| `raw/search_dryer.json` and `raw/wikis/*.json` | Retain the source snapshot for traceability |
| `processed/dryer_decision_trees.json` | Retain the generated guide data used by the backend |
| `processed/dryer_embeddings.npz` | Retain the small generated vector snapshot used by the backend |
| `evaluation/dryer_retrieval_cases.json` | 20 development labels |
| `evaluation/dryer_retrieval_challenge_cases.json` | 12 challenge labels, later used for method selection |
| `evaluation/dryer_retrieval_final_validation_cases.json` | 12 subsequent validation labels |
| `evaluation/dryer_out_of_scope_cases.json` | 12 unsupported-query labels |
| `evaluation/dryer_domain_routing_challenge_cases.json` | 10 routing challenge labels |
| `evaluation/dryer_brand_ranking_cases.json` | 11 brand-score experiment labels |
| `venv/`, `__pycache__/` | Local runtime/cache; ignored, not source artifacts |

Embedding files are binary NumPy data, not documents to format. Guide content and label files are retained with their original schema. A future data migration should update builders, indexes, tests, and documentation together.
