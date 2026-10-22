# Emory and Pittsburgh data expansion, October 22, 2026

Audited all 100 school files by CDS-year count and numeric-field count. Colby (one year), Stevens (four), and Chicago (five) have the fewest years; earlier repository research documents their public-source limitations. Rochester, Boston College, Emory, Rutgers-New Brunswick, Pittsburgh, Washington, Davidson, and Syracuse each had eight years. This batch expands Emory and Pittsburgh using their newest official reports.

| School | Years before | Years after | Numeric fields before | Numeric fields after | Added |
| --- | ---: | ---: | ---: | ---: | ---: |
| Emory University | 8 | 9 | 282 | 329 | 47 |
| University of Pittsburgh | 8 | 9 | 336 | 369 | 33 |

Counts include numeric leaves under `years`, including derived totals and rates, and exclude admissions-factor profiles. Added **two school-year records and 80 numeric fields**. Both schools now cover **2017-2018 through 2025-2026**. Every pre-existing year object is exactly unchanged against Git HEAD. Both C7 profiles now cite 2025-2026; Pittsburgh's factor levels are unchanged. Emory's standardized-test factor changes from important to very important, and recommendations from very important to important, matching page 10 of the new report.

## Sources and independent extraction

- [Emory official archive](https://provost.emory.edu/planning-administration/data/common-data-set.html) links the [2025-2026 PDF](https://provost.emory.edu/planning-administration/_includes/documents/sections/institutional-data/emory-common-date-set-2025-2026.pdf). Downloaded 401,697 bytes, 31 pages; SHA-256 begins `35ef3959fe94f491`.
- [Pittsburgh official archive](https://www.ir.pitt.edu/university-information/common-data-set) links the [September 2025-2026 PDF](https://www.ir.pitt.edu/sites/default/files/2026-09/2025-2026%20Pittsburgh%20Common%20Data%20Set.pdf). Downloaded 1,562,759 bytes, 62 pages; SHA-256 begins `d63a8026a8f2bad4`.
- The indexed [February Pittsburgh PDF](https://www.ir.pitt.edu/sites/default/files/2026-02/CDS_2025-2026_PGH-UA_0.pdf) was incomplete: C9, G1, and H2 were unfilled. It was superseded before assembly. Its file, manifest, and initial extractions remain in `College-Data/universitypittsburgh/superseded-2026-02/`. Both independent extractions were repeated from the September source.

Claude Sonnet 5.5 and Codex gpt-6.1-sol extracted each final source independently. `compare.py` found **66 agreed source fields for Emory** and **46 for Pittsburgh**, with **zero conflicts and zero single-source fields**. No manual value overrides were needed. Raw derivation inputs and C7 factors account for the difference between these counts and published numeric leaves.

Official files, complete SHA-256 hashes, source manifests, extracted page text, rendered images, and extraction/comparison JSON remain under the gitignored `College-Data/emory/` and `College-Data/universitypittsburgh/` directories. The baseline audit and retrieval log are in `College-Data/sparse-expansion-2026-10-22/`.

## Source-page checks and limitations

Page references are 1-based PDF pages, including front matter. Decisions below describe source interpretation and intentional omissions, not changes to prior years.

### Emory 2025-2026

- **C1, page 8:** the residency table explicitly prints overall applications/admissions/enrollment of **37,561 / 3,869 / 1,443**. The gender rows give men **14,990 / 1,764 / 624**, women **22,566 / 2,105 / 819**, and unknown sex **5 / 0 / 0**. The five unknown-sex applications are retained in raw derivation inputs; the published totals include them. No residency headcounts were inferred for the entire undergraduate population from this first-year table.
- **C7, page 10:** visually checked the two changed factor ratings and the checkbox columns. The latest profile reflects the source's ratings.
- **C9, page 11:** SAT composite **1480 / 1510 / 1540**; SAT EBRW **720 / 740 / 760**; SAT math **740 / 780 / 790**; ACT composite **33 / 34 / 35**. Submission rates **47% / 21%**.
- **C21/C22, page 14:** ED applications/admissions **4,728 / 1,049**. No early action offered; absent EA counts were not replaced with zeros.
- **B1/B2, pages 1-2:** **7,320** undergraduates, **8,180** graduate students, **15,500** total. B2 uses the populated rightmost total-undergraduates column.
- **G1, page 21:** the source explicitly labels **2026-2027** costs: undergraduate tuition **$70,300**, fees **$1,148**, food and housing **$22,406**. They remain keyed to the CDS year under the site's existing convention; the assembler's three-component total is **$93,854**.
- **H1/H2, pages 24-25:** H1 selects **2025-2026 Estimated**. The full-time-undergraduate H2 column has A/D/H **7,128 / 2,657 / 2,649**, average aid package **$68,697**, and average need-based grant **$66,417**. Derived aid shares use D/A and H/D, rather than row I's different measure.

### Pittsburgh 2025-2026

- **C1, page 13:** men applied/admitted/enrolled **27,732 / 15,646 / 2,335**; women **36,992 / 22,831 / 3,541**. Printed enrollment totals include part-time students. No overall totals are printed, so the assembler sums these gender rows to **64,724 / 38,477 / 5,876**. Unknown-gender placeholders remain absent.
- **C9, pages 18-19:** SAT submission **40.3%**, ACT submission **8.3%**. SAT EBRW **650 / 690 / 720**; math **630 / 680 / 730**; ACT composite **29 / 32 / 33**. No SAT composite percentile row is provided; composite scores were not synthesized by adding sections. The latest SAT headline therefore displays N/A, while the existing composite chart retains its earlier reported years.
- **B1, page 4:** **21,388** undergraduates, **9,849** graduate students, **31,237** total.
- **B2, page 6:** the rightmost total-undergraduates column is blank. Its nine race fields remain absent. The populated degree-seeking column totals **21,222**, a narrower population; it was not substituted for all **21,388** undergraduates. Historical race data remain unchanged.
- **C21/C22, page 23:** both ED and EA are marked No. Counts remain absent.
- **G1, pages 31-32:** the source explicitly labels **2026-2027** costs. Public in-state undergraduate tuition **$21,594**, fees **$2,152**, food and housing **$15,430** yield the site's three-component total **$39,176**. G4 states **36.8%** pay more than the reported tuition and fees; this is the published typical amount, not every program's price.
- **H1/H2, pages 35 and 37:** H1 selects **2024-2025 Final**, rather than 2025-2026 estimated. Full-time-undergraduate H2 A/D/H are **19,729 / 8,670 / 1,081**; average aid package **$20,258**, average need-based grant **$17,819**. These retain the report's aid-period caveat.
- No undergraduate residency headcounts were inferred from F1 percentages or first-year admissions tables.

## Remaining year gaps and discovery limits

The missing target year for each school is **2016-2017**. Official current archives do not list it; direct searches and the inspected College Transitions repository supplied no verifiable report. College Transitions' displayed years begin at 2017-2018, so its omissions do not establish whether a 2016-2017 report exists.

Pittsburgh's candidate historical and migrated `PGHCDS_2016-2017.pdf` URLs both returned HTTP 404. The pre-existing local Emory file named `emory-common-data-set-2016-2017.pdf` is a five-page printout of an institutional-research web page, not a CDS, and was rejected. Filtered Wayback CDX requests for the two historical domains returned HTTP 400; those failed requests provide no evidence that an archived report does not exist. No data were estimated or borrowed from another year. No newer CDS than 2025-2026 is linked on either current official archive.

## Validation

- `python -I scripts/cds/validate.py emory`: zero errors, zero warnings.
- `python -I scripts/cds/validate.py universitypittsburgh`: zero errors; two unchanged baseline warnings: 2018-2019 race counts total 19,127 versus 19,330 undergraduates; 2022-2023 applications rise 53% from 2021-2022. Confirmed that validating the untouched Git HEAD file emits exactly the same warnings. This batch introduces neither warning.
- `bun run validate`: all 100 school files valid.
- `bun run typecheck`: passed.
- Existing development server at port 3457: both school pages render 2025-2026 titles, admissions rows, and matching headlines. Emory renders seven chart containers; Pittsburgh six, each with SVG data marks. Pittsburgh's unavailable new-year SAT composite and race counts are intentionally omitted.
- Baseline comparison: all 16 pre-existing year objects are unchanged; 80 numeric fields added, none deleted or corrected in prior years.
- `git diff --check`: passed. No application code, registrations, commits, or worktrees were created.
