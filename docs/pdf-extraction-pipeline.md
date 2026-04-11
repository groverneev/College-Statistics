# PDF Screenshot Prep Workflow

This repo now uses a Codex-first CDS ingestion workflow under `cds_pipeline/`.

The repo-side automation is intentionally narrow:

- discover CDS PDFs
- group them by year
- render every PDF page to PNG screenshots
- write a simple per-year manifest for Codex/subagent handoff

Codex then reads those screenshots and produces the structured year JSON used for the website.

## Default Recommendation

Use the prep step directly:

```bash
python -m cds_pipeline prepare <school-or-path>
```

`extract` remains as a backward-compatible alias, but it now performs the same render-only prep step.

Examples:

```bash
python -m cds_pipeline prepare tufts
python -m cds_pipeline extract tufts
python -m cds_pipeline validate .cds_pipeline/tufts/2024-2025/subagent-output.json
python -m cds_pipeline validate src/data/schools/tufts.json
```

## Workspace Output

The prep step writes artifacts to:

```text
.cds_pipeline/<school-slug>/
```

For each year it creates:

- `pages/`: rendered PNG screenshots in page order
- `manifest.json`: the year handoff packet for a Codex subagent

It also writes:

- `school_manifest.json`: summary of all year manifests for the school

## Per-Year Manifest Shape

Each year manifest includes:

- `school_slug`
- `school_name`
- `year`
- `source_pdfs`
- `page_count`
- `screenshot_paths`
- `screenshots`
- `subagent_prompt`
- `output_contract`

## Codex Handoff Model

Recommended operator flow:

1. Add new CDS PDFs to `College-Data/<School>/`.
2. Run `python -m cds_pipeline prepare <school-or-path>`.
3. Give one year's manifest and screenshots to one Codex subagent.
4. Have that subagent return strict JSON with `year`, `data`, and `notes`.
5. Merge the per-year outputs into `src/data/schools/<slug>.json`.
6. Run guardrails and site wiring checks before finishing.

## Validation

The lightweight validator is deterministic only. It checks:

- `acceptanceRate == admitted / applied`
- `yield == enrolled / admitted`
- `total enrollment == undergraduate + graduate`
- race totals are plausible against undergraduate enrollment
- residency totals are plausible against undergraduate enrollment
- `totalCOA == tuition + fees + roomAndBoard`

These checks are guardrails, not a second extraction pipeline.
