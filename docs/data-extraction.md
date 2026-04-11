# Data Extraction Guide

This project uses official institutional Common Data Set sources and a Codex-first screenshot workflow. Use the school's local files in `College-Data/<School>/` when available and keep all extracted values source-backed.

## Core Rules

- Do not invent data.
- Prefer official CDS archive pages and institution-hosted PDFs.
- Do not read PDFs directly with the Read tool; use the screenshot prep command.
- If a value is missing or screenshots are ambiguous, verify against official web sources before using a manual override.
- If a time series looks unnaturally flat or overly round, treat it as suspicious and re-check it.

## Recommended Workflow

1. Run `python -m cds_pipeline prepare <school-or-path>`.
2. Inspect `.cds_pipeline/<slug>/school_manifest.json` and the per-year manifests.
3. Hand one year's screenshots to one Codex subagent and request strict `YearData` JSON plus notes.
4. Reconcile unclear values against official institutional sources when the screenshots are incomplete.
5. Merge all years into `src/data/schools/<slug>.json`.
6. Run the lightweight validator and site checks before wiring the school into the registry.

See `docs/pdf-extraction-pipeline.md` for the command flow.

## What Codex Should Extract

Per year, the subagent should build the existing `YearData` schema:

- admissions
- test scores
- demographics
- costs
- financial aid

The subagent may derive obvious schema values when the visible source values support them directly:

- acceptance rate
- yield
- total enrollment
- total cost of attendance

If an optional field is not visible, omit it. If a required field cannot be recovered safely, note that explicitly instead of guessing.

## Verification Checklist

For each updated year:

- `undergraduate + graduate == total`
- `sum(byRace)` is plausible against undergraduate enrollment
- `sum(byResidency)` is plausible against undergraduate enrollment
- costs look plausible and vary year over year
- acceptance rate and yield reconcile with applied/admitted/enrolled counts

## When To Use Manual Or Web Overrides

Use an official web-backed/manual override only when:

- the local CDS is missing the value
- the screenshots do not show the needed field clearly
- the PDF is too ambiguous to verify safely from the screenshots alone
- the official institutional web source clearly states the needed value
