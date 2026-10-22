# WashU and UC Irvine data expansion, October 22, 2026

Audited all 100 school JSON files by year count and numeric fields per year. Colby (one year), Stevens (four), and Chicago (five) have the shortest histories; earlier expansion reports document their public-source limitations. Rochester has the lowest field density (32 fields/year), followed by WashU (32.7), UCLA (33), Boston College (33.25), and UC Santa Cruz (33.4). UC Irvine averages 33.56 fields/year. Selected WashU and UC Irvine because each has sparse records and an accessible official 2025-2026 CDS missing from the site.

- **Washington University in St. Louis:** nine to ten years; 294 to 341 numeric fields, adding **47**.
- **University of California, Irvine:** nine to ten years; 302 to 329 numeric fields, adding **27**.

Added two school-year records and **74 numeric fields** under `years`, including derived rates and totals and excluding profiles. Both schools now cover every target CDS year from **2016-2017 through 2025-2026**. No target years remain missing. No newer report was located in this source search.

All 18 existing year objects are unchanged. The other 98 school JSON files, including the pre-existing uncommitted Emory, Pittsburgh, Tufts, and Wake Forest expansions, are byte-identical to their starting snapshots.

## Sources and extraction

- WashU: [official 2025-2026 PDF](https://washu.edu/app/uploads/2026/06/2025-2026-WashU-CDS.pdf), 43 pages, 635,914 bytes; SHA-256 `6e31784a370ec0c61814a19c98b2eb360953705e1eea92921a59eff49373d8ee`. Located through a direct-file search after the university data pages were inaccessible. Princeton's [peer CDS index](https://ir.princeton.edu/other-university-data/common-data-set) also lists WashU 2025-2026, but its protected outbound link could not be resolved.
- UC Irvine: [official CDS archive](https://irap.uci.edu/institutional-research/data-hub/common-data-set/) links the [2025-2026 PDF](https://sites.uci.edu/irap/files/2026/05/2025-26-CDS-PDF-Upload.pdf) through its `diviElementLinkData` script. The report has 50 pages and 2,292,153 bytes; SHA-256 `a3e5ce1ae6f2117180ead8800b13e880a5c7ca3a418fb975371e00a53738b88d`.

Each report was independently extracted by Claude Sonnet 5.5 and the repository's `crosscheck.py` using Codex gpt-6.1-sol. WashU produced **65 agreed fields, zero conflicts, and zero single-source fields**. UC Irvine produced **41 agreed fields, zero conflicts, and three single-source fields**. The three UC Irvine totals were accepted after visual review as described below, leaving 44 reconciled extraction fields. Extraction counts include factors and raw aid inputs; published numeric counts include derived fields instead.

Raw PDFs, download manifests, page text, rendered page images, independent extractions, and reconciliations are retained in the gitignored `College-Data/washu/` and `College-Data/uci/` folders. Windows resolves the latter to the existing `College-Data/UCI/` directory. The baseline audit, snapshots, and HTTP-rendered page copies are in `College-Data/expansion-washu-uci-2026-10-22/`.

## Source-page decisions and omissions

Page numbers are 1-based PDF pages, including front matter. No values were estimated or carried forward from prior years.

### WashU 2025-2026

- **C1, page 7:** retained the printed residency-table totals **33,283 applications / 3,968 admissions / 1,961 enrolled**. Men are **15,251 / 1,874 / 906** and women **18,016 / 2,093 / 1,054**. The unknown-sex row reports **16 / 1 / 1** and is retained in raw extraction inputs. Totals include that row.
- **B1/B2, pages 2-3:** enrollment is **8,153 undergraduates / 7,781 graduate students / 15,934 total**. The rightmost total-undergraduate race column sums to **8,153**, including **850 international, 981 Hispanic/Latino, 727 Black, 3,174 White, 1,723 Asian, 7 American Indian/Alaska Native, 7 Native Hawaiian/Pacific Islander, 479 multiracial, and 205 unknown**.
- **C9, page 11:** SAT composite **1500 / 1530 / 1550**, EBRW **730 / 750 / 760**, math **760 / 780 / 790**, ACT composite **33 / 34 / 35**. Submission rates are **32% SAT / 29% ACT**.
- **C21/C22, page 15:** ED counts are **4,934 applications / 1,333 admissions** for Fall 2025. EA is offered, but no EA counts are printed; those fields remain absent.
- **G1, page 21:** the source explicitly identifies **2026-2027** costs: tuition **$71,310**, fees **$1,412**, combined food/housing **$24,272**. The assembler derives **$96,994** under the site's existing CDS-year convention.
- **H1/H2, pages 24-25:** visually confirmed **2025-2026 estimated** aid. Full-time-undergraduate A/D/H are **7,427 / 3,322 / 3,322**; average package **$79,052**, average need-based grant **$73,547**. Aid shares derive from D/A and H/D.
- **C7, page 9:** the Interview row is entirely blank. The schema and assembler require all 18 factor ratings for a new profile. The 17 reported ratings remain in the extraction evidence, while the site retains its explicitly dated **2022-2023** profile unchanged. No interview rating was invented or carried into a newer profile.

### UC Irvine 2025-2026

- **Manual reconciliation, C1 page 14:** used `resolve.py --accept` for `admissions.applied=124231`, `admissions.admitted=35964`, and `admissions.enrolled=6421`. These were single-source Codex fields. The page image explicitly prints **124,231 / 35,964 / 6,421** in the residency table's TOTAL column. They are source-reported totals, not extractor-computed sums.
- **C1, page 13:** men are **58,513 / 15,851 / 2,896** and women **65,718 / 20,113 / 3,525**. Enrolled counts include part-time students. Unknown-sex cells are blank, so no zeros were substituted. B1 prints 3,517 full-time first-year women versus C1's 3,516, and B2 prints 6,422 first-years versus C1's 6,421. Admissions use C1 without adjusting the source inconsistencies.
- **B1/B2, pages 5-6:** enrollment is **30,260 undergraduates / 7,008 graduate students / 37,268 total**. Race counts use the rightmost total-undergraduate column, which sums to **30,260**.
- **C7, page 16:** updated the complete profile to **2025-2026**. Extracurricular activities, talent/ability, volunteer work, and work experience change from important to **very important**; character/personal qualities changes from considered to **important**. The other 13 factor ratings are unchanged. Checked boxes were visually reviewed because text extraction does not preserve them.
- **C9, page 19:** all requested SAT/ACT cells are blank; `testScores` remains empty for the new year.
- **C21/C22, page 23:** ED and EA are both marked No and their count cells are blank. No early-admission counts were added.
- **G1, page 29:** **2026-2027** costs are marked unavailable, with an anticipated availability date of **07/01/2026**. All requested amounts are blank. `costs` remains empty for the new year; the earlier year's costs are not copied forward.
- **H1/H2, pages 32-33:** visually confirmed **2025-2026 estimated** aid. Full-time-undergraduate A/D/H are **29,596 / 14,997 / 2,477**; package **$28,526**, need-based grant **$25,734**. Retained H2's printed denominator despite its difference from B1 full-time enrollment.

Neither report supplies all-undergraduate residency headcounts. First-year admissions residency tables and F1 percentages were not substituted.

## Validation and existing issues

- Both new 2025-2026 year objects pass the repository's `check_shape` and `check_values` functions with **zero errors and zero warnings**.
- `python -I scripts/cds/validate.py uci`: **zero errors, zero warnings**.
- WashU's full-history validator reports **six pre-existing errors and nine pre-existing warnings**. Validation of the untouched baseline and updated file produces identical error and warning lists. Historical records were preserved under the add-college skill's instruction to fill only missing/new years.
- The six existing WashU errors are: 2016-2017 yield **0.3677** versus recomputed **0.3679**; B2/B1 population differences in 2016-2017 (**7,116 / 7,540**), 2017-2018 (**7,253 / 7,675**), 2018-2019 (**7,356 / 7,751**), and 2019-2020 (**7,404 / 7,822**); and 2022-2023 total cost **$79,760** versus component sum **$83,760**.
- The nine existing warnings are residency/enrollment population differences for 2016-2017 through 2019-2020, and race/enrollment population differences for 2020-2021 through 2024-2025. This batch introduces none.
- `bun run validate`: all **100 school files valid** against the Zod schema.
- `bun run typecheck`: passed.
- HTTP checks on the existing development server at port 3457: both school pages return **200**, have **2025-2026** titles, and display admissions rows and headline figures matching the final JSON. WashU HTML contains seven chart containers; UC Irvine contains six. UC Irvine shows N/A for latest-year SAT and explicitly dates its latest available cost to 2024-2025.
- Browser snapshot inspection failed twice with `Preview automation snapshot timed out after 15000ms.` The alternate browser tool reported `No browser is available`. Used the CDS skill's HTTP fallback. Interactive chart hydration and appearance were not verified; chart container counts alone do not establish those checks.
- Equality checks passed for all **18** previous year objects and all **98** other school files. `git diff --check` passed.

No application code, registrations, worktrees, or commits were created.
