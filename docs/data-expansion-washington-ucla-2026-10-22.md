# Washington and UCLA data expansion, October 22, 2026

Added three missing CDS years and re-extracted one sparse existing year using independent Claude Sonnet 5.5 and Codex gpt-6.1-sol passes. Both schools now cover every CDS year from 2016-2017 through 2025-2026.

| School | Years before / after | Numeric fields before / after | Change |
| --- | --- | --- | --- |
| University of Washington, Seattle | 8 / 10 | 336 / 412 | Added 2016-2017 and 2017-2018, 76 fields |
| UCLA | 9 / 10 | 297 / 333 | Added 2016-2017 and verified/corrected 2017-2018, net 36 fields |

Counts include numeric leaves under `years`, including derived rates and totals, and exclude profiles. In total: 119 newly populated fields, 7 unsupported legacy fields removed, 22 existing values corrected, net +112 fields. The UCLA 2017-2018 change adds six admissions-by-gender fields. All other existing year objects and both latest admissions-factor profiles are exactly equal to saved baselines.

## Selection and source limits

Audited all 100 school JSON files by year count and field count. Colby (one year), Stevens (four), and UChicago (five) have the shortest histories. The existing expansion reports already document extensive unsuccessful searches for their missing years. Current searches and the Stevens/UChicago official listings did not reveal additional CDS reports. Their data was preserved. Washington and UCLA were selected from the next sparse records because official and archived official sources could fill actual gaps.

## Sources

- Washington official archive: <https://www.washington.edu/opb/uw-data/external-reporting/common-data-set/>. Selected Seattle, excluding Bothell and Tacoma. The current listing ends at 2025-2026.
- Washington 2016-2017: <https://depts.washington.edu/opbfiles/web/CDS_2016-2017_Seattle.xlsx>.
- Washington 2017-2018: <https://depts.washington.edu/opbfiles/web/CDS_2017-2018_Seattle.xlsx>.
- UCLA official archive: <https://apb.ucla.edu/campus-statistics/common-data-set-undergraduate-profile>. The current listing ends at 2025-2026.
- UCLA 2016-2017 main report, an archived official PDF: <https://web.archive.org/web/20200608194139id_/https://www.apb.ucla.edu/Portals/90/Documents/Campus%20Stats/CDS%20Fall%202016.pdf>. Located through the Wayback CDX PDF inventory. Page 1 identifies UCLA and Fall 2016.
- UCLA 2016-2017 matching Section H: <https://apb.ucla.edu/file/a328d5ae-18a6-4ec4-9d31-54f7cba4825a>.
- UCLA 2017-2018 main report: <https://apb.ucla.edu/file/5cd56d8d-3eba-45b2-ae85-daed0a934fea>.
- UCLA 2017-2018 matching Section H: <https://apb.ucla.edu/file/fb0dc558-2683-447e-8273-27ecb79bfdf1>.

`fetch.py` recorded URLs, retrieval timestamps, sizes and SHA-256 hashes in each school's ignored `College-Data/<slug>/sources.json`. UCLA's main and aid sections were combined in that order. `pages.py` prepared worksheet text for Washington and PDF text/images for UCLA. PDF page citations below refer to the combined files. Washington page numbers are worksheet order: B=2, C=3, G=7, H=8.

## Independent extraction and manual decisions

Claude and Codex received the `prompt.py` field definitions independently. The Claude tasks were explicitly prohibited from reading site JSON, previous extractions or the other model's output. Codex ran through `crosscheck.py` for each of the four reports. No unresolved value conflicts remain.

| Report | Agreed fields | Initial single-source fields | Resolved final fields |
| --- | ---: | ---: | ---: |
| Washington 2016-2017 | 48 | 2 | 50 |
| Washington 2017-2018 | 52 | 0 | 52 |
| UCLA 2016-2017 | 53 | 0 | 53 |
| UCLA 2017-2018 | 57 | 1 | 57 |

Every manual reconciliation:

1. **Washington 2016-2017, worksheet/page 3:** accepted `admissions.byGender.men.enrolled=3044` and `admissions.byGender.women.enrolled=3431`. Checked source cells CDS-C E11/E12 (3,014 full-time + 30 part-time) and E14/E15 (3,399 + 32). These fields explicitly require full- plus part-time enrollment. Codex had omitted them under its broader interpretation of the instruction not to compute totals. All-gender admissions totals remain assembler-derived.
2. **UCLA 2017-2018, PDF pages 2 and 4:** dropped single-source `admissions.enrolled=6038` from the extraction, because its citation was the B1 total on page 2 rather than the C1 field. The assembler independently derives the same 6,038 from verified C1 rows on page 4: men 2,410 + 5, women 3,612 + 11, unknown/other 0 + 0. Applied/admitted totals also include C1 unknown/other applicants (1,990) and admits (366).

Additional source checks:

- Washington 2016-2017 C9 reports old-scale SAT Critical Reading and Writing, so neither is mapped to Evidence-Based Reading/Writing. Neither Washington year prints a SAT composite or medians. UCLA 2016-2017 similarly has no composite or medians. The new section/ACT score data is retained without inventing composites.
- Washington G1 prints next-year headers but checks that next-year costs are unavailable. Preserved the printed undergraduate in-state tuition/fees/room-and-board: 9,694/1,059/11,691 and 9,909/1,375/12,117. Their precise cost-year labeling remains a source limitation.
- UCLA 2016-2017 G1 is on page 13; undergraduate fees are 2,024, distinct from freshman fees of 2,189. Used in-state tuition 11,220. Aid uses the middle, full-time undergraduate H2 column, pages 17-18. UCLA 2017-2018 aid uses the same column, pages 20-21. Both aid sections select the estimated current-year cohort.
- Visually reviewed UCLA 2017-2018 C1/C7 (pages 4-5), C9 (page 7), G1 (page 14), H2 (pages 20-21), and the 2016-2017 H2 continuation (page 18). No residency headcounts were inferred from F1 percentages.

## UCLA 2017-2018 corrections

The previous record included stale or unsupported figures. Replaced the affected year with reconciled source values:

- Admissions: admits 16,515 to 16,456; enrolled 6,022 to 6,038. Applied remains 102,242. Acceptance rate becomes 0.1610 and yield 0.3669. Page 4 supplies every C1 gender/unknown row.
- Costs, page 14: tuition 41,275 to the source's **in-state** 11,502; required fees 1,721 to 1,778. Room and board remains 15,991. Derived total becomes 29,271 instead of 58,987.
- B2 race counts, page 2: all nine categories now use the rightmost **All undergraduates** column. They sum to the preserved B1 undergraduate enrollment of 31,002.
- H2, pages 20-21: average package 21,927 to 23,980; average need-based grant 19,542 to 20,489; receiving-aid fraction 0.56 to 16,365/30,120 = 0.5433; fully-met fraction 0.40 to 4,199/16,365 = 0.2566.
- C9, page 7: SAT submission 0.67 to 0.7440 and ACT submission 0.33 to 0.5822. Removed four unsupported p50 values (SAT composite, EBRW, Math and ACT composite); the form prints only 25th/75th percentiles.
- Removed the three residency headcounts. F1 supplies percentages, not all-undergraduate residency headcounts, so those legacy values lack support in the source.

## Verification and remaining limitations

- `assemble.py` ran for both schools. Exact equality assertions confirmed preservation of all Washington existing years, all UCLA years except 2017-2018, and both profiles.
- All four newly extracted year objects pass the CDS validator's shape and numeric/consistency checks with **0 errors and 0 warnings**.
- `bun run validate`: **100 school files valid**. `bun run typecheck`: passed.
- Full `validate.py ucla`: **0 errors, 6 warnings**. Three existing latest-year gender gaps and two existing tuition warnings remain. Correcting 2017-2018 to in-state tuition exposes an additional jump into the unchanged 2018-2019 legacy tuition. The 2018-2019 through 2024-2025 UCLA cost records were not re-extracted in this batch.
- Full `validate.py uwashington`: **4 pre-existing errors and 10 pre-existing warnings**, reproduced against the saved baseline. The errors are 2020-2021 through 2023-2024 race counts using degree-seeking populations while B1 includes non-degree students. Existing residency objects also fail population reconciliation. Checked original CDS-B worksheet cells: 2020/2021/2022 B1 C22/C22/C25 agrees with the site's enrollment values, while B2 E40/E40/E48 agrees with the site's degree-seeking race sums. The 2023-2024 official file was freshly downloaded and is byte-identical to the existing copy; it additionally reports B1 total undergraduates 39,125 (E19) but B2 all-undergraduate total 33,598 (G53), so the source itself has a population inconsistency. These legacy records were preserved; this batch does **not** claim a clean whole-school Washington consistency check.
- Used the existing development server on port 3457. Both school pages load with ten admissions rows and six nonzero-size chart containers with populated SVG series. Charts include the recovered 2016/2017 years where the relevant metric exists. SAT composite charts correctly start later because these older sources do not print a composite. Latest headline values and profiles remain unchanged. Browser snapshot attempts timed out, but navigation and DOM evaluation succeeded; no screenshot-based visual review is claimed.

Only the two school JSON files and this report are tracked changes. Downloaded sources, prepared pages, independent extractions, reconciliation decisions and baselines remain gitignored. No application code or shared scripts changed. No worktree or commit was created.
