# Targeted iFixit Search Coverage Check

## Goal

Determine whether targeted dryer symptom searches reveal additional iFixit wiki pages beyond the existing broad `dryer` search before downloading or embedding more data.

## Method

The project already contains 59 wiki-type results returned by the broad iFixit `dryer` search. On 2026-09-13, the public iFixit API was queried read-only with the following targeted phrases. Each returned wiki ID was compared with the existing 59 IDs.

| Targeted query | Wiki results returned | New wiki pages beyond broad search |
| --- | ---: | ---: |
| `dryer not heating` | 6 | 0 |
| `dryer not spinning` | 4 | 0 |
| `dryer will not start` | 0 | 0 |
| `dryer squeaking` | 1 | 0 |
| `dryer making loud noise` | 1 | 0 |
| `dryer smells` | 2 | 0 |

## Result

All targeted-search results were already present in the raw data collected from the broad `dryer` search. No files were downloaded and the retrieval dataset was not changed.

## Decision

Do not run targeted iFixit searches as a data-expansion strategy. They would duplicate current source pages without improving diagnosis coverage.

Future coverage expansion should use a deliberately reviewed new source or a different kind of source record, with licensing, provenance, data structure, duplication, and evaluation considered before ingestion.
