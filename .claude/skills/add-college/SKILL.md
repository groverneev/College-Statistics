---
name: add-college
description: Add a college (or new CDS years for an existing one) to the site end to end - find Common Data Set files anywhere online, download them, extract values with two independent models, validate, and publish the school page. Use when the user says "add <college>", "add <college> data", or "update <college> with the new CDS".
---

# Add a college

Run the whole loop without stopping to ask. Stop and ask only when no CDS can be found for the school at all, or when the final validation still fails after three repair rounds.

All scripts live in `scripts/cds/`. Plain scripts run with `python -I`; `fetch.py` and `pages.py` need `uv run` (they declare their own dependencies). Raw files and working data go to `College-Data/<slug>/` (git-ignored).

## 1. Resolve

- Pick a slug: lowercase letters only, matching the existing style (`bowdoincollege`, `johnshopkins`, `uncchapelhill`).
- If `src/data/schools/<slug>.json` exists, only fill missing years and any newer CDS year.
- Target years: every CDS from 2016-2017 to the newest published, keyed by CDS year (`2024-2025`).

## 2. Find the files

Search in this order and stop per year once a file is found:
1. The school's institutional research / IR / "Common Data Set" page (web search `"<school>" "common data set"`). Fetch the page and collect every CDS link.
2. Direct file search: `"<school>" common data set 2019-2020 filetype:pdf`.
3. Wayback Machine for years the school removed: `https://web.archive.org/cdx/search/cdx?url=<ir-domain>/*&filter=mimetype:application/pdf&output=json&collapse=urlkey`, then `https://web.archive.org/web/<timestamp>id_/<url>`.
4. Mirrors (pass `--mirror <name>`): College Transitions CDS repository, then other aggregators.

Prefer PDF over XLSX when both exist. A file is the right one only if its cover or headers name the school and the CDS year.

## 3. Download

```
uv run scripts/cds/fetch.py <slug> <year> "<url>" [more urls] --name "<Official Name>" [--referer "<page that links it>"] [--mirror college_transitions]
```

- Some schools publish each CDS section as its own PDF (Amherst does). Pass the A, B, C, G and H section URLs in order; they are merged into one file.
- Always pass `--referer` with the page the links came from; bot walls (AWS WAF, Cloudflare) often let requests with a referer through.
- It tries urllib, then curl, then the Wayback Machine copy, rejects HTML pages, and records URLs and SHA-256 in `College-Data/<slug>/sources.json`. Drive and Box share links are resolved automatically.
- The year is the CDS year printed on the form, not the year in the page URL (Amherst's `/2024` page is the 2024-2025 CDS).

## 4. Prepare pages

```
uv run scripts/cds/pages.py College-Data/<slug>/<slug>-cds-<year>.pdf --render B1,B2,C1,C7,C9,C21,C22,G1,H2
```

This writes per-page text, PNGs for the listed sections, and `index.json` mapping sections to pages. Scanned pages are rendered automatically.

## 5. Extract twice, independently

For each year, in parallel:
- **Claude**: launch a general-purpose subagent whose prompt is the output of `python -I scripts/cds/prompt.py <slug> <year> --extractor claude`. It writes `College-Data/<slug>/extract/<year>.claude.json`. Run up to 4 subagents at once.
- **Codex** (a different model family, so its mistakes are not correlated): `python -I scripts/cds/crosscheck.py <slug> <year>` writes `<year>.codex.json`. Run it in the background while the Claude subagents work.

If Codex is unavailable, launch a second Claude subagent with `--extractor claude2` and compare against that instead.

## 6. Reconcile

```
python -I scripts/cds/compare.py <slug> <year> [--right claude2]
```

This writes `<year>.final.json` with the agreed values plus `conflicts` and `single_source`. For each one, look at the cited page image yourself (Read the PNG), decide, and record the decision:

```
python -I scripts/cds/resolve.py <slug> <year> --accept <path>... --reason "..."
python -I scripts/cds/resolve.py <slug> <year> --drop <path>... --reason "..."
python -I scripts/cds/resolve.py <slug> <year> --set <path>=<value> --page <n> --reason "..."
```

Common cases: drop admissions totals an extractor added up itself (the assembler sums gender rows plus `raw.C1.otherGender.*`); accept values under stale template headers ("Fall 2017" on a 2018-19 form) when they differ from the prior year's values.

## 7. Assemble and validate

```
python -I scripts/cds/assemble.py <slug> --name "<Official Name>"
python -I scripts/cds/validate.py <slug>
```

Assemble derives acceptance rate, yield, total cost, enrollment total, percent receiving aid (H2 D/A) and percent of need fully met (H2 H/D), and takes C7 factors from the newest year. For each validation error, go back to the page, fix the value in `<year>.final.json`, and re-run. Do up to three rounds. Treat warnings as prompts to re-check the page; leave the value if the page confirms it.

## 8. Register and check the page

```
python -I scripts/cds/register.py <slug> --color "#RRGGBB" --aliases "Short Name,Abbreviation"
npx tsc --noEmit
```

Run `npm ci` first if `node_modules` is missing. `next dev` re-adds a Next.js block to `AGENTS.md`; leave it alone.

Use the school's official primary color. Then start `npm run dev`, open `/<slug>` (or curl it if the browser preview is unavailable), and confirm every chart has data and the headline numbers match the newest `final.json`.

## 9. Report

Report the years published, the years missing and why, every value you resolved by hand (with page numbers), and any remaining warnings. Do not commit unless asked.

Known site conventions the validator will not catch: costs come from whatever year G1 prints (often the next year, or the current year when the next is "not available"); aid figures use the full-time undergraduate H2 column, and H2 row A often exceeds B1 because it counts a different term.

## Benchmark

To measure extraction accuracy against a school already on the site, extract one of its years and run `python -I scripts/cds/compare.py <slug> <year> --site claude`.
