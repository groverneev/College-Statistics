# Rochester data expansion — 2026-10-22

## Result and scope

Added four missing numeric leaves to `src/data/schools/rochester.json`, all for 2020–2021 admissions: men enrolled **643**, women enrolled **720**, enrolled total **1,363**, and yield **0.1962** (1,363 / existing 6,947 admitted, rounded to four decimals). These are actual additions; none of the audited empty admissions/test-score/cost/aid sections or absent years could be securely filled from the retrieved official CDS sections. No claim is made that the sparse-data audit is fully resolved.

Every pre-existing scalar value is preserved. A before/after leaf comparison found zero changed or removed values and exactly four additions. Used a narrow patch rather than `assemble.py`, which would rebuild other years/profile from incomplete extractions. Only the Rochester JSON, this report, and ignored Rochester working data were written. No commit or worktree was created.

## Sources and discovery

Current [official CDS index](https://www.rochester.edu/provost/university-data/data-insights-reporting/university-of-rochester-common-data-set/) was fetched and saved as `College-Data/rochester/current-index.html`; it currently links the latest CDS only. WordPress media search returned current files, not the missing historical sections.

Archived official index pages were fetched directly, saved locally, and their actual links inspected:

- [2019 official index capture](https://web.archive.org/web/20190911000000id_/http://www.rochester.edu/provost/?page_id=10452), saved `page2019.txt`: links A/B/D/E/G/I/J for 2018–2019; no C or H.
- [2020 official index capture](https://web.archive.org/web/20200611000000id_/https://www.rochester.edu/provost/about-institutional-research/university-of-rochester-common-data-set/), saved `index2020proper.html`: A/B/J updated to 2019–2020, D/E/G/I still 2018–2019; no C or H.
- [2021 official index capture](https://web.archive.org/web/20211211000000id_/https://www.rochester.edu/provost/about-institutional-research/university-of-rochester-common-data-set/), saved `index2021proper.html`: C/H updated to filenames 2020–2021, A/B/J still 2019–2020 and G still 2018–2019. This explicitly establishes that the index mixed vintages; the page's date alone cannot date every linked section.

Official source files reused from ignored working data, with the actual pages inspected:

- [2018–2019 A](https://web.archive.org/web/20190910212249id_/https://www.rochester.edu/provost/wp-content/uploads/2019/06/CDS-Section-A-18-19-for-website.pdf), [B](https://web.archive.org/web/20190910212251id_/https://www.rochester.edu/provost/wp-content/uploads/2019/06/CDS-Section-B-18-19-for-website-new.pdf), and [G](https://web.archive.org/web/20190910212257id_/https://www.rochester.edu/provost/wp-content/uploads/2019/06/CDS-Section-G-18-19-for-website.pdf), merged as `rochester-cds-2018-2019.pdf`, four pages; SHA-256 `28006614294f25e9850e4ef5170af5d76b4bfedb38bbfe17db63a91efb3238c2`.
- [2020–2021 C](https://web.archive.org/web/20211211143822id_/https://www.rochester.edu/provost/wp-content/uploads/2021/10/CDS_2020-2021-C.pdf) and [H](https://web.archive.org/web/20211211143833id_/https://www.rochester.edu/provost/wp-content/uploads/2021/10/CDS_2020-2021-H.pdf), merged as `rochester-cds-2020-2021.pdf`, six pages; SHA-256 `5df0d5162d43ff571b76c9fd71bddd4158a3068251cd650294cb7898ade9bb21`.

The [College Transitions repository](https://www.collegetransitions.com/dataverse/common-data-set-repository/) was inspected after official/archive searches. Its 2019–2020 [Drive file](https://drive.google.com/file/d/1pUCUxWCN2_yuiBdGcoRSMUW_fOXcK8TX/view) was downloaded with `fetch.py --mirror college_transitions --referer ...`. It is byte-identical to the pre-existing collegedata.fyi mirror: SHA-256 `30ae72bf6f747943181444266f82bf0026331c38686bed1ef4295bd8db0a2c2e`, 16 pages. It is a mixed-year compilation, not a securely dated complete 2019–2020 CDS. The repository supplies no Rochester links for 2018–2019, 2017–2018, or 2016–2017 in the inspected row. The 2020–2021 link is Drive ID `16J9bia3qPvc2MbIkdKEyC25CrdWU5Uer`; the already available official C/H sections were preferred.

Searches for official 2016–2017/2017–2018 CDS PDFs returned no usable University of Rochester source. An archived 2017 IR landing page was retrieved but provided no CDS link. Cached official-domain Wayback PDF inventory contains no CDS before 2018–2019. Broader CDX queries timed out; a narrower common-page query returned an empty list. Thus these are retrieval limitations, not proof that no earlier CDS ever existed. Several guessed missing C/H/G URLs returned 404. No guesses were used as data.

## Independent extraction and manual resolutions

Followed `.claude/skills/add-college/SKILL.md` with the parent agent?s documented recovery deviation: direct extraction plus a separate Codex `gpt-6.1-sol` agent, not Claude. No Claude calls were made because of the reported provider rate limit. Both passes are the same model family, so this does **not** provide the skill's preferred cross-family independence. The separate agent independently read text and page images before reconciliation. This used an independent agent rather than `crosscheck.py`'s external Codex invocation.

Reused per-page text/images/indexes, reran `uv run scripts/cds/pages.py ...2020-2021.pdf --render C1,H2`, and visually inspected the rendered pages. Page numbers below are 1-based merged PDF pages unless specified otherwise.

- **2020–2021 C1, p1 (standalone C p1):** blue heading explicitly says Fall 2020. The sole enrollment row reads “Full-time enrolled” with men 643, women 720, total 1,363. Both passes verified those cells. There is no separate part-time row; the published sole enrollment total is retained, with no invented part-time count. `compare.py --left direct --right independent` agreed on both gender counts; the independent structured extraction intentionally omitted totals for assembler derivation. Manually accepted the printed total via `resolve.py --accept admissions.enrolled` after image inspection. Yield is the normal derived ratio. The row's full-time scope is a source limitation of the enrollment count.
- **Mixed mirror C1 p5:** explicitly Fall 2020, so rejected for 2019–2020. Its counts match the official C page above; no extra 2019 admissions were published.
- **2018–2019 G1, p4 (standalone G p1), also mixed mirror p15:** image explicitly says Common Data Set 2018–2019, and G6 also says FY 2018–19. Tuition 55,040, fees 990, room/board 16,548 match existing 2018 data. Rejected carrying these costs into 2019–2020 or 2020–2021 just because later index pages link the same file.
- **Official 2020–2021 H2 p3, also mixed mirror p8:** image says Fall 2019, yet official index/filename label the H publication 2020–2021. Full-time undergraduate COMBINED column prints A=5,941, D=3,115, H=2,879. The continuation (official merged p4 / mirror p9) gives J=51,250 and K=47,250. These coincide with existing 2020 aid. The independent reviewer and direct review both rejected copying/reassigning them to 2019: prior-year reporting or stale headings cannot be resolved from these pages. Existing 2020 values were preserved as instructed; their vintage ambiguity remains flagged.
- **2018–2019 B1/B2 p2 (standalone B p1):** image confirms B1 all-undergraduate total 6,535 and B2 degree-seeking undergraduate total 6,348. The validator warning is a population difference, not an arithmetic error in copied categories; preserve both. No admission counts were inferred from B1 enrollment.

Extraction/reconciliation artifacts: `extract/2020-2021.direct.json`, `extract/2020-2021.independent.json`, `extract/2020-2021.final.json`; absence/ambiguity notes are also in `extract/2018-2019.independent.json` and `extract/2019-2020.independent.json`. All are ignored.

## Additions and remaining gaps by year

| CDS year | Added | Remaining target gaps and reason |
|---|---|---|
| 2016–2017 | None | Entire year absent; no verifiable official CDS located after official search, archived IR/index/inventory checks, and prescribed mirror inspection. |
| 2017–2018 | None | Entire year absent; same retrieval limitation. |
| 2018–2019 | None | Admissions/testScores/financialAid remain empty: official index lacks C/H; available A/B/G pages do not report these fields. |
| 2019–2020 | None | Admissions/testScores/costs/financialAid remain empty: official index omits C/H, stale G belongs to 2018–2019, and mirror C/H year conflicts prevent safe reassignment. |
| 2020–2021 | C1 enrolled total, men/women enrolled, derived yield | testScores and costs remain empty: official C has C1/C2/C3/C4/C7 only, no C9, and linked G is 2018–2019. Demographics also remains empty as before; retrieved official sections are C/H. |

No SAT composite was inferred from marginal percentiles. No missing percentage was treated as zero, and no existing year/profile was regenerated. All later years were preserved.

## Verification

- `python -I scripts/cds/compare.py rochester 2020-2021 --left direct --right independent`: two agreed fields, one single-source printed total; `resolve.py` accepted that total after page-image review, leaving zero conflicts/single-source fields.
- `python -I scripts/cds/validate.py rochester`: **0 errors, 1 warning** (2018 B2/B1 population difference described above).
- `bun run validate`: **100 school files valid** at check time.
- `bun run typecheck`: passed.
- Before/after flattened JSON preservation assertion: passed; exactly four new leaves, zero changed/deleted existing leaves.
- Local page `http://localhost:3457/rochester`: HTTP 200; collaborative browser opened it with the expected Rochester 2025–2026 page title. Both detailed browser snapshot attempts failed with `Preview automation snapshot timed out after 15000ms.` Server-rendered HTML was saved as ignored `page-after-expansion.html`; fallback content checks found the new 2020 enrolled/yield data and unchanged latest-year headline counts 21,609 applied, 9,056 admitted, 1,231 enrolled, 41.9% acceptance. Chart rendering could not be visually verified; existing sparse sections remain sparse and were not falsely populated.
- No registration or color changes were needed for this existing school. Concurrent changes to other schools were left untouched.
- Scoped `git diff --check` passed. Verification summary is saved as ignored `verification-expansion.json`.
