# Brand filtering policy

Current feature note. See also [dryer type selection](dryer-type-selection.md).

## Purpose

A technician who describes a dryer symptom without naming a brand should receive generic guides. Removing manufacturer names from source content would conceal its original applicability, so titles and repair content are preserved and each guide receives separate `brand` metadata.

## Implementation

`data_pipeline/build_dataset.py` detects six brands in guide titles: Samsung, Whirlpool, Kenmore, GE, Maytag, and LG. Generic guides have JSON `null` as their brand. The current dataset contains 10 generic and 8 brand-specific guides.

`backend/main.py` limits eligible search results:

| Query | Eligible guides |
| --- | --- |
| No recognized brand | Generic only |
| Recognized brand | Generic and that brand |
| D80 code | Generic and LG |

Eligible guides retain the existing 80% semantic / 20% lexical score. The filter does not guarantee a matching-brand guide ranks first. Electric and gas are dryer types, not brands; both remain eligible for generic queries.

The processed dataset change adds only brand metadata. Existing titles, descriptions, source attribution, and embeddings remain unchanged.

## Verification

Run from the repository root:

```powershell
.\data_pipeline\venv\Scripts\python.exe -m data_pipeline.test_brand_filter_policy
```

The user ran the three-case regression test successfully:

| Case | Returned brands |
| --- | --- |
| Generic heating | generic, generic, generic |
| Samsung heating | Samsung, generic, generic |
| D80 without brand | LG, generic, generic |

The test checks nonempty results and rejects disallowed brands. For the two specific fixtures it also checks the matching brand ranks first; this is a ranking regression expectation, not a general filtering guarantee. These three examples are limited coverage, not a measure of overall retrieval accuracy.

Live API checks produced the same brand patterns. The user also reported seeing Electric Dryer Not Heating with iFixit attribution on the Android app.

## Limits and follow-up

Brand detection currently uses a fixed list and word boundaries. Unknown brands fall back to generic results. Multiple-brand queries and conflicts between a named brand and D80 are not resolved: D80 currently takes precedence. Review these cases before broadening the policy.

The filter relies on accurate guide metadata. New sources and brands need metadata review. Generic labeling does not establish that every repair instruction applies to every dryer model. The Android flow should also confirm electric versus gas when that distinction is needed.

An earlier brand-score adjustment experiment passed all 11 cases even at zero adjustment. It did not establish a need for a scoring boost. The current change implements a product eligibility rule instead.
