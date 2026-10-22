# Boston College data expansion, October 22, 2026

Boston College (`src/data/schools/bostoncollege.json`) had 8 CDS years (2017-2018 through 2024-2025) but only **266 numeric fields** (28 per year for 2017-2018 to 2021-2022, 42 per year for 2022-2023 to 2024-2025). It had no admissions-by-gender, no early-decision counts, and no test scores at all for 2017-2018 through 2021-2022. This batch re-extracted every year from the official PDFs and filled every source-supported gap.

Result: **266 to 368 numeric fields (+102)**, counting leaves under `years` (derived rates and totals included, profile excluded; the profile has no numeric leaves). All 8 years remain; no new year could be added (see "Missing years").

| Year | Before | After | Added |
| --- | ---: | ---: | ---: |
| 2017-2018 | 28 | 42 | +14 |
| 2018-2019 | 28 | 42 | +14 |
| 2019-2020 | 28 | 44 | +16 |
| 2020-2021 | 28 | 44 | +16 |
| 2021-2022 | 28 | 46 | +18 |
| 2022-2023 | 42 | 50 | +8 |
| 2023-2024 | 42 | 50 | +8 |
| 2024-2025 | 42 | 50 | +8 |

By category: **48** admissions-by-gender fields (men and women applied/admitted/enrolled, all 8 years); **46** test-score fields (SAT EBRW/Math and ACT composite 25th/75th percentiles plus SAT and ACT submission rates for 2017-2018 to 2021-2022, plus SAT composite 25th/75th for 2019-2020 to 2021-2022); **8** early-decision fields (applied and admitted for 2021-2022, 2022-2023, 2023-2024, 2024-2025).

**No existing value was changed.** Every overlap between the original year records and the audited, source-derived fields matched exactly (zero differences), including acceptance rate, yield, total cost of attendance, enrollment total, percent receiving aid and percent of need fully met. Existing residency estimates and the profile were preserved with the limitations listed below; they are not all source-confirmed. The file was updated with a deep merge (`College-Data/bostoncollege/scratch/merge.py`), not `assemble.py`, because `assemble.py` replaces whole years; a script check confirmed every baseline value is still present and equal. The `profile` block is byte-for-byte unchanged. Baseline copy: `College-Data/bostoncollege/scratch/bostoncollege.baseline.json`.

## Official sources and SHA-256

The official IR page ([Institutional Research](https://www.bc.edu/bc-web/offices/institutional-research-planning/institutional-research.html)) and the [Common Data Set page](https://www.bc.edu/bc-web/sites/common-data-set.html) were re-fetched on 2026-10-22. Between them they link the current 2024-2025 PDF and "Common Data Sets from Previous Years" 2023-2024 back to 2017-2018, and nothing else. The saved archive snapshot `College-Data/expansion-bc-syracuse-2026-10-22/bc.html` (SHA-256 `972f3de8916643439e3029402b789db719a68c62740529362ef570ba8c308d65`) lists the same single PDF as the live CDS page. All eight files were downloaded with `scripts/cds/fetch.py` (directly, no mirror, referer set to the IR page) to `College-Data/bostoncollege/bostoncollege-cds-<year>.pdf`; they are byte-identical to the previously held `College-Data/BostonCollege/CDS_<year>_BostonCollege.pdf` copies. Manifest: `College-Data/bostoncollege/sources.json`.

| Year | Pages | Bytes | SHA-256 | Official URL |
| --- | ---: | ---: | --- | --- |
| 2017-2018 | 33 | 524,685 | `67ca2bb3352c8513bb278457eb8e6e4898d7d955064c4839d200a8f71a52e12a` | https://www.bc.edu/content/dam/bc1/offices/irp/ir/cds/Boston_College_CDS_2017-2018_Final.pdf |
| 2018-2019 | 36 | 667,922 | `344dd231d59b93adb2906be07c10099c807adb82ded4282c5cf4dc39f150cab2` | https://www.bc.edu/content/dam/bc1/offices/irp/ir/cds/Boston_College_CDS_2018-2019_Final.pdf |
| 2019-2020 | 32 | 677,525 | `921f425d57981b2b2abac0c98fb50c534d59cb8ad9852a9b4744b170e8120c3f` | https://www.bc.edu/content/dam/bc1/offices/irp/ir/cds/Boston_College_CDS_2019-2020_Final.pdf |
| 2020-2021 | 34 | 710,808 | `996acaf69b2a9c38b9ab47cc142fb7c3d7489cfb3589a7f613dabb11938baef2` | https://www.bc.edu/content/dam/bc1/offices/irp/ir/cds/Boston_College_CDS_2020-2021_Final.pdf |
| 2021-2022 | 34 | 700,447 | `5d029fc4f5b21763511602cb8d4c6ed89db0ce8ab39a34e669de3a732a73e908` | https://www.bc.edu/content/dam/bc1/offices/irp/ir/cds/Boston_College_CDS_2021-2022_Final.pdf |
| 2022-2023 | 29 | 436,858 | `39b98c559e628f3d0516528a6c9d619e2866bb4a4d299754e93f3676da505b42` | https://www.bc.edu/content/dam/bc1/offices/irp/ir/cds/Boston%20College%202022-2023%20Common%20Data%20Set.pdf |
| 2023-2024 | 31 | 270,508 | `254af806b08da8f24ebda1967a31f56a96d2e5c81eea7d5408b09230844e742e` | https://www.bc.edu/content/dam/bc1/offices/irp/ir/cds/CDS_2023-2024-Final.pdf |
| 2024-2025 | 26 | 269,503 | `42f0948c44eae3641e73583e29608d2a8f932700392c27b30ec83a14f7c93e85` | https://www.bc.edu/content/dam/bc1/offices/irp/ir/cds/Boston_College_CDS_2024-2025_Final.pdf |

Pages were rendered with `scripts/cds/pages.py` (sections B1, B2, C1, C7, C9, C21, C22, G1, H1, H2; all pages for 2023-2024, whose text layer is scrambled because the form is landscape). Page numbers below are 1-based PDF pages; BC's printed footers differ for some years (for example 2022-2023 PDF page 8 is printed "Page 13").

## Extraction method

- **Claude (Sonnet 5.5)** extracted all 8 years itself, following the `prompt.py --extractor claude` field list and rules, reading page text and the rendered PNGs (images for every year's C1, C7 and C9, plus B1, B2, C21, G1 and H2 where the layout was ambiguous). Output was held in `College-Data/bostoncollege/scratch/claude-pending/` until the Codex run finished and was not supplied to the Codex prompt; Codex was instructed not to read other extractions.
- **Codex gpt-6.1-sol** (reasoning effort high) extracted all 8 years in one T3 `delegate_task` batch in the same workspace. Each year used the full text of `prompt.py <slug> <year> --extractor codex`, saved to `College-Data/bostoncollege/scratch/codex-prompts/<year>.md`. The task was told not to read any other extraction, the school JSON, or other schools' data. Outputs: `extract/<year>.codex.json`.
- `compare.py` results: 2017-2018 51 agreed; 2018-2019 51; 2019-2020 51 agreed plus 1 single-source; 2020-2021 53; 2021-2022 57; 2022-2023 61; 2023-2024 62; 2024-2025 63. **Zero value conflicts in any year.** Final JSON per year: `extract/<year>.final.json`.

## Hand resolutions (all pages are PDF pages)

### 2019-2020, C1 enrollment by gender (p7, cross-checked against B1 on p3)

On p7 the C1 cells print full-time men who enrolled **1,078**; the "part-time men" cell prints **1,219**; and both women rows are blank. B1 on p3 prints first-time first-year full-time **men 1,078 and women 1,219** (part-time zero), and B2 on p3 prints the first-time total **2,297 = 1,078 + 1,219**. The 1,219 is therefore a misplaced women's entry.

- Claude included `admissions.byGender.men.enrolled = 1078` (single-source). Codex omitted both enrolled fields because it would not reassign the misplaced cell. Accepted 1,078 with `resolve.py --accept`, since both p7 (labelled cell) and p3 print it.
- Set `admissions.byGender.women.enrolled = 1219` with `resolve.py --set ... --page 3`, sourced from the printed B1 cell and corroborated by the p7 misplaced cell, not computed. This is a judgment call: the C1 cell for women is blank. If you prefer to leave it blank, delete that one field; the year total of 2,297 is unaffected because it was already on the site.

### Dropped or omitted rather than resolved

- **2020-2021 early decision (p13):** the C21 "applications received" and "admitted" cells print **"6/12"** and **"9/10"**, which are spreadsheet date artifacts, not counts. Both extractors omitted them; nothing was added or inferred.
- **2022-2023 C1 gender detail does not sum to the printed totals (p8):** men/women applied 15,887 + 24,459 = 40,346 vs printed 40,494; admitted 2,964 + 3,765 = 6,729 vs 6,748; enrolled 1,079 + 1,253 = 2,332 vs 2,335. The form says the detail need not sum. All values are stored as printed; no other/unknown-gender counts were inferred. B1 on p3 lists first-time women at 1,256, not the C1 figure 1,253; the C1 value is used for the C1 field.
- **2018-2019 C1 men enrolled (p9):** C1 prints **1,107**; B1 on p3 prints 1,106 for first-time full-time men. C1 as printed is stored; the existing site enrolled total (2,327 = 1,107 + 1,220) is unchanged.
- **2024-2025 early decision (p11):** 4,288 applications / 1,434 admitted, explicitly labelled "For the Fall 2024 entering class" (nearby plan dates still say 2025).

### Source-supported absences

- **SAT composite 25th/75th is absent for 2017-2018 and 2018-2019** (those forms print only EBRW, Math and ACT rows). It was not summed from sections. **No 50th percentiles** are printed for 2017-2018 through 2021-2022 (only 25th and 75th columns), so none were added; the 2022-2023 onward forms do print medians and those already existed.
- **Early-decision counts are blank for 2017-2018, 2018-2019 and 2019-2020** (ED offered, count cells empty). No early-action counts exist in any year (where BC marks early action in the older forms, no count fields are printed; later forms leave C22 unmarked or answer No).
- **No critical-reading-only values were added** to EBRW; only the printed "SAT Evidence-Based Reading and Writing" row was used.
- **No residency headcounts were added.** The F1/C1 first-year residency table in 2022-2023 onward covers first-years only, not all undergraduates.

## Corrections

No prior numeric values were changed. All overlapping source-derived fields matched the existing values. The retained residency estimates and profile Interview value remain legacy limitations, as described below.

## Missing years and why

- **2016-2017:** no verifiable CDS located. BC's official IR page lists CDS years only back to 2017-2018. A Wayback CDX query of `bc.edu/content/dam/bc1/offices/irp/*` returns only 2017-2018 through 2024-2025 CDS files (plus unrelated fact book, flier and HEOA PDFs), and the Wayback availability API has no capture of any plausible 2016-2017 CDS URL. A filtered query of the older `bc.edu/offices/irpa` and `bc.edu/offices/irp` paths found no CDS-named files (the archive server was intermittently unreachable, so this is not exhaustive). The 2016-2017 Fact Book is not a CDS and was not used.
- **2025-2026:** no verifiable CDS located as of 2026-10-22. The live IR page and CDS page link 2024-2025 as the newest CDS (page footer "Data as of 9/5/25"), and a Wayback capture of the CDS page from 2026-06-15 shows the same. The IR page now links Fall 2025 and Fall 2026 enrollment fliers, but those are not CDS files and were not used. The BC "At a Glance" and fact book PDFs were also not used. The official BC Facts page mixes Fall 2025 admissions with Fall 2024 enrollment; it was not treated as a 2025-2026 CDS. A parent check of the [College Transitions repository](https://www.collegetransitions.com/dataverse/common-data-set-repository/) found no linked Boston College report in its 2025-2026 column; that repository begins at 2017-2018.

## Reporting-population and date caveats

- BC's CDS undergraduate counts **exclude associate's-degree and continuing-education programs** (Messina College and the Woods College). 2024-2025 B1 undergraduates are 9,654, while BC's CDS web page lists a separate 116 Messina and 392 Woods students (total students 15,234 there versus 14,726 in the CDS). The site keeps the CDS-defined population.
- G1 costs follow the site convention: each CDS prints the **next** academic year (2017-2018 CDS prints 2018-2019 costs, and so on). The 2021-2022 CDS ticks "2022-2023 costs not available" yet prints $62,950 tuition; the existing value matches the page, but the cost year for that file is ambiguous. Costs were not modified.
- H1/H2 aid is the full-time undergraduate column. Several forms carry stale template labels (H2 line A cites a "Fall 2014" cohort in 2017-2018 and "Fall 2017" in 2018-2019 and 2019-2020; 2021-2022 aid is marked "estimated"; 2020-2021 text says "Final as of 8/8/21"). In every year the H2 line A values equal that year's B1/B2 undergraduate total, so the cohort is the current fall.
- 2023-2024's PDF text layer is scrambled; all of its values were read from images.
- **Existing `demographics.byResidency` values were not re-derived or verified.** The profile note says they are derived from F1 out-of-state percentages applied to domestic undergraduates, not printed headcounts. They are left as they were and no new residency estimates were added.
- **C7 interview factor:** the 2024-2025 C7 table leaves Interview unmarked, while the existing profile records `interview: not_considered`. The other 17 factor ratings in the profile match the audited 2024-2025 page exactly. The profile was preserved untouched; the Interview value is not source-confirmed (a blank cell is not proof of "not considered").

## Checks

- `python -I scripts/cds/validate.py bostoncollege`: **ok (0 errors, 0 warnings)**.
- Equality check: all 266 baseline numeric fields and the profile are present and unchanged in the updated file.
- Parent verification: `bun run validate` passed for all 100 schools; `bun run typecheck` and `git diff --check` passed. The local route returned HTTP 200, contained all eight years and seven chart containers, and its latest headlines matched the JSON. Interactive browser verification was unavailable after two preview snapshot timeouts, so the authorized HTTP fallback was used.
- No commits or worktrees were created; only `src/data/schools/bostoncollege.json`, this note, and gitignored `College-Data/bostoncollege/` (including `sources.json`, `work/`, `extract/`, `scratch/`) were touched.
