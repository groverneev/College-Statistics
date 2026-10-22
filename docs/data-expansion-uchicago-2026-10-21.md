# University of Chicago CDS expansion — 2026-10-21

## Result and scope

Added **2025-2026**, expanding UChicago from **4 to 5 CDS years** (2021-2022 through 2025-2026). The new year contains **36 published numeric fields**. Updated the admissions-factor profile to its 2025-2026 source; all **18 factor ratings** match the previous profile. All four pre-existing year objects remain exactly equal to the saved original and are unchanged in the git diff.

Only `src/data/schools/uchicago.json`, `College-Data/uchicago/` working artifacts, and this new note were edited. No global code, registration, other schools, or existing documentation was changed. No commits or worktrees were created. No Claude model was used. Global checks and development-server review remain with the parent task.

## Sources and discovery

- [Official Office of Institutional Analysis CDS page](https://data.uchicago.edu/common-data-set/) lists exactly five reports, from 2021-22 through 2025-26. A fresh HTML copy is saved as `College-Data/uchicago/research/official-common-data-set-resumed.html`; extracted links and the query log are in `research/discovery-summary.json`.
- [Official 2025-2026 PDF](https://data.uchicago.edu/files/2026/08/CDS_2025-2026_to_publish-1.pdf): 31 pages, 603,913 bytes, SHA-256 `492d2a3a1f9ad62cd207444d84b06ce8d83b4af4661efd5f8aadd526488cd58e`. Reused the prior run's successful `fetch.py` download, `sources.json`, and `pages.py` output, then verified the PDF signature and checksum. The file is `College-Data/uchicago/uchicago-cds-2025-2026.pdf`.
- Direct PDF searches were performed separately for the five missing years starting 2016 through 2020; none produced an authentic UChicago CDS. Searches also checked for 2026-2027; none was found, and the current official listing ends with 2025-2026.
- [Chicago Maroon, April 27, 2023](https://chicagomaroon.com/39053/news/university-releases-common-data-set-for-first-time-shedding-light-on-admissions-process/), reporting a university spokesperson's statement, identifies 2021-2022 as the first completed CDS and December 2022 as its publication date. Saved HTML: `research/maroon-first-cds.html`.
- Wayback CDX request for `data.uchicago.edu/*` with the PDF MIME filter returned an HTML **Internet Archive: Temporarily Offline** page, not archive results. That response is retained as `research/wayback-data-pdfs.json` despite its extension. A second CDX request for `voices.uchicago.edu/oi/*` timed out after 40,006 ms without receiving bytes. Archive retrieval therefore supplied no evidence for older years; it was not treated as proof that no archived copies exist.
- [College Transitions CDS repository](https://www.collegetransitions.com/dataverse/common-data-set-repository/): the UChicago row has no linked files for 2017-18, 2018-19, 2019-20, or 2020-21. Its current table does not include 2016-17. Saved HTML and parsed headers/row are `research/college-transitions.html` and `research/college-transitions-row.json`.
- [collegedata.fyi UChicago archive](https://www.collegedata.fyi/schools/uchicago) also lists five reports beginning in 2021. Aggregators were used for discovery only; published values came from the official PDF.

Remaining year gaps are **2016-2017, 2017-2018, 2018-2019, 2019-2020, and 2020-2021**. Evidence indicates that these predate UChicago's first published CDS. No values were invented, interpolated, or taken from an unrelated institution's report. No 2026-2027 CDS was located; costs labeled 2026-2027 inside the 2025-2026 report do not constitute a separate CDS year.

## Independent extraction and reconciliation

The current Codex agent wrote `extract/2025-2026.primary.json` from source text and rendered table images before reading the independent extraction file. The independent extractor ran through the repository's unmodified `crosscheck.py`, which explicitly selected **gpt-6.1-sol**. Its initial sandbox launch failed with access denied; the escalated retry succeeded and wrote `extract/2025-2026.codex.json` with 52 fields and eight source notes. There was no account-limit failure on this resumed run.

`compare.py uchicago 2025-2026 --left primary --right codex` reported **52 agreed fields, nine single-source fields, and zero value conflicts**. The primary extraction had used B2's populated degree-seeking-only race column. The independent extraction omitted it because `fields.py` requests the total-undergraduates column. After inspecting page 4, all nine single-source race fields were dropped with `resolve.py`; the rationale is recorded for each field in `extract/2025-2026.final.json`. Final status: **52 accepted source fields, zero unresolved single-source fields, zero conflicts**.

The 52 source fields comprise 28 directly published numeric fields, six raw derivation inputs, and 18 profile factors. `assemble.py`/`fields.py` produce eight additional numeric fields: three admissions totals, acceptance rate, yield, total cost, percent receiving aid, and percent of need fully met. The resulting year has 36 numeric leaves.

## Manual source-page decisions

Page numbers below are 1-based PDF pages and match the printed page numbers.

- **Year identification, pages 1, 3, 8, 10, 21, 24:** page 1 says 2025-2026 and names The University of Chicago. Many interior running headers incorrectly retain 2024-2025. B1 explicitly specifies October 15, 2025; C1/C9 specify Fall 2025; G1 specifies 2026-2027; H1/H2 selects 2025-2026 Estimated. Accepted the file as the official 2025-2026 CDS without overwriting the existing 2024-2025 year.
- **C1, page 8:** retained men applied/admitted/enrolled **19,929 / 1,169 / 1,042**, women **24,578 / 870 / 744**, and unknown sex **1,026 / 0 / 0** in the raw inputs. The assembler derives totals **45,533 / 2,039 / 1,786**, acceptance rate **0.0448**, and yield **0.8759**. No all-gender totals were falsely attributed to printed cells.
- **B1, page 3:** accepted the printed totals **7,453 undergraduates, 8,953 graduate students, 16,406 overall**.
- **B2, page 4:** dropped `demographics.byRace.international`, `hispanicLatino`, `blackAfricanAmerican`, `white`, `asian`, `americanIndianAlaskaNative`, `nativeHawaiianPacificIslander`, `twoOrMoreRaces`, and `unknown`. The rightmost all-undergraduate column is blank. The adjacent degree-seeking-only values **1,432 / 1,181 / 445 / 2,136 / 1,476 / 3 / 1 / 514 / 250**, respectively, sum to **7,438**, excluding B1's 15 non-degree students. These are retained in the primary extraction audit only, not published as all-undergraduate values. The new year's `byRace` is empty.
- **C7, pages 9-10:** inspected the checkmark columns visually. Very important: rigor, essay, recommendations, extracurricular activities, talent, character. Not considered: interview and applicant interest. The remaining ten tracked factors are considered. All 18 ratings match the previous profile, while source year/PDF now identify 2025-2026.
- **C9, page 11:** verified SAT composite **1500 / 1540 / 1560**, reading/writing **740 / 760 / 770**, math **760 / 780 / 790**, ACT composite **34 / 35 / 35**, SAT submission **57%**, and ACT submission **25%**. Scores were copied, not generated by adding sections.
- **C21-C22, pages 13-14:** early decision/action plans are offered, but ED application/admit counts are blank and EA counts are unreported. Omitted all four count fields; blanks were not converted to zero.
- **Residency, page 19:** F1 reports percentages, not all-undergraduate residency headcounts. Omitted the entire residency breakdown rather than deriving counts from percentages.
- **G1, page 21:** selected the **Undergraduates** column: tuition **$75,960**, required fees **$1,995**, food/housing **$21,414**. First-year fees are **$2,715** and were not used. These figures are explicitly for **2026-2027**; the site convention attaches G1's printed cost year to its CDS report. The derived three-component total is **$99,369**.
- **H2, pages 24-25:** selected **Full-time Undergrad (Incl. First-Year)**. Raw A/D/H are **7,496 / 2,510 / 2,510**, J is **$83,276**, and K is **$77,445**. Derived aid shares are **0.3348** and **1.0**. Page 24 marks these as **2025-2026 Estimated**. Preserved H2's printed 7,496 denominator despite its difference from B1's undergraduate population; did not replace it with 7,453 or 7,438.

## Validation and remaining caveats

Ran `python -I scripts/cds/assemble.py uchicago --name "University of Chicago"` and `python -I scripts/cds/validate.py uchicago`: **0 errors, 0 warnings**. An equality assertion against `research/published-before.json` confirmed that every existing year is preserved. Git diff confirms only a new 2025-2026 year and the two profile provenance fields changed in the school JSON.

Source caveats remain: stale interior year headers; estimated aid; different H2/B1 populations; blank all-undergraduate race and residency data; absent ED/EA counts; next-year G1 costs; unavailable Wayback responses. These are documented source limitations even though the validator emits no warnings. Parent will handle global schema/type checks and application review.
