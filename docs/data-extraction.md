# Data Extraction Guide

This project uses official institutional Common Data Set sources and a vision-first PDF pipeline. Use the school's local files in `College-Data/<School>/` when available and keep all extracted values source-backed.

## Core Rules

- Do not invent data.
- Prefer official CDS archive pages and institution-hosted PDFs.
- Do not read PDFs directly with the Read tool; use the pipeline or Python-based helpers.
- If a value is missing or extraction fails, verify against official web sources before using a manual override.
- If a time series looks unnaturally flat or overly round, treat it as suspicious and re-check it.

## Recommended Workflow

1. Run `python -m cds_pipeline extract <school-or-path>`.
2. Inspect `.cds_pipeline/<slug>/candidate.json` and `.cds_pipeline/<slug>/review.md`.
3. Check missing sections, low-confidence fields, and validation issues before exporting anything.
4. Reconcile unclear values against official institutional sources when the PDF or model result is incomplete.
5. Patch all affected years for that school in one pass to avoid mixed-quality series.

See `docs/pdf-extraction-pipeline.md` for the current command flow.

## What The Model Extracts

The current pipeline asks the vision model to find and extract fields from these CDS sections:

- `B1`: undergraduate and graduate enrollment
- `B2`: undergraduate race and ethnicity counts
- `C1`: applicants, admitted students, enrolled students
- `C9`: SAT and ACT submission rates and percentiles
- `F1`: residency counts or out-of-state percentage
- `G1`: tuition, fees, room and board, total cost
- `H2`: aid rates and average grant/package values

The model is constrained to strict JSON and section-specific field allowlists.

## Normalization Notes

After extraction, the normalizer:

- keeps the highest-confidence candidate per field
- records provenance in `field_meta`
- derives:
  - acceptance rate
  - yield
  - total enrollment
  - total cost of attendance
  - residency counts from out-of-state percentage when necessary
- applies guardrails to suppress implausible values

## Practical Extraction Notes

### Admissions (`C1`)

- The model should return total first-time, first-year applicants, admitted students, and enrolled students.
- Acceptance rate and yield are derived later.

### Test Scores (`C9`)

- The model should return visible SAT/ACT submission rates and percentile values only.
- SAT/ACT composite blocks are reconstructed after extraction.
- Invalid percentile ordering is suppressed by guardrails.

### Costs (`G1`)

- Keep tuition, required fees, and room/board separate when possible.
- `Food and housing` can map to `roomAndBoard`.
- `totalCOA` is re-derived from tuition + fees + roomAndBoard even if the PDF shows a total.

### Demographics (`B2`)

- Use total undergraduate counts for race/ethnicity reconciliation.
- `Nonresident` / `Nonresident alien` maps to `international`.

### Residency (`F1`)

- If direct in-state/out-of-state counts are not shown but out-of-state percentage is visible, residency may be derived as:
  - `domestic = undergraduate - international`
  - `outOfState = round(domestic * outPct)`
  - `inState = domestic - outOfState`

### Financial Aid (`H2`)

- The model should target first-year aid rates and average package/grant values only.

## Verification Checklist

For each updated year:

- `undergraduate + graduate == total`
- `sum(byRace) == undergraduate`
- `sum(byResidency) == undergraduate`
- costs look plausible and vary year over year
- acceptance rate and yield reconcile with applied/admitted/enrolled counts

## When To Use Manual Or Web Overrides

Use an official web-backed/manual override only when:

- the local CDS is missing the value
- the model could not find the needed section or field
- the PDF is too ambiguous to verify safely from the extracted candidate alone
- the official institutional web source clearly states the needed value

Document the reason in task notes or commit notes when a school needs this treatment.
