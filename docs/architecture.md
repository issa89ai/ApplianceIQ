# Architecture

## Data preparation

```text
iFixit search snapshot (100 results)
  -> 59 wiki JSON pages
  -> 18 troubleshooting guides
  -> clean titles, descriptions, causes, steps, branches, source metadata
  -> title + description -> 384-dimensional guide embeddings
```

`build_dataset.py` reads stored pages, selects `is_troubleshooting`, extracts repair content, removes selected markup/navigation text, and adds brand and provenance fields. A leaf contains causes and steps; a router contains links to more specific guides. The current dataset has 17 leaves and one heating router. "Wiki" is the source API's content category.

`build_embeddings.py` encodes title plus description with `all-MiniLM-L6-v2`. It writes NumPy embeddings alongside guide IDs, titles, and types. The raw pages remain available for traceability; the builders do not run on every search.

## Search

At startup, FastAPI loads the model, embeddings, and processed guides. It builds a small lexical TF-IDF index once from titles, descriptions, cause titles, steps, and branch titles.

For each query:

1. Encode the query into a 384-number vector and normalize it.
2. Compare it with normalized guide vectors using cosine similarity.
3. Build a normalized TF-IDF query vector and calculate lexical similarity.
4. Combine scores: `0.80 * semantic + 0.20 * lexical`.
5. Keep guides allowed by the recognized query brand, then sort by combined score.
6. Return the requested top results with repair content and source metadata.

There is no vector database and no generated answer. With 18 guides, in-memory NumPy arrays are sufficient. Scores express similarity, not probability that a component is faulty. Brand eligibility is a deterministic product rule, separate from model similarity.

## Android flow

Kotlin / Jetpack Compose renders the result card. Retrofit and Gson handle HTTP responses. The app walks through causes in source order; cause order is not a learned diagnosis or probability ranking.

The general heating router offers Electric, Gas, and I'm not sure. A selection fetches the exact linked guide by ID; it does not run another semantic search. The user can return to the parent to change the choice. An uncertain user sees identification help and no selected repair steps.

Search responses are stored with DataStore for up to 20 normalized query strings. A failed search may show a saved response. This is not a complete offline guide library, and cached content has no freshness/version check.

## API surface

| Route | Purpose |
| --- | --- |
| `GET /health` | Status and ranking weights |
| `GET /search?q=...&top_k=3` | Ranked guide retrieval with brand filtering |
| `GET /guides/{wikiid}/branches/{branch_id}` | Exact child of a known parent; unrelated/missing IDs return 404 |

Branch responses use `score: 0.0` for compatibility with the Android model; it is not a calculated match score.

## Boundaries

The runtime uses repository-relative file paths, so start it from the root. Embedding and lexical rows depend on consistent data order. The query-brand rules recognize six names and D80, with known ambiguity limits documented in [brand filtering](features/brand-filter-policy.md). Type selection is restricted to router navigation, as documented in [dryer type selection](features/dryer-type-selection.md). The historical ranking scripts do not automatically test these later product rules.
