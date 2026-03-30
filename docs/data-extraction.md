# Data Extraction Guide

This project primarily uses official institutional Common Data Set sources. Use the school's local files in `College-Data/<School>/` when available and keep all extracted values source-backed.

## Core Rules

- Do not invent data.
- Prefer official CDS archive pages and institution-hosted PDFs.
- Do not read PDFs directly with the Read tool; use Python-based extraction instead.
- If a value is missing or extraction fails, verify against official web sources before using a manual override.
- If a time series looks unnaturally flat or overly round, treat it as suspicious and re-check it.

## Recommended Workflow

1. Start with the local-first pipeline in `cds_pipeline/`.
2. Inspect the generated `candidate.json` and `review.md` before making dataset changes.
3. Pull values from the official CDS first, then reconcile with official institutional web pages if the CDS is incomplete or machine-unreadable.
4. Patch all affected years for that school in one pass to avoid mixed-quality series.
5. Run consistency checks before considering the data complete.

See `docs/pdf-extraction-pipeline.md` for the current command flow.

## Common Extraction Techniques

### Admissions (`C1`)

- Search for gendered application/admit/enroll totals and sum them.
- Newer CDS files may place men/women values on one line for the current fall.

### Test Scores (`C9`)

- Prefer text extraction for SAT/ACT ranges.
- Treat test-optional gaps carefully; missing values are not always extraction bugs.

### Costs (`G1`)

- Extract tuition, required fees, and room/board separately when possible.
- Some schools publish a broader financial-aid cost-of-attendance figure that does not match CDS `G1`; keep definitions consistent within the dataset.
- Newer forms may say `Food and housing` instead of `Room and Board`.

### Demographics (`B2`)

- Use total undergraduate counts for race/ethnicity reconciliation.
- `Nonresident` / `Nonresident alien` usually maps to the `international` bucket.

### Residency (`F1`)

- Residency often requires calculation rather than direct counts:
  - `domestic = undergraduate - international`
  - `outOfState = round(domestic * outPct / 100)`
  - `inState = domestic - outOfState`

### Financial Aid (`H2`)

- Rows `J` and `K` are usually the fastest path to average aid package and average need-based grant.

## PDF Handling Notes

- Prefer the extractor cascade in `cds_pipeline/` over direct ad hoc parsing.
- Use `pypdf` for AcroForm fields and low-level PDF metadata.
- Use `PyMuPDF` for block-aware native-text extraction.
- Use `Docling` when layout recovery matters.
- Use OCR only when the PDF is scanned or text extraction is corrupted.
- Fillable forms can have empty-looking extracted tables while still exposing usable field values through form metadata.
- Newer PDFs may contain encoding artifacts; join lines and try alternate text patterns before falling back to web research.

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
- the PDF structure is unreadable after reasonable extraction attempts
- the official institutional web source clearly states the needed value

Document the reason in commit notes or task notes when a school needs this treatment.
