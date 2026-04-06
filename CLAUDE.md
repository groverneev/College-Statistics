# College Statistics - Working Guide

> **WORKTREE:** Work directly in the main repository. Do not create git worktrees.

> **PDF HANDLING:** Do not read PDFs directly with the Read tool. Use Python extraction scripts or shell-based extraction instead.

> **DATA RULE:** Never invent data. If extraction is incomplete, verify against official institutional sources and keep definitions consistent within a school's time series. Moreover, feel free to conduct web searches if pdfs contain incomplete data.

> **DOCS:** Detailed reference material lives in:
> - `docs/data-extraction.md`
> - `docs/architecture.md`
> - `docs/pdf-extraction-pipeline.md`

> **DEPENDENCIES:** If extra local tooling is needed, tell the user exactly what to install instead of assuming it is available or trying to work around missing packages silently.

> **PATCH SIZE:** Prefer smaller, staged edits over sweeping all-at-once patches. Large multi-file changes may get rejected by the editing tool, so break them into focused chunks when implementing bigger features.

## Repo Purpose

This is a Next.js site for exploring Common Data Set trends across colleges. The repo contains:

- local source files in `College-Data/<School>/`
- extraction scripts in `scripts/`
- normalized datasets in `src/data/schools/`

## Add A New School

Use this checklist:

1. Run `python -m cds_pipeline extract <school-or-path>` and inspect `.cds_pipeline/<slug>/review.md`.
2. Export or finalize `src/data/schools/<slug>.json` with complete, source-backed data.
2. Register the school once in `src/data/schools/index.ts`.
3. Add the school color in `src/lib/types.ts`.
4. Add aliases in `src/components/SearchBar.tsx` if the school needs abbreviation support.
5. Update any user-facing hardcoded copy only if it is not already derived from the registry.
6. Update `README.md` only if the public-facing behavior or documented coverage changed.
7. Run `npm run build`.

## Data Quality Checks

Before finishing school data work:

- confirm values are source-backed
- check for suspiciously flat or overly round trends
- verify race/residency totals reconcile with undergraduate enrollment
- verify costs and admissions values look consistent year over year

## Verification Checklist

Run these after significant changes:

- `npm run build`
- verify the homepage still renders the expected schools
- verify at least one direct school route works
- verify search still finds schools and aliases

## Notes

- The shared school registry in `src/data/schools/index.ts` is the canonical source of truth for school ordering and route registration.
- Keep internal refactors behavior-preserving unless the task explicitly asks for product changes.
