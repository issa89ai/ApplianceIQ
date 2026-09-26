# Data provenance and attribution

The stored snapshot contains 100 iFixit search results, 59 downloaded wiki JSON pages, and 18 processed troubleshooting guides. This describes the repository snapshot, not a claim about current iFixit search coverage.

Raw records live in `data_pipeline/raw/`; processed records and vectors live in `data_pipeline/processed/`. Cleaning adapts source text by extracting repair sections and removing selected markup, image/table syntax, and navigation phrases. Raw files are retained so transformations can be investigated.

Each processed guide stores provider, original page ID and URL, API URL, source modification timestamp, license label and URL, and `adapted_for_applianceiq`. The builder labels the repair content `CC BY-NC-SA 3.0`; the Android app displays the provider, license, and original-source link. Brand labels preserve source specificity instead of relabeling branded instructions as universally applicable.

Source-content attribution and software licensing are separate. This repository does not currently contain a software LICENSE file; no license choice has been invented during documentation cleanup. Before redistribution or commercial use, review the applicable source terms and choose an appropriate license for original project code. This page records the project's metadata, not a legal clearance.

Source fetch scripts make network requests and may change stored snapshots. They are not needed to run the existing demo. Consult the [dataset audit](experiments/dryer-dataset-audit.md) before changing the data and rebuild both processed content and embeddings when appropriate.
