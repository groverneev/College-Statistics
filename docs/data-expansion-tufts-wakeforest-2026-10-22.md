# Tufts and Wake Forest data expansion, October 22, 2026

Audited all 100 school JSON files by CDS-year count and numeric fields per year. Colby (1 year), Stevens (4), and Chicago (5) have the shortest histories, with public-source limitations documented in earlier expansion notes. Rochester has the lowest field density (32 fields/year), followed by Tufts, Wake Forest, and WashU (32.7 each). This batch expands Tufts and Wake Forest with their newly located official 2025-2026 reports.

Both schools now cover every target CDS year from **2016-2017 through 2025-2026**. No target years remain missing for either school. Their current official archives do not list a newer report.

- **Tufts:** 9 to 10 years; 294 to 339 numeric fields, an addition of **45**.
- **Wake Forest:** 9 to 10 years; 294 to 337 numeric fields, an addition of **43**.

Added **two school-year records and 88 numeric fields**, counting leaves under `years`, including derived totals and rates, and excluding profiles. All 18 pre-existing year objects are exactly unchanged. Both C7 profiles now cite 2025-2026; all 18 factor ratings for each school match its previous profile. The pre-existing uncommitted Emory and Pittsburgh files remain byte-identical to their snapshots at the start of this batch.

## Official sources and extraction

- [Tufts official archive](https://provost.tufts.edu/institutionalresearch/common-data-set/) links the [2025-2026 PDF](https://provost.tufts.edu/institutionalresearch/wp-content/uploads/sites/5/CDS_2025-2026.pdf): 48 pages, 1,487,343 bytes; SHA-256 `a593cfd77f058312192d071cc3f83528b598ae23051b2b4d03e3a57a5d374d16`. The cover records a September 8, 2026 correction to H2 item G and H5; this is the corrected file.
- [Wake Forest official archive](https://ir.wfu.edu/common-data-set/) links the [June 2026 copy of the 2025-2026 PDF](https://prod.wp.cdn.aws.wfu.edu/sites/202/2026/06/CDS_2025-2026-PDF_Template_WFU.pdf): 50 pages, 1,966,490 bytes; SHA-256 `67bac687c0505a807d1eb84909abdf0aea5040f7b85345b4f166e3c08a790be6`. Used this current archive link instead of the older April URL returned by search.

Each report was extracted independently by Claude Sonnet 5.5 and Codex gpt-6.1-sol using the repository's extraction prompts. `compare.py` found **64 agreed fields, two single-source fields, and zero conflicts for Tufts**, and **60 agreed fields with zero single-source fields or conflicts for Wake Forest**. The two Tufts single-source ED fields were dropped after source-image review, leaving no unresolved fields. Raw inputs and C7 factors account for the difference between extraction counts and published numeric-field counts.

Downloads, manifests, page text, rendered images, independent extractions, and reconciliations are retained in the gitignored `College-Data/tufts/` and `College-Data/wakeforest/` directories. The baseline audit and school snapshots are in `College-Data/expansion-tufts-wakeforest-2026-10-22/`. Exploratory archive HTML is in `College-Data/expansion-bc-syracuse-2026-10-22/`.

## Source-page decisions and limitations

Page numbers are 1-based PDF pages, including front matter. The extraction subprocesses encountered PDF access restrictions while attempting additional renders. The parent rendered and visually checked the missing pages before assembly; those review decisions are recorded under `review_notes` in each final extraction.

### Tufts 2025-2026

- **C1, pages 11-12:** retained the explicitly printed totals **33,415 applied / 3,613 admitted / 1,765 enrolled** from the residency table. The gender rows print men **14,444 / 1,568 / 777**, women **18,947 / 2,044 / 987**, and unknown sex **4 / 0 / 0**. These sum to **33,395 / 3,612 / 1,764**, slightly below the printed totals. Preserved both as reported; did not replace explicit totals with sums. The overall acceptance rate and yield derive from the printed totals.
- **C21, page 21:** dropped the single-source ED applications/admissions **3,344 / 1,071** using `resolve.py`. The image explicitly labels these **Fall 2024**, while C1 reports Fall 2025. The previous 2024-2025 PDF, page 14, leaves its ED count cells blank, so it cannot establish whether the new heading is stale. These counts were not published under 2025-2026 or inserted into another year. C22 marks No; EA counts remain absent.
- **B1/B2, pages 3-4:** retained **7,031 undergraduates / 6,619 graduate students / 13,650 total** and the rightmost total-undergraduate race column, which sums to **7,031**.
- **C9, page 17:** SAT composite **1460 / 1500 / 1520**, EBRW **720 / 740 / 760**, math **730 / 760 / 780**; ACT composite **33 / 34 / 35**. Submission rates **42% / 16%**.
- **G1, page 27:** explicitly reports **2026-2027** tuition **$74,862**, fees **$1,696**, and combined food/housing **$20,594**. The assembler derives **$97,152** under the site's existing CDS-year convention.
- **H1/H2, pages 30-31:** visually confirmed **2025-2026 Estimated**. Full-time-undergraduate A/D/H are **6,830 / 2,529 / 2,529**; package **$65,473**, need-based grant **$63,238**. Aid shares derive from D/A and H/D. The first-year column's H>D inconsistency is outside the selected full-time-undergraduate column.

### Wake Forest 2025-2026

- **C1, pages 13-14:** page 13 gives men **8,235 / 1,965 / 676**, women **11,360 / 2,103 / 868**, and unknown sex **5 / 0 / 0**. The assembler derives **19,600 / 4,068 / 1,544**, including the five unknown-sex applications. The optional, unfilled residency table on page 14 shows default zero totals; these were rejected because the populated main table contradicts them.
- **B1/B2, pages 5-6:** **5,595 undergraduates / 4,038 graduate students / 9,633 total**. Used the rightmost total-undergraduate race column, including **3,742 White** and **269 unknown**, rather than the narrower degree-seeking column.
- **C9, page 19:** SAT composite **1420 / 1450 / 1490**, EBRW **700 / 730 / 750**, math **700 / 730 / 760**; ACT composite **32 / 33 / 34**. Submission rates **24% / 22%**.
- **C21/C22, page 23:** ED is offered and EA is offered for first-generation applicants, but counts are not supplied. ED/EA count fields remain absent.
- **G1, page 29:** explicitly reports **2026-2027** tuition **$71,894** and fees **$1,276**. The combined food-and-housing cell is blank. Separate housing **$12,900** and maximum meal plan **$10,530** were not summed or substituted; `roomAndBoard` and `totalCOA` remain absent. The typical-meal estimate **$7,396** was also not substituted.
- **H1/H2, pages 32-33:** visually confirmed **2025-2026 Estimated**, resolving the extractors' uncertainty about the checkbox. Full-time-undergraduate A/D/H are **5,401 / 1,206 / 1,079**; package **$77,994**, need-based grant **$69,008**. Retained the source H2 denominator despite its difference from current B1; the H2 row label still references Fall 2024.

Neither report provides all-undergraduate residency headcounts. No headcounts were inferred from F1 percentages or first-year admissions residency tables. Unreported fields remain absent.

## Checks

- `python -I scripts/cds/validate.py tufts`: zero errors; one pre-existing 2024-2025 race-population warning (**7,126** race counts vs **7,036** undergraduates). Validating the saved untouched baseline gives exactly the same warning; this batch introduces none.
- `python -I scripts/cds/validate.py wakeforest`: zero errors, zero warnings.
- `bun run validate`: all 100 school files valid.
- `bun run typecheck`: passed.
- Both pages render 2025-2026 titles and matching latest-year admissions rows and headlines on the existing development server at port 3457. Each has six chart containers with SVG data marks. Wake Forest's unreported new-year combined cost is omitted while historical costs remain charted.
- Equality checks passed for all 18 existing year objects and both pre-existing Emory/Pittsburgh edits.
- `git diff --check`: passed. No application code, registrations, commits, or worktrees were created.
