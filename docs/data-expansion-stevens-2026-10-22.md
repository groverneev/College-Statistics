# Stevens CDS expansion attempt — 2026-10-22

## Result

No additional CDS sources could be located for **2016-2017, 2017-2018, 2018-2019, 2019-2020, 2020-2021, or 2021-2022**. All six remain missing. No new years or values were published. This is a source-limited outcome, not a claim that these reports never existed.

The existing 2022-2023 through 2025-2026 records and profile were preserved byte-for-byte. `src/data/schools/stevens.json` SHA-256 before and after: `9192d54170dd9adb07b2c9bc9342f73e0148c66a0f753f6dd748d1526ebb7b62`.

## Sources and searches

1. [Official institutional research Facts and Figures](https://www.stevens.edu/office-of-institutional-research-and-effectiveness/facts-and-figures): the CDS section lists only 2022-2023, 2023-2024, 2024-2025, and 2025-2026. The older [page-right-nav URL](https://www.stevens.edu/page-right-nav/facts-and-figures) and indexed staging page show the same starting year. Web retrieval exposed this content; direct terminal retrieval returned HTTP 403.
2. The official page separately lists **2019-2020, 2020-2021, and 2021-2022 Fact Sheets**. These are not CDS forms and were not substituted for the missing CDS years. Prior-cohort or prior-aid-year figures inside a newer CDS likewise do not establish an older CDS-year record.
3. Direct searches used the institution's exact name plus `common data set` and each of the six requested years; PDF-specific searches were also made. Follow-up searches included `site:stevens.edu`, `CDS`, `CDS_2021`, and `CDS_2019`. No matching official missing-year form was found. Results for Wisconsin–Stevens Point, generic blank templates, credit default swaps, and unrelated colleges were rejected. Older third-party financial-aid/admission compilations had blank Stevens entries, not a downloadable Stevens form.
4. Wayback Machine (second pass, inventory obtained): CDX queries over `assets.stevens.edu/*` return only CDS files for 2022-2023 (three upload variants), 2023-2024 (three), 2024-2025 and 2025-2026; nothing for earlier years. CDX filters for `cds` / `common data` across `stevens.edu/*`, `web.stevens.edu/*` and `ir.stevens.edu/*` returned no CDS document (only unrelated hits). Wayback snapshots of the old IR pages (`/directory/office-institutional-research-and-effectiveness/fast-facts`, 2016-2022, and `/about-stevens/facts-statistics`, 2016-2022) link only to Institutional Fact Sheets (2019-2020, 2020-2021, 2021-2022) and never mention a Common Data Set. An earlier pass in this task could not reach CDX; that limitation no longer applies.
5. [College Transitions repository](https://www.collegetransitions.com/dataverse/common-data-set-repository): inspecting the actual Stevens row showed links only for 2025-26 through 2022-23. Its 2021-22 through 2017-18 cells are plain `CDS` text without hyperlinks. Search-result summaries misleadingly display all these labels as if each represented a file. Direct terminal retrieval returned HTTP 403. This repository did not supply an older source.
6. [National Test Prep Association archive](https://nationaltestprep.org/common-data-set-archive/): the Stevens row explicitly states `Not available: 2018-19, 2019-20, 2020-21, 2021-22`. Its coverage starts at 2018-19, so it provides no evidence about 2016-17 or 2017-18.

7. Other aggregators: [collegedata.fyi](https://www.collegedata.fyi/schools/stevens-institute-of-technology) hosts only 2022-23, 2023-24 and 2024-25 for Stevens. Two additional Stevens-hosted PDFs surfaced in search, `CDS_2024.pdf` (58 pages, 2024-2025 form, a variant of the existing 2024-2025 file) and `CDS-2025-2026-PDF_3.12_updated.pdf` (50 pages, a March update of the existing 2025-2026 file); neither is an older year and neither was used. A 2021 third-party demonstrated-interest compilation marks Stevens as having no CDS found.

The preexisting official PDF downloads for 2022-2023 through 2025-2026 remain in ignored `College-Data/stevens/`, with their original `sources.json` provenance. No missing-year source was downloaded, prepared, or assigned invented provenance.

## Extraction workflow and manual resolutions

Read `.claude/skills/add-college/SKILL.md`. As documented in the parent agent?s recovery instructions, Claude extraction was unavailable due to the preceding rate-limit failure and **no Claude call was retried**. The intended replacement was direct extraction by this agent followed by independent `scripts/cds/crosscheck.py` and image reconciliation. Because no source for any requested year was found, there was no valid input for either extraction pass: **direct extraction, crosscheck.py, compare, page-image reconciliation, and assembly were not run for missing years**. No replacement extraction is claimed to have occurred. No manual value resolutions or cited resolution pages exist for this attempt.

Registration was already present; no registration files were changed. Assembly was deliberately skipped because it would reprocess existing final files without any new verified year, contrary to the exact-preservation requirement.

## Validation and page check

- `python -I scripts/cds/validate.py stevens`: passed, **0 errors, 0 warnings**.
- `bun run validate`: passed, **100 school files valid** at the time of the check.
- `bun run typecheck`: passed.
- Compared the complete Stevens JSON bytes against a saved baseline: identical.
- Local port 3000 was unavailable. A sandboxed development-server attempt failed with `spawn EPERM`; an elevated attempt identified an existing shared server on port **3457** and exited without replacing it. That existing server was left running.
- `curl http://localhost:3457/stevens`: **HTTP 200**; saved response in ignored `College-Data/stevens/rendered-page.html`.
- Inspected server-rendered content: four year rows (2022-2023 through 2025-2026), admissions, early decision, SAT, financial aid, cost, enrollment, demographics, and admissions-factor sections contain data. Latest headlines match the school record: **10,499 applications, 5,321 admits, 50.7% acceptance, 1,104 enrolled, SAT 1370–1470, $88,974 total cost**. SAT values and headline admissions counts were checked against the existing 2025-2026 final extraction; no new extraction was performed. Curl confirms server-rendered content, not visual chart painting or browser interactivity.

## Scope and remaining limitations

Only this report and ignored Stevens working artifacts were created by this task. No school JSON was modified, no worktree was created, and no commit was made. Preexisting Boston College/Rutgers edits and concurrent UChicago/Colby work were left untouched.

There are no data-validation warnings. The remaining limitation is source availability: no Stevens-hosted, Wayback-archived, or aggregator copy of a 2016-2017 through 2021-2022 CDS was found, and Stevens appears not to have published CDS forms before 2022-2023. A future attempt can resume if an authentic missing-year CDS is supplied or an accessible archive capture is located; complete both extraction passes and page-image reconciliation before publishing it.
