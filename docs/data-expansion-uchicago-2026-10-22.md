# University of Chicago CDS source review — 2026-10-22

## Result and scope

No authentic University of Chicago CDS was located for **2016-2017, 2017-2018, 2018-2019, 2019-2020, or 2020-2021**. These years remain absent. Evidence indicates that 2021-2022 was the university's first CDS, rather than a missing run of previously published reports.

Used the requested fallback: added **16 missing reported fields to 2021-2022** in `src/data/schools/uchicago.json`. Every preexisting leaf value, all existing year keys, the profile, and the complete 2022-2023 through 2025-2026 records were preserved. No other school files were edited by this task. No worktrees or commits were created.

## Source discovery and evidence

- [Official CDS listing](https://data.uchicago.edu/common-data-set/), freshly retrieved with curl: links only 2021-22, 2022-23, 2023-24, 2024-25, and 2025-26. Saved to ignored `College-Data/UChicago/research2/official-2026-10-22.html`.
- Direct PDF searches were made separately for all five target years using `"University of Chicago" "common data set" "<year>" filetype:pdf`. No matching school-and-year report was found. Results from University of Illinois Chicago, Illinois Urbana-Champaign, DePaul, and other institutions were excluded.
- [Chicago Maroon, April 27, 2023](https://chicagomaroon.com/39053/news/university-releases-common-data-set-for-first-time-shedding-light-on-admissions-process/) reports the university's first CDS, identifies it as 2021-22, and reports publication in December 2022. It includes a university spokesperson's explanation of the change in reporting approach. This supports the absence of earlier CDS reports; it is not used as numerical extraction evidence.
- [Chicago Maroon, September 23, 2024](https://chicagomaroon.com/43910/data/three-years-later-what-have-we-learned-from-the-uchicago-common-data-set/) independently describes 2023-24 as the third released report.
- [Wayback PDF index for data.uchicago.edu](https://web.archive.org/cdx/search/cdx?url=data.uchicago.edu/*&filter=mimetype:application/pdf&output=json&collapse=urlkey), refreshed successfully: eight entries, with CDS URLs for 2021-22, 2022-23, 2023-24, and 2025-26, and no older CDS. Saved as `research2/wayback-2026-10-22.txt`. This is an archive coverage check, not proof of exhaustive archival coverage.
- The corresponding `voices.uchicago.edu/oi/*` archive request returned two unrelated `oishilab` PDFs, not CDS reports; saved as `research2/wayback-voices-2026-10-22.txt`. The broad prefix response does not establish complete coverage of the former institutional analysis site.
- [College Transitions repository](https://www.collegetransitions.com/dataverse/common-data-set-repository/), freshly retrieved: the UChicago row has the label “CDS” but **no hyperlink** in 2017-18, 2018-19, 2019-20, or 2020-21. The table does not cover 2016-17. Labels alone are not available sources. HTML and parsed row/headers are saved as `research2/college-transitions-2026-10-22.html` and `research2/mirror-evidence-2026-10-22.json`.
- Other mirror searches surfaced later reports (including 2021-22 on WPS and 2022-23 on collegedata.fyi), but no authentic missing-year source. No historical admissions profile or IPEDS figures were relabeled as a CDS.

## Official PDF and preparation

Numerical source: [University of Chicago CDS 2021-2022](https://data.uchicago.edu/files/2022/10/UChicago_CDS_2021-22.pdf), 28 pages. A fresh official download (`research2/official-2021-22-verified.pdf`) exactly matches the existing prepared source `uchicago-cds-2021-2022.pdf`:

`SHA-256 81ef9f18e3625d3f40542e85f0ff2cbff0ba95d4abd884392f1eb6b1c7a13fd8`

Reused the existing per-page text, section index, and rendered PNGs under `work/uchicago-cds-2021-2022/`. Parent agent visually inspected complete page images 7, 10, and 18. Page numbers below are 1-based PDF pages and match printed footers.

## Extraction deviation and reconciliation

Read `.claude/skills/add-college/SKILL.md`. **Claude was not retried.** Instead of its specified Claude/Codex model-family pair, the parent agent manually extracted the eligible missing fields from page text and images into `extract/2021-2022.primary.json` before reading the fresh independent output. Then `python -I scripts/cds/crosscheck.py uchicago 2021-2022 --timeout 300` ran a separate gpt-6.1-sol extraction, producing 57 fields in `2021-2022.codex.json`. This is independent extraction in separate context, but not different-model-family validation; correlated errors remain possible.

The initial sandboxed crosscheck failed with `Access is denied` while initializing the Codex runtime. The escalated rerun completed successfully. Network retrieval and PDF hashing likewise required escalation; no automatic approval rejection occurred.

`compare.py --left primary --right codex` found **16 agreements, zero numerical conflicts, and 41 single-source fields** outside the missing-field patch. Those 41 were explicitly dropped from this patch's final extraction using `resolve.py`, with a scope-preservation reason. “Dropped” here means excluded from the patch, not removed from the school JSON. The final extraction contains 16 agreed fields and no unresolved entries.

The assembler was deliberately not run: its full-year merge would replace existing values and recompute costs. A selective missing-leaf merge with assertions was used instead. Baseline is saved in ignored `research2/baseline-2026-10-22.json`.

## Added values and manual decisions

- **Page 7, C1:** men applied 17,513; admitted 1,254; enrolled 1,067. Women applied 20,445; admitted 1,206; enrolled 986. Part-time enrollment is explicitly zero for both, so the reported full-time counts also represent total enrolled by gender.
- **Page 10, C9:** SAT composite 25th/75th = 1510/1560; reading and writing = 740/780; math = 770/800. SAT submission rate = 49% (stored as 0.49).
- **Page 10, C9:** ACT composite 25th/75th = 33/35; submission rate = 35% (stored as 0.35).
- **Page 10:** no 50th percentile is reported; medians remain absent. ACT section scores have no matching supported schema field and were not added.
- **Page 7:** preserved the printed overall applications count of 37,974. Men plus women sum to 37,958, a difference of 16. The form explicitly permits totals to include students without gender data; no missing-gender count was fabricated or published. Admission and enrollment gender counts sum to the reported totals.
- **Pages 12-13, C21-C22:** early decision/action are offered, but application and admission counts are unreported. These remain absent; offering a plan does not establish a numeric count or zero.

## Warnings and limits

- **Preexisting fee discrepancy, visually confirmed on page 18, G1:** the JSON retains fees of $3,081 and totalCOA of $82,656. The PDF labels $3,081 as First-Year fees and $1,761 as Undergraduates fees. Applying the workflow's Undergraduates-column convention would yield $81,336 from tuition + fees + room/board. Neither existing value was changed because preservation was explicitly requested. G1 itself prints 2022-2023 costs in the 2021-2022 CDS.
- **Preexisting 2021-22 residency counts:** independent extraction omits them because F1, page 17, gives percentages rather than all-undergraduate residency headcounts. Existing values remain untouched and were not treated as newly verified reported headcounts.
- **2025-26 racial enrollment remains empty:** prepared B2 page 4 reports first-year and degree-seeking undergraduate counts; the requested total-undergraduates column is blank. It would be unsafe to silently substitute the degree-seeking column or carry forward another year. Its stale template header also requires care. No values were added there.
- No historical CDS file could be downloaded/prepared because no qualifying historical source was found. Archive/search absence cannot prove that no private or unindexed document exists.

## Checks

- Fresh official PDF hash matches the prepared source exactly.
- Programmatic preservation assertions: every old leaf value retained; year set unchanged; all four later year objects exactly equal to baseline; only 16 missing leaves added to 2021-2022.
- `python -I scripts/cds/validate.py uchicago`: **0 errors, 0 warnings**. The source-level cautions above are not detected by this validator.
- `bun run validate`: **100 school files valid** at check time.
- `bun run typecheck`: passed.
- `git diff --check` for owned files: passed.
- Existing dev server discovered on port 3457; used it without terminating another task's process. `curl http://localhost:3457/uchicago` returned **HTTP 200**. Saved response under ignored `research2/rendered-uchicago-2026-10-22.html`; it includes the added 2021-22 values and latest headline counts 45,533 applications, 2,039 admitted, and 1,786 enrolled, matching unchanged 2025-26 JSON.
- T3 preview navigation succeeded and reported the UChicago page title. Two snapshot attempts failed with `Preview automation snapshot timed out after 15000ms.` HTTP/content verification was used as the fallback; a visual chart review was not completed.

Tracked changes owned by this task are only the UChicago JSON and this report. Raw sources, refreshed discovery evidence, prepared pages, independent extraction, and reconciliation records remain under ignored `College-Data/UChicago/`. Preexisting Boston College/Rutgers edits and concurrent school work were not modified.

## Addendum: Sonnet 5.5 + Codex run on the same school

A second, concurrent run (Claude Sonnet 5.5 as the primary extractor, per the add-college skill) reached the same conclusion independently.

- **Sources re-checked:** the official CDS page still links only 2021-22 through 2025-26. A Wayback CDX query for `data.uchicago.edu/*` PDFs returned no CDS older than 2021-22. Two web searches for 2016-2020 UChicago CDS files found nothing and again pointed to the Chicago Maroon report that 2021-22 was the first CDS. No 2026-2027 CDS exists. Missing years: 2016-2017, 2017-2018, 2018-2019, 2019-2020, 2020-2021 (no published source).
- **2021-2022 extraction:** `scripts/cds/fetch.py` recorded the official PDF in `sources.json` (28 pages, SHA-256 `81ef9f18e3625d3f...`). The Sonnet 5.5 subagent wrote `extract/2021-2022.claude.json` (57 values) and `crosscheck.py` wrote `2021-2022.codex.json` (57 values, gpt-6.1-sol). `compare.py` reported **57 agreed, 0 single-source, 0 conflicts**, so nothing needed manual resolution. I checked C1 (page 7), C9 (page 10) and G1 (page 18) against the page text.
- **Merge:** I ran `assemble.py`, which recomputes whole years, then restored the three values it would have changed in the existing 2021-2022 record (`costs.fees` 3,081, `costs.totalCOA` 82,656 and `demographics.byResidency`). The only net change to the JSON is the 16 added 2021-2022 leaves (C1 gender rows and C9 SAT/ACT percentiles and submission rates), the same 16 the first run added. 2025-2026 was re-assembled byte-identically in value.
- **Checks:** `validate.py uchicago` reports 0 errors and 0 warnings. `bun run validate` reports 100 files valid, and `bun run typecheck` passes.
- **Warnings:** the fee and residency caveats above stand. In the 2021-22 G1, `$1,761` is the Undergraduates fee and `$3,081` is the First-Year fee. The existing JSON still holds the First-Year figure.
