# ApplianceIQ

A dryer-troubleshooting portfolio prototype: from repair data and retrieval experiments to a working Android app.

Describe a dryer symptom, retrieve relevant iFixit troubleshooting guides, and work through source-attributed checks. The project demonstrates data preparation, semantic search, evaluation, error analysis, and application integration. It is a focused learning project, not a finished multi-appliance repair service.

## What works

- Local sentence embeddings from `all-MiniLM-L6-v2` and cosine similarity.
- Hybrid ranking: 80% semantic similarity + 20% lexical TF-IDF similarity.
- Brand filtering: generic queries get generic guides; recognized brands allow generic and matching-brand guides.
- An Android interface with repair checks, original-source links, and saved search results.
- Electric, Gas, and "I'm not sure" choices when opening the general heating guide.

The model is pretrained; it was not trained or fine-tuned for this project. The app retrieves existing repair content rather than generating answers with an LLM.

## What the experiments showed

The dataset contains **18 troubleshooting guides**, selected from 59 wiki pages in a 100-result iFixit search snapshot.

| Evaluation | Semantic only: Top-1 | Hybrid: Top-1 |
| --- | ---: | ---: |
| 12 challenge cases used during hybrid selection | 67% | 75% |
| 12 subsequent validation cases | 83% | 100% |

These are small, manually labeled guide-retrieval tests. They do not measure repair success or prove general accuracy. The comparison scripts evaluate ranking before the later brand filter; current backend behavior has separate regression tests. Once a challenge set is used to select a method, it is no longer an untouched test set.

The useful story is the reasoning: simplifying embedding text improved the development results; harder queries exposed remaining errors; cause-text re-ranking did not help; lexical evidence improved the ranking. See the [evaluation summary](docs/evaluation.md) and [experiment reports](docs/README.md#experiment-records).

## Run or explore

1. Follow the [Windows setup guide](docs/setup.md) to start the backend and connect an Android phone.
2. Read the [architecture](docs/architecture.md) to understand the data and search flow.
3. Use the [demo script](docs/demo.md) for a short portfolio recording.
4. Consult the [repository map](docs/repository-map.md) for what each file is for and why it is kept.

```text
ApplianceIQ/
  README.md          Project introduction
  requirements.txt   Python environment snapshot
  backend/           FastAPI search and guide navigation
  android/           Kotlin / Jetpack Compose app
  data_pipeline/     Collection, processing, experiments, fixtures, tests
  docs/              Setup, design, evaluation, demo, and project records
```

## Current limits

Only dryers are covered. The API can still return a dryer guide for an unrelated or vague query: no validated abstention/domain-routing rule is deployed. Similarity scores are not confidence probabilities. Brand recognition uses a small fixed list. Type confirmation applies to the general heating router, not every directly retrieved heating guide. The app currently uses a local backend and development HTTP configuration; saved results can be stale and branch navigation requires a connection.

Future appliance expansion would need appliance context, new data review, and fresh evaluations. It is deliberately outside this portfolio milestone. The prototype has not established the correctness or safety of repairs across models.

## Source attribution

Repair records preserve iFixit page links and `CC BY-NC-SA 3.0` attribution. The app displays this source information. See [data provenance](docs/data-provenance.md) for the stored metadata and the distinction between third-party repair content and project code. No repository-wide software license has been selected.
