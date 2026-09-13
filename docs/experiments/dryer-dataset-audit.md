# Dryer Dataset Audit

## Question

Before collecting more data, determine whether the current retrieval dataset lost eligible source pages during ingestion and whether its records have the minimum provenance fields needed for a source-aware prototype.

## Data flow audited

1. iFixit search for `dryer` returned 100 results.
2. 59 wiki-type results were fetched as raw JSON files.
3. 18 raw pages were marked `is_troubleshooting` by iFixit.
4. The dataset builder converted those pages into retrieval nodes.

## Results

| Check | Result |
| --- | ---: |
| Raw iFixit wiki files | 59 |
| iFixit troubleshooting pages | 18 |
| Processed retrieval nodes | 18 |
| Leaf diagnosis pages | 17 |
| Router pages | 1 |
| Nodes without descriptions | 0 |
| Nodes without original-source URLs | 0 |
| Nodes without license metadata | 0 |

Every source page that iFixit itself marked as a troubleshooting page appears exactly once in the processed retrieval dataset.

The 17 leaf pages contain between 4 and 13 possible repair causes each, with an average of 8.0. The one router page is `Dryer Not Heating`, which links to gas- and electric-dryer branches.

## Interpretation

The current 18-guide coverage is limited, but the limitation is not caused by accidentally discarding eligible pages during processing. It comes from the narrow dryer search result set and from intentionally restricting the prototype to source pages classified as troubleshooting.

This is a good trade-off for the current prototype: retrieval candidates are structured diagnostic pages with original-source links and license metadata, rather than arbitrary repair content.

## Data-expansion rule

Future expansion should not simply add more pages. For each new source or search path, the project should first verify:

1. the source permits the intended non-commercial retrieval use;
2. the page is genuinely diagnostic or can be structured reliably;
3. provenance and licensing fields can be stored;
4. new coverage fills a known gap, rather than duplicating existing guides;
5. the retrieval evaluation set is expanded before declaring an improvement.

## Reproduce

```powershell
.\data_pipeline\venv\Scripts\python.exe data_pipeline\audit_dataset.py
```

Relevant files:

- `data_pipeline/audit_dataset.py`
- `data_pipeline/raw/search_dryer.json`
- `data_pipeline/raw/wikis/`
- `data_pipeline/processed/dryer_decision_trees.json`
