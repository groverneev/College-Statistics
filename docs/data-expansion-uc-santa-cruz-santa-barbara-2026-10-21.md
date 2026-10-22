# UC Santa Cruz and UC Santa Barbara data expansion

Audited all 100 college records. The smallest histories were Colby (1 year), Stevens (4), Chicago (5), and Santa Cruz, Santa Barbara, Pomona and Virginia (6 each). Colby has no additional located CDS in the target period, as documented in the earlier expansion report; the current Stevens archive links only the four CDS years already present. This batch expands Santa Cruz and Santa Barbara, where all missing target years could be recovered.

Each school now covers every CDS year from **2016-2017 through 2025-2026**. Added 8 school-year records and **284 numeric fields**, including derived totals and rates. All pre-existing year objects, both original admissions-factor profiles, and the other 98 colleges are unchanged. No app code was changed. No worktree or commit was created.

| College | Years before | Years after | Numeric fields before | Numeric fields after |
| --- | ---: | ---: | ---: | ---: |
| University of California, Santa Cruz | 6 | 10 | 196 | 334 |
| University of California, Santa Barbara | 6 | 10 | 196 | 342 |

## Sources and extraction

Used `.claude/skills/add-college/SKILL.md`: downloaded with `fetch.py` and referer metadata, prepared page text/images with `pages.py`, extracted each report independently using Claude Sonnet 5.5 delegated tasks and Codex gpt-6.1-sol via `crosscheck.py`, compared with `compare.py`, and resolved every single-source value against rendered source pages before assembly. No differing numerical or factor values remained between the extractors; their differences were omissions and extractor-computed totals.

Raw reports, SHA-256 download manifests, page text/images, independent extractions and reconciliation records remain in the git-ignored `College-Data/<slug>/` folders. All covers/headers identify the correct school and CDS year. Existing C7 profiles already used 2025-2026; independently extracted factors matched them, so original profiles were preserved.

Official pages: [Santa Cruz public CDS files](https://mediafiles.ucsc.edu/iraps/common-data-set/common-data-set-2025-26.pdf), [Santa Barbara IR](https://bap.ucsb.edu/institutional-research), [Stevens facts and figures](https://www.stevens.edu/page-basic/facts-and-figures). Santa Barbara historical original URLs return 404; Wayback retained the official PDFs.

| College | Added CDS year | Source | Final extracted values |
| --- | --- | --- | ---: |
| ucsantacruz | 2016-2017 | [Official PDF](https://mediafiles.ucsc.edu/iraps/common-data-set/common-data-set-2016-17-revised.pdf) | 53 |
| ucsantacruz | 2017-2018 | [Official PDF](https://mediafiles.ucsc.edu/iraps/common-data-set/common-data-set-2017-18-revised.pdf) | 55 |
| ucsantacruz | 2018-2019 | [Official PDF](https://mediafiles.ucsc.edu/iraps/common-data-set/common-data-set-2018-19-revised.pdf) | 55 |
| ucsantacruz | 2025-2026 | [Official PDF](https://mediafiles.ucsc.edu/iraps/common-data-set/common-data-set-2025-26.pdf) | 42 |
| ucsb | 2016-2017 | [Official PDF via Wayback](https://web.archive.org/web/20200412102214id_/http://bap.ucsb.edu/institutional.research/common.data.set.2016.17.pdf) | 50 |
| ucsb | 2017-2018 | [Official PDF via Wayback](https://web.archive.org/web/20201111191555id_/http://bap.ucsb.edu/institutional.research/common.data.set.2017.18.pdf) | 52 |
| ucsb | 2018-2019 | [Official PDF via Wayback](https://web.archive.org/web/20201112035505id_/http://bap.ucsb.edu/institutional.research/common.data.set.2018.19.pdf) | 55 |
| ucsb | 2025-2026 | [Official PDF](https://drive.google.com/file/d/1FIkvY5dANho45ioG7-JHgO3IPH6-ui1W/view?usp=sharing) | 50 |

## Manual resolutions

PDF pages below are 1-based, including covers. Every resolved field is listed here. Accepted B2 race counts use the populated degree-seeking undergraduate column: the form explicitly reserves its optional rightmost column for schools unable to supply the first two columns, and B1 explicitly prints identical degree-seeking and total undergraduate populations. No non-degree population or unprinted counts were inferred.

| College / year | Field | Value / action | PDF page | Reason |
| --- | --- | --- | ---: | --- |
| ucsantacruz 2016-2017 | `admissions.applied` | Dropped extractor sum; assembler derives total | 6 | C1 prints gender rows, not overall totals. |
| ucsantacruz 2016-2017 | `admissions.admitted` | Dropped extractor sum; assembler derives total | 6 | C1 prints gender rows, not overall totals. |
| ucsantacruz 2016-2017 | `admissions.enrolled` | Dropped extractor sum; assembler derives total | 6 | C1 prints gender rows, not overall totals. |
| ucsantacruz 2017-2018 | `admissions.applied` | Dropped extractor sum; assembler derives total | 7 | C1 prints gender rows, not overall totals. |
| ucsantacruz 2017-2018 | `admissions.admitted` | Dropped extractor sum; assembler derives total | 7 | C1 prints gender rows, not overall totals. |
| ucsantacruz 2017-2018 | `admissions.enrolled` | Dropped extractor sum; assembler derives total | 7 | C1 prints gender rows, not overall totals. |
| ucsantacruz 2025-2026 | `admissions.applied` | 66374 | 13 | Printed C1 total in residency table. |
| ucsantacruz 2025-2026 | `admissions.admitted` | 48274 | 13 | Printed C1 total in residency table. |
| ucsantacruz 2025-2026 | `admissions.enrolled` | 4596 | 13 | Printed C1 total in residency table. |
| ucsb 2016-2017 | `demographics.byRace.international` | 1810 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2016-2017 | `demographics.byRace.hispanicLatino` | 5689 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2016-2017 | `demographics.byRace.blackAfricanAmerican` | 485 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2016-2017 | `demographics.byRace.white` | 7417 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2016-2017 | `demographics.byRace.asian` | 4443 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2016-2017 | `demographics.byRace.americanIndianAlaskaNative` | 37 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2016-2017 | `demographics.byRace.nativeHawaiianPacificIslander` | 81 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2016-2017 | `demographics.byRace.twoOrMoreRaces` | 1298 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2016-2017 | `demographics.byRace.unknown` | 314 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2016-2017 | `testScores.sat.math.p25` | 580 | 8 | Printed SAT Math; old scale retained, Critical Reading not mapped to EBRW. |
| ucsb 2016-2017 | `testScores.sat.math.p75` | 720 | 8 | Printed SAT Math; old scale retained, Critical Reading not mapped to EBRW. |
| ucsb 2017-2018 | `demographics.byRace.international` | 2185 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2017-2018 | `demographics.byRace.hispanicLatino` | 5957 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2017-2018 | `demographics.byRace.blackAfricanAmerican` | 548 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2017-2018 | `demographics.byRace.white` | 7331 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2017-2018 | `demographics.byRace.asian` | 4532 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2017-2018 | `demographics.byRace.americanIndianAlaskaNative` | 42 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2017-2018 | `demographics.byRace.nativeHawaiianPacificIslander` | 75 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2017-2018 | `demographics.byRace.twoOrMoreRaces` | 1317 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2017-2018 | `demographics.byRace.unknown` | 199 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2018-2019 | `demographics.byRace.international` | 2743 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2018-2019 | `demographics.byRace.hispanicLatino` | 6181 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2018-2019 | `demographics.byRace.blackAfricanAmerican` | 516 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2018-2019 | `demographics.byRace.white` | 7338 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2018-2019 | `demographics.byRace.asian` | 4671 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2018-2019 | `demographics.byRace.americanIndianAlaskaNative` | 44 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2018-2019 | `demographics.byRace.nativeHawaiianPacificIslander` | 60 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2018-2019 | `demographics.byRace.twoOrMoreRaces` | 1375 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2018-2019 | `demographics.byRace.unknown` | 142 | 3 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2025-2026 | `demographics.byRace.international` | 1963 | 4 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2025-2026 | `demographics.byRace.hispanicLatino` | 6630 | 4 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2025-2026 | `demographics.byRace.blackAfricanAmerican` | 377 | 4 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2025-2026 | `demographics.byRace.white` | 7235 | 4 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2025-2026 | `demographics.byRace.asian` | 4368 | 4 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2025-2026 | `demographics.byRace.americanIndianAlaskaNative` | 28 | 4 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2025-2026 | `demographics.byRace.nativeHawaiianPacificIslander` | 17 | 4 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2025-2026 | `demographics.byRace.twoOrMoreRaces` | 1879 | 4 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |
| ucsb 2025-2026 | `demographics.byRace.unknown` | 594 | 4 | Printed B2 degree-seeking counts equal B1 all-undergraduate population; optional total column blank. |

## Reporting caveats

- Santa Cruz 2025-2026 C9 (p18), G1 (p28), and H2 (p32) are blank. Test-score, cost, and aid fields remain absent; G1 marks 2026-2027 costs unavailable with an expected date of May 2026. Santa Barbara 2025-2026 C9 (p9) is also blank; test scores remain absent. No prior-year values were carried into those records. Historical chart data remains available.

- Santa Cruz 2025-2026 C1 (p12) prints enrolled men/women/unknown totals **2,081 / 2,370 / 145**, while its status rows sum to **2,046 / 2,351 / 199**. Used the explicit all-status gender totals; both distributions total **4,596**, confirmed by the printed total on p13. B2 (p5) prints 4,599 first-year students, a source discrepancy.

- Santa Barbara 2025-2026 C1 (p6) prints enrolled men/women/unknown totals **1,982 / 3,052 / 47**, while status rows sum to **1,978 / 3,056 / 47**. Used explicit gender totals. Both distributions total **5,081**, matching the printed residency-table total. B1 p3 full-time first-year men is 1,974, versus C1 status-row 1,973.

- Santa Cruz 2017-2018 C1 (p7) enrolled totals sum to **4,045**, while B1/B2 (pp2-3) report **4,047** first-year students. Santa Cruz 2018-2019 C1 (p7) full-/part-time rows sum to **3,701** enrolled, versus B1/B2 (pp2-3) **3,695**. Admissions uses C1; demographics uses B1/B2. Santa Barbara 2017-2018 B1 p3 prints first-time full-time men 1,897, versus C1 p6 1,896; 2018-2019 B1 p3 prints men/women full-time 2,199/2,868, versus C1 p7 2,205/2,862. These source differences were preserved.

- Santa Cruz and Santa Barbara 2016-2017 C9 report the old SAT. Math remains as printed (Santa Cruz p9: **540/660**; Santa Barbara p8: **580/720**). Critical Reading and Writing are not mapped to Evidence-Based Reading and Writing; no SAT composite was inferred. Old and redesigned Math percentiles are not directly interchangeable. No unprinted medians or composite scores were added.

- G1 follows the project CDS-year convention: the 2016-2017, 2017-2018 and 2018-2019 forms report the following academic year's costs (Santa Cruz pp16/17/18; Santa Barbara pp16/16/17). Santa Barbara 2025-2026 p18 reports **2026-2027** costs, using the continuing-undergraduate column: tuition **$13,368**, fees **$3,365**, food/housing **$23,974** (sum **$40,707**). First-year tuition $14,202 and fees $3,441 were not substituted.

- H2 uses the full-time undergraduate column. H1 marks the new historical reports and Santa Barbara 2025-2026 as estimated. Santa Barbara H2 row A differs from B1 by one in 2016-2017 (**21,199**, p18), while 2017-2018 H2 prints **21,776** (p18). Santa Cruz 2017-2018 H2 A prints **16,783** (p21), versus B1 degree-seeking full-time **17,082** (p2). Santa Barbara 2018-2019 H2 p19 still mentions Fall 2017, while H1 selects 2018-2019 estimated; retain the reported figures with this stale-template caveat. Aid percentages are H2 D/A and H/D, not H2 row I.

- First-year residency tables and F1 percentages were not treated as all-undergraduate residency headcounts. Neither school offers ED/EA in the added reports; blank early-plan counts remain absent.

## Validation and page checks

- `python -I scripts/cds/validate.py ucsantacruz ucsb`: zero errors. Remaining warnings are listed below.
- `bun run validate`: all 100 school files valid.
- `bun run typecheck`: passed.
- `git diff --check`: passed.
- Before/after assertions confirm every pre-existing year object and both profiles are unchanged, as are the other 98 colleges.
- The existing Next.js development server runs at `http://localhost:3457`. Both school pages returned HTTP 200. Their server-rendered HTML shows the 2016-2026 range, all ten admissions rows, and all five chart sections. Latest headline applications / acceptance / enrolled match the final data: Santa Cruz **66,374 / 72.7% / 4,596**; Santa Barbara **110,187 / 38.2% / 5,081**. Latest SAT headline is N/A for each. Each chart category has historical numeric data.
- Browser preview snapshots twice returned `Preview automation snapshot timed out after 15000ms.` Page verification used HTTP and rendered HTML; interactive chart appearance was not visually verified.

### Retained validator warnings

```text
ucsantacruz: ok (0 errors, 7 warnings)
  warn  2016-2017: men+women applied is 1632 short of total 49185
  warn  2016-2017: men+women admitted is 1078 short of total 28884
  warn  2016-2017: men+women enrolled is 138 short of total 4221
  warn  2025-2026: men+women applied is 2975 short of total 66374
  warn  2025-2026: men+women admitted is 2327 short of total 48274
  warn  2025-2026: men+women enrolled is 145 short of total 4596
  warn  2020-2021: tuition fell from 11994 to 11442
```

```text
ucsb: ok (0 errors, 4 warnings)
  warn  2025-2026: men+women admitted is 1521 short of total 42093
  warn  2018-2019: tuition fell from 12570 to 11442
  warn  2020-2021: tuition fell from 11994 to 11442
  warn  2025-2026: tuition fell from 14202 to 13368
```

The six Santa Cruz unknown-gender warnings and one Santa Barbara unknown-gender warning match the source C1 rows (Santa Cruz 2016-2017 p6 and 2025-2026 p12; Santa Barbara 2025-2026 p6). The schema exposes men/women only, while total counts include unknown gender. Santa Barbara tuition drops were rechecked against p16 (2017-2018: $12,570), p17 (2018-2019: $11,442), and p18 (2025-2026: $13,368). Both 2020-2021 tuition warnings predate this batch; those records were not changed.
