# Dryer type selection

## Problem and change

The generic Dryer Not Heating router previously displayed electric and gas branches as text. Its next-result button advanced through search rankings without confirming the dryer type.

The Android card now offers Electric and Gas buttons for this router. Each loads its exact linked guide through `GET /guides/{wikiid}/branches/{branch_id}`. The endpoint returns 404 for an unknown parent, an unrelated branch, or a missing child. The returned score is 0.0 because this is direct guide navigation, not a search score.

I'm not sure displays identification help without opening repair steps. Users can return from a selected guide and change their choice. Failed branch requests retain the choice screen and show a retry message. Branch loading requires the backend connection; selected branch content is not cached separately.

## Verification

- Android `assembleDebug` completed successfully.
- `python -m unittest data_pipeline.test_guide_branches` passed three tests: exact electric/gas guides with causes and attribution; rejection of an unrelated guide; rejection of an unknown parent.
- The user confirmed on the physical phone that Electric, Gas, and I'm not sure all worked as expected, including selected repair steps.
- Git whitespace checks passed.

Run the test from the repository root using the project virtual environment:

```powershell
.\data_pipeline\venv\Scripts\python.exe -m unittest data_pipeline.test_guide_branches
```

## Scope

This completes navigation from the general heating router. It does not require type confirmation for every directly ranked heating leaf or for brand-specific guides containing both types. Retrieval ranking is unchanged. A broader type-confirmation policy remains a separate task.
