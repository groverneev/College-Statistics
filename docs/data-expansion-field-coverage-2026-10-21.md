# Expansion of colleges with sparse field coverage

Audited all 100 school JSON files on October 21, 2026. Ranked schools by numeric fields per existing CDS year, rather than year count alone. Numeric fields are leaves under `years`, including derived totals and rates; admissions-factor profiles are excluded.

The sparsest records were Texas A&M (24 fields/year), UC Merced (28), Ohio State (31.25), and Georgetown (31.5). This batch expands Texas A&M and UC Merced. Pre-existing Rochester and Swarthmore edits and their separate report were preserved.

| School | Years before | Years after | Numeric fields before | Numeric fields after |
| --- | ---: | ---: | ---: | ---: |
| Texas A&M University | 7 | 10 | 168 | 414 |
| University of California, Merced | 6 | 9 | 168 | 324 |

Each source year was extracted independently with Claude Sonnet 5.5 and Codex gpt-6.1-sol, compared with `scripts/cds/compare.py`, and reconciled before assembly. The parent Codex agent independently extracted Texas A&M 2016-2017. No values were estimated or carried between years. Source files, SHA-256 download manifests, page text/images, extraction evidence and resolutions remain in the git-ignored `College-Data/<slug>/` directories.

## Published years and sources

Texas A&M now covers every CDS year from **2016-2017 through 2025-2026**. UC Merced covers **2016-2017 through 2024-2025**. UC Merced 2025-2026 is linked by its official archive, but direct/original/migrated URL attempts returned HTTP 403 and no matching Wayback capture was found. College Transitions has no 2025-2026 file for Merced. Third-party summaries were not used to populate that year.

Official archive pages: [Texas A&M](https://abpa.tamu.edu/accountability-rankings/common-data-set.html), [UC Merced](https://cie.ucmerced.edu/archive/external-reporting).

| School | CDS year | Source | Retrieved via |
| --- | --- | --- | --- |
| Texas A&M University | 2016-2017 | [Official source](https://web.archive.org/web/20170520144106id_/http://dars.tamu.edu:80/Data-and-Reports/Student/files/CDS_2016-2017-Final.aspx) | direct |
| Texas A&M University | 2017-2018 | [Official source](https://web.archive.org/web/20180703051829id_/http://dars.tamu.edu:80/Student/files/CDS_2017-2018.aspx) | curl |
| Texas A&M University | 2018-2019 | [Official source](https://abpa.tamu.edu/getattachment/c18920a5-3bec-4914-9362-3ff05488fdae/CDS_2018-2019.pdf) | wayback |
| Texas A&M University | 2019-2020 | [Official source](https://abpa.tamu.edu/getattachment/34fa8576-484b-4e19-a03a-7541c5289761/2019-2020-Common-Dataset.pdf) | wayback |
| Texas A&M University | 2020-2021 | [Official source](https://abpa.tamu.edu/getattachment/799f3672-b951-4536-b5df-5417dfc284a3/CDS_2020-2021-fixed-20211005.pdf) | wayback |
| Texas A&M University | 2021-2022 | [Official source](https://abpa.tamu.edu/getattachment/be61a654-0a21-4766-abb2-723ac566712d/CDS_2021-2022.pdf) | wayback |
| Texas A&M University | 2022-2023 | [Official source](https://abpa.tamu.edu/getattachment/ecf37248-03d2-4ec3-b246-dc0e6cde9bb4/CDS_2022-2023a.pdf) | wayback |
| Texas A&M University | 2023-2024 | [Official source](https://abpa.tamu.edu/_files/_documents/common-data/texas-a-m-commondataset-2023-2024updated.pdf) | direct |
| Texas A&M University | 2024-2025 | [Official source](https://abpa.tamu.edu/getattachment/439f54fe-1105-48af-955a-405775f80872/CDS-2024-2025_TexasA-M.pdf) | wayback |
| Texas A&M University | 2025-2026 | [Official source](https://abpa.tamu.edu/_files/_documents/common-data/cds-pdf-2025-2026.pdf) | direct |
| University of California, Merced | 2016-2017 | [Official source](https://cie.ucmerced.edu/sites/g/files/ufvvjh616/f/documents/irds/cds_2016-2017.pdf) | wayback |
| University of California, Merced | 2017-2018 | [Official source](https://cie.ucmerced.edu/sites/g/files/ufvvjh616/f/documents/irds/cds_2017-2018.pdf) | wayback |
| University of California, Merced | 2018-2019 | [Official source](https://cie.ucmerced.edu/sites/g/files/ufvvjh616/f/documents/cds_2018-2019.pdf) | wayback |
| University of California, Merced | 2019-2020 | [Official source](https://cie.ucmerced.edu/sites/g/files/ufvvjh616/f/documents/irds/cds_2019-2020_ucm_rev_2020522.pdf) | wayback |
| University of California, Merced | 2020-2021 | [Official source](https://cie.ucmerced.edu/sites/cie.ucmerced.edu/files/page/documents/ucm_cds_2020-2021.xlsx) | wayback |
| University of California, Merced | 2021-2022 | [Official source](https://cie.ucmerced.edu/sites/cie.ucmerced.edu/files/page/documents/cds_2021-2022_ucm.xlsx) | wayback |
| University of California, Merced | 2022-2023 | [Official source](https://cie.ucmerced.edu/sites/cie.ucmerced.edu/files/page/documents/cds_2022-2023_uc_merced.xlsx) | wayback |
| University of California, Merced | 2023-2024 | [Official source](https://cie.ucmerced.edu/sites/cie.ucmerced.edu/files/page/documents/university_of_california_merced_02132024_0.xlsx) | wayback |
| University of California, Merced | 2024-2025 | [Official source](https://cie.ucmerced.edu/sites/cie.ucmerced.edu/files/page/documents/2024-2025_cds_uc_merced.xlsx) | wayback |

PDF page numbers below are 1-based, including covers. For XLSX sources, `page` in extraction records is the 1-based worksheet index, not a print page.

## Manual reconciliation

| School/year | Field | Decision |
| --- | --- | --- |
| Texas A&M University 2016-2017 | `admissions.applied` | drop. PDF page 6 prints gender rows only. Drop extractor-computed totals 35494/23594/10142; assembler derives all-gender totals from the verified men and women rows. |
| Texas A&M University 2016-2017 | `admissions.admitted` | drop. PDF page 6 prints gender rows only. Drop extractor-computed totals 35494/23594/10142; assembler derives all-gender totals from the verified men and women rows. |
| Texas A&M University 2016-2017 | `admissions.enrolled` | drop. PDF page 6 prints gender rows only. Drop extractor-computed totals 35494/23594/10142; assembler derives all-gender totals from the verified men and women rows. |
| Texas A&M University 2019-2020 | `testScores.sat.composite.p25` | drop. PDF page 9 SAT Composite row is visually blank. Values 1180/1390 exist only as hidden text under opaque PDF content and are not displayed in the source table. |
| Texas A&M University 2019-2020 | `testScores.sat.composite.p75` | drop. PDF page 9 SAT Composite row is visually blank. Values 1180/1390 exist only as hidden text under opaque PDF content and are not displayed in the source table. |
| Texas A&M University 2024-2025 | `admissions.applied` | accept. PDF page 12 C1 residency breakdown explicitly prints all-student TOTAL column: applied 54,905; admitted 31,472; enrolled 12,498. Verified visually; these are source totals, not extractor sums. |
| Texas A&M University 2024-2025 | `admissions.admitted` | accept. PDF page 12 C1 residency breakdown explicitly prints all-student TOTAL column: applied 54,905; admitted 31,472; enrolled 12,498. Verified visually; these are source totals, not extractor sums. |
| Texas A&M University 2024-2025 | `admissions.enrolled` | accept. PDF page 12 C1 residency breakdown explicitly prints all-student TOTAL column: applied 54,905; admitted 31,472; enrolled 12,498. Verified visually; these are source totals, not extractor sums. |
| Texas A&M University 2025-2026 | `admissions.applied` | accept. PDF page 14 C1 residency table explicitly prints all-student TOTAL column: applied 62,967; admitted 32,531; enrolled 12,484. Visually verified; these are printed totals, not extractor sums. |
| Texas A&M University 2025-2026 | `admissions.admitted` | accept. PDF page 14 C1 residency table explicitly prints all-student TOTAL column: applied 62,967; admitted 32,531; enrolled 12,484. Visually verified; these are printed totals, not extractor sums. |
| Texas A&M University 2025-2026 | `admissions.enrolled` | accept. PDF page 14 C1 residency table explicitly prints all-student TOTAL column: applied 62,967; admitted 32,531; enrolled 12,484. Visually verified; these are printed totals, not extractor sums. |
| University of California, Merced 2020-2021 | `financialAid.averageAidPackage` | set = 23399. H2 full-time undergraduate column, worksheet CDS-H, displays whole dollars; visually confirmed in matching PDF page 22 ($23,399 and $21,127), not hidden cached decimals. |
| University of California, Merced 2020-2021 | `financialAid.averageNeedBasedGrant` | set = 21127. H2 full-time undergraduate column, worksheet CDS-H, displays whole dollars; visually confirmed in matching PDF page 22 ($23,399 and $21,127), not hidden cached decimals. |
| University of California, Merced 2020-2021 | `costs.roomAndBoard` | set = 18887. G5 explicitly prints Residents room and board total $18,887, verified visually on matching PDF page 18. Use the explicit combined G5 total; G1 misplaces same amount on Room Only row. |
| University of California, Merced 2021-2022 | `financialAid.averageAidPackage` | set = 26005. H2 full-time undergraduate column, worksheet CDS-H, displays whole dollars; visually confirmed in matching PDF page 24 ($26,005 and $23,290), not hidden cached decimals. |
| University of California, Merced 2021-2022 | `financialAid.averageNeedBasedGrant` | set = 23290. H2 full-time undergraduate column, worksheet CDS-H, displays whole dollars; visually confirmed in matching PDF page 24 ($26,005 and $23,290), not hidden cached decimals. |
| University of California, Merced 2021-2022 | `costs.roomAndBoard` | set = 19341. G5 explicitly prints Residents room and board total $19,341, verified visually on matching PDF page 20. Use explicit combined G5 total, not the mislabeled Room Only G1 cell. |
| University of California, Merced 2022-2023 | `financialAid.averageAidPackage` | set = 26464. H2 full-time undergraduate column uses whole-dollar currency format; visually confirmed matching PDF page 28 ($26,464 and $24,100). |
| University of California, Merced 2022-2023 | `financialAid.averageNeedBasedGrant` | set = 24100. H2 full-time undergraduate column uses whole-dollar currency format; visually confirmed matching PDF page 28 ($26,464 and $24,100). |
| University of California, Merced 2022-2023 | `costs.roomAndBoard` | set = 19341. G5 explicitly prints Residents room and board total $19,341, verified visually on matching PDF page 25 (stale 2021-22 header but 2023-24 cost year). Use explicit G5 combined total, not G1 Room Only cell. |
| University of California, Merced 2023-2024 | `costs.tuition` | set = 12260. CDS-G D27 value 12259.5 uses currency number format $#,##0, displaying $12,260. Preserve displayed whole-dollar amount. |
| University of California, Merced 2023-2024 | `financialAid.averageAidPackage` | set = 28191. CDS-H D83/D84 cached values 28190.961027 and 26033.284299 use $#,##0 format, displaying $28,191 and $26,033. Preserve displayed amounts. |
| University of California, Merced 2023-2024 | `financialAid.averageNeedBasedGrant` | set = 26033. CDS-H D83/D84 cached values 28190.961027 and 26033.284299 use $#,##0 format, displaying $28,191 and $26,033. Preserve displayed amounts. |

## Corrections to existing years

Re-extraction uses the undergraduate G1 column for costs and C1 full-time plus part-time enrollment for admissions. It also uses the latest located official revision of each report. The resulting numeric corrections are listed below. Rates/totals are recalculated from the verified components.

All three `demographics.byResidency` fields were removed from the seven existing Texas A&M years and six existing UC Merced years. These were estimated headcounts derived from F1 percentages, which are not source-reported all-undergraduate headcounts. Race-table international counts remain in `demographics.byRace.international`.

| School/year | Field | Before | After | Source location |
| --- | --- | ---: | ---: | --- |
| Texas A&M University 2018-2019 | `demographics.enrollment.undergraduate` | 53744 | 53743 | page/worksheet 3 |
| Texas A&M University 2020-2021 | `costs.tuition` | 9208 | omitted | source cell blank; omitted |
| Texas A&M University 2020-2021 | `costs.totalCOA` | 24578 | omitted | source cell blank; omitted |
| Texas A&M University 2023-2024 | `demographics.enrollment.total` | 76449 | 76633 | derived from verified components |
| Texas A&M University 2023-2024 | `demographics.enrollment.graduate` | 16516 | 16700 | page/worksheet 3 |
| Texas A&M University 2023-2024 | `costs.tuition` | 8665 | 8443 | page/worksheet 46 |
| Texas A&M University 2023-2024 | `costs.roomAndBoard` | 13081 | 13008 | page/worksheet 46 |
| Texas A&M University 2023-2024 | `costs.totalCOA` | 25716 | 25421 | derived from verified components |
| Texas A&M University 2024-2025 | `costs.tuition` | 8886 | 8958 | page/worksheet 27 |
| Texas A&M University 2024-2025 | `costs.totalCOA` | 25864 | 25936 | derived from verified components |
| University of California, Merced 2019-2020 | `admissions.applied` | 25368 | 25424 | derived from verified components |
| University of California, Merced 2019-2020 | `admissions.admitted` | 18263 | 18291 | derived from verified components |
| University of California, Merced 2019-2020 | `admissions.enrolled` | 2105 | 2107 | derived from verified components |
| University of California, Merced 2019-2020 | `admissions.acceptanceRate` | 0.7199 | 0.7194 | derived from verified components |
| University of California, Merced 2019-2020 | `admissions.yield` | 0.1153 | 0.1152 | derived from verified components |
| University of California, Merced 2019-2020 | `costs.tuition` | 11994 | 11442 | page/worksheet 17 |
| University of California, Merced 2019-2020 | `costs.fees` | 2150 | 2096 | page/worksheet 17 |
| University of California, Merced 2019-2020 | `costs.totalCOA` | 32411 | 31805 | derived from verified components |
| University of California, Merced 2021-2022 | `demographics.enrollment.total` | 9093 | 9094 | page/worksheet 2 |
| University of California, Merced 2021-2022 | `demographics.enrollment.graduate` | 772 | 773 | page/worksheet 2 |
| University of California, Merced 2021-2022 | `costs.tuition` | 11928 | 11442 | page/worksheet 7 |
| University of California, Merced 2021-2022 | `costs.fees` | 2286 | 2238 | page/worksheet 7 |
| University of California, Merced 2021-2022 | `costs.totalCOA` | 33555 | 33021 | derived from verified components |
| University of California, Merced 2022-2023 | `admissions.enrolled` | 2393 | 2356 | derived from verified components |
| University of California, Merced 2022-2023 | `admissions.yield` | 0.0925 | 0.0911 | derived from verified components |
| University of California, Merced 2022-2023 | `costs.tuition` | 12522 | 11834 | page/worksheet 7 |
| University of California, Merced 2022-2023 | `costs.fees` | 1230 | 1166 | page/worksheet 7 |
| University of California, Merced 2022-2023 | `costs.totalCOA` | 33093 | 32341 | derived from verified components |
| University of California, Merced 2023-2024 | `costs.tuition` | 13146 | 12260 | page/worksheet 8 |
| University of California, Merced 2023-2024 | `costs.totalCOA` | 36941 | 36055 | derived from verified components |

## Remaining source limitations

- UC Merced 2017-2018 G1 and H2 are blank. Its SAT table is blank, while ACT is reported. UC Merced 2023-2024 C9 is blank; 2024-2025 C9, G1 and H2 are blank. Partial years are retained without inventing missing values.
- Both 2016-2017 reports use pre-redesign SAT Critical Reading, not Evidence-Based Reading and Writing. Critical Reading values are omitted because the schema has no matching field. Old SAT Math values are retained as printed.
- UC Merced 2021-2022 and 2022-2023 test scores describe small submitting groups (SAT 9%/8%, ACT 2%/2%). They are reported percentiles, not campus-wide estimates.
- UC Merced 2018-2019 reports 100% SAT submission (2,217 students) although B1 first-time freshmen total 2,209. Retained as printed.
- UC Merced 2019-2020 C1 still labels Fall 2018, but values differ from the prior report. The revised official 2019-2020 report is used as published. Some UC Merced 2022-2023 PDF headers still say 2021-2022, while G explicitly reports 2023-2024 costs; the canonical official workbook is used.
- UC Merced 2023-2024 C1 includes another gender: applied 1,110, admitted 988, enrolled 50. Its 2024-2025 C1 includes unknown gender: 1,397, 1,298, 81. These contribute to all-gender totals but cannot be represented in the site schema's men/women-only breakdown. The five validator warnings reflect these published extra categories.
- Texas A&M 2020-2021 G1 page 19 leaves undergraduate in-state/in-district tuition blank. Its $9,208 first-year tuition is not substituted, so undergraduate tuition and derived total cost are omitted for that edition.
- Texas A&M's tuition decrease warning is confirmed by the source images: the 2021-2022 CDS G1 page 18 prints $9,208 for undergraduates, while the 2022-2023 CDS G1 page 17 prints $8,443. These are retained as reported.
- Texas A&M C7 alumni relation is explicitly blank in older reports. The profile uses the complete 2024-2025 table. The 2025-2026 C7 page 16 leaves volunteer work, work experience, and applicant interest unchecked; the schema requires a complete profile, so its partial table does not replace 2024-2025. No factor level is invented for a blank cell.
- Texas A&M 2024-2025 H1 page 30 selects 2023-2024 Final aid, and 2025-2026 H1 page 32 selects 2024-2025 Final aid. Their H2 row A cohorts match the preceding fall's B1 degree-seeking full-time counts. The values are retained under the CDS edition, following the site's convention, with this reporting-period caveat. The 2021-2022 H1 checkbox selects 2020-2021 Final although H2 row A matches Fall 2021; preserve the printed values without inventing a replacement period.
- G1 usually reports the following academic year's costs. This update preserves the project's CDS-year convention and the cost year printed in each source. H1/H2 can use an earlier final aid cohort or a current estimated cohort; the extraction notes preserve those labels. Texas A&M 2016-2017, for example, selects 2015-2016 final aid.

## Validation

```text
texasam: ok (0 errors, 1 warnings)
  warn  2022-2023: tuition fell from 9208 to 8443
```

```text
ucmerced: ok (0 errors, 5 warnings)
  warn  2023-2024: men+women applied is 1110 short of total 30017
  warn  2023-2024: men+women admitted is 988 short of total 26595
  warn  2024-2025: men+women applied is 1397 short of total 31582
  warn  2024-2025: men+women admitted is 1298 short of total 28903
  warn  2024-2025: men+women enrolled is 81 short of total 2097
```

- `bun run validate`: all 100 school JSON files valid.
- `bun run typecheck`: passed.
- `git diff --check`: passed.
- Browser checks: Texas A&M's page uses 2025-2026 and displays 62,967 applications, 12,484 enrolled, SAT 1160-1390, 62,031 undergraduates and 80,808 total students, matching the reconciled data. UC Merced's page uses 2024-2025 and displays 31,582 applications, 2,097 enrolled, 8,372 undergraduates and 9,110 total students. Its cost/aid charts correctly stop at 2023-2024, where those fields last appear.
- Both local routes returned HTTP 200.
- Both pages contain six rendered chart containers and 17 chart marks (lines, areas and bars), with historical data in each chart section and no hydration-error message.
- No application code was changed. No commits were created.
