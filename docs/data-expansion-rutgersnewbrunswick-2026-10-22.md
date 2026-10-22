# Rutgers University-New Brunswick data expansion, 2026-10-22

Reworked `src/data/schools/rutgersnewbrunswick.json` (8 years, 2016-2017 to 2023-2024) from **300 to 310 numeric leaves**, profile excluded. The change is **+40 newly sourced leaves, 32 existing aid leaves replaced by the correct-population values, and 30 unsupported legacy leaves removed**. Every admissions, enrollment, race and cost value already on the site was re-extracted independently and confirmed unchanged. The profile (C7 factors, source 2023-2024) is byte-for-byte unchanged.

Only the Rutgers school JSON, this note and gitignored `College-Data/rutgersnewbrunswick/` were edited. No app code, registry, shared scripts, worktrees or commits.

## Sources and newer-year check

Official archive: [Rutgers OIRAP Common Data Set page](https://oirap.rutgers.edu/ReportingCommonDataSet.html). Fetched live on 2026-10-22 (`web/live.html`, sha256 `826b7594...2570f`; differs from the parent's April 2026 snapshot `College-Data/expansion-bc-syracuse-2026-10-22/rutgers.html`, sha256 `87416e6a...f58f`, only in line endings). The page lists the same 41 CDS links in both, and the newest New Brunswick report is **2023-2024**. The Wayback copy of 2026-04-10 (`web.archive.org/web/20260410054148id_/...`, saved decoded as `web/wayback-20260410.decoded.html`) is identical in content. Wayback CDX shows the page captured 2025-05-13, 2025-07-11 and 2026-04-10, with no later or additional reports.

No 2024-2025 or 2025-2026 report was found: direct URL guesses for `CDS/2024/` and `CDS/2025/` with the established `New Brunswick CDS_<year>...pdf` patterns all returned HTTP 404, the Wayback CDX query for those paths returned empty/503, and two web searches found only the 2023-2024 file and third-party summaries. **No verifiable 2024-2025 or later CDS was located, so these years remain absent.** A parent check of the [College Transitions repository](https://www.collegetransitions.com/dataverse/common-data-set-repository/) also found no linked Rutgers file in its 2024-2025 or 2025-2026 columns. The collegedata.fyi archive likewise identifies 2023-2024 as its latest CDS; its newer IPEDS facts were not substituted for CDS values. Reports before 2016-2017 (2012-2015 exist on the archive) are outside the project's target range.

All eight PDFs were re-downloaded with `fetch.py` (direct, referer = archive page, canonical names `rutgersnewbrunswick-cds-<year>.pdf`) and rendered with `pages.py --render B1,B2,C1,C7,C9,C21,C22,G1,H2`. Hashes are identical to the pre-existing `College-Data/Rutgers-New-Brunswick/CDS_<year>_RutgersNewBrunswick.pdf` files. Page 1 of each file names Rutgers University - New Brunswick and the CDS year. Full URLs, SHA-256 and page counts are in `College-Data/rutgersnewbrunswick/sources.json`.

| CDS year | Official PDF | SHA-256 | Pages |
| --- | --- | --- | ---: |
| 2016-2017 | https://oirap.rutgers.edu/CDS/2016/New%20BrunswickRegion16.pdf | 123da5f065fb2e6e012fefde29c1f9d66cdc883be172a5ebbc0c24fc399a54a3 | 31 |
| 2017-2018 | https://oirap.rutgers.edu/CDS/2017/New%20Brunswick%20CDS_2017-2018.pdf | a0f839fedfb546027aec9b0e369aec54249f53f22087c062eaf45c1677bb4f3c | 30 |
| 2018-2019 | https://oirap.rutgers.edu/CDS/2018/New%20Brunswick%20CDS_2018-2019.pdf | 3f43089ef2141d48e6bf66eefb3592654cc6102f90f11e92c43ab05de5153922 | 31 |
| 2019-2020 | https://oirap.rutgers.edu/CDS/2019/New%20Brunswick%20CDS__2019-2020_Final_V3.pdf | 1c53e0b7ea86822a1b6d8423f774431254b7930ec5a3674334a730aaceab3bda | 31 |
| 2020-2021 | https://oirap.rutgers.edu/CDS/2020/New%20Brunswick%20CDS_2020-2021.pdf | 1590169fea82a243c116b9ecf16a87dd74b5088ea23ef864fab3c868d7ef5917 | 31 |
| 2021-2022 | https://oirap.rutgers.edu/CDS/2021/New%20Brunswick%20CDS_2021-2022_Final%20V1.pdf | 5e4c9b92181607a74dbbb2d0d55e88aa1b1172e06ef1f3293deea9c934d07df5 | 31 |
| 2022-2023 | https://oirap.rutgers.edu/CDS/2022/New%20Brunswick%20CDS_2022-2023__Final.pdf | e56fbef82f6b90cc0a74b04b75dd75dd578e6e247eacfaf42c18d62fe8d75164 | 29 |
| 2023-2024 | https://oirap.rutgers.edu/CDS/2023/New%20Brunswick%20CDS_2023-2024_final_V1.pdf | 9adfd2e36365ee65d3316ae7a0d1ea3674cf62aa0a412018d753366ddc8296f3 | 29 |

Page numbers below are one-based PDF pages. The layout is consistent across years: B1/B2 p2, C1 p5, C7 p7, C9 p9, C21/C22 p12, F1 p17 (p16 in 2017-2018), G1 pp19/21 (pp18/20 in 2017-2018, p19 only from 2022-2023), H2 p24 (p23 in 2017-2018; p22 from 2022-2023).

## Independent extraction and reconciliation

- **Claude extraction**: me, Claude Sonnet 5.5, directly from the rendered pages, using the field list and rules emitted by `prompt.py --extractor claude`; written to `extract/<year>.claude.json` before the Codex results were opened. C7 images (p7 of each year) and the C9 images of 2019-2020 and 2022-2023 were visually read.
- **Codex extraction**: one T3 `delegate_task` (provider `codex`, model `gpt-6.1-sol`, `reasoningEffort=high`, `serviceTier=default`) in the same workspace ran all eight years, each with the full `prompt.py --extractor codex` prompt saved as `prompts/<year>.codex.txt`. It was told not to read other extraction files, site JSON, docs, git history or the old PDF folder, and was not shown any of my values. All eight `<year>.codex.json` files carry page numbers and verbatim evidence. Its files were all written at one moment (07:27:40) after mine; The extraction prompts required isolation from the other pass, and no extractor-to-extractor information flowed in the prompts.
- `compare.py` result per year: 50, 51, 54, 54, 54, 54, 58, 58 agreed values with **zero conflicts**. Single-source fields: only `admissions.enrolled` in 2017-2018 to 2021-2022 (sum of the printed full + part-time gender rows; Codex left it blank because no combined total is printed). I viewed the five C1 page images (p5 of those years): the totals are not printed, so I dropped the field with `resolve.py --drop` and the assembler derives enrolled from the gender rows (and in each year it equals the first-time B2 total). The 2016-2017 total (6,466) is printed and both extractors agreed.
- `assemble.py` overwrites existing years and rewrites the profile source name. I ran it with the original saved in `before.json`, saved the output as `assembled-verified.json`, restored the original, and built the final JSON from the assembled years plus the original untouched profile. `merge-audit.json` lists every overlap change, removal and addition.

Agreement on all the numeric fields the site already held (admissions applied/admitted/enrolled and by gender, enrollment, B2 race, tuition/fees/room and board, total cost of attendance, acceptance rate and yield) was complete, so none of those values changed.

## What was added (40 numeric leaves)

| Year | Added | Pages |
| --- | --- | --- |
| 2016-2017 | SAT math p25 580 / p75 700 (old scale); SAT submission rate 0.89 | 9 |
| 2017-2018 | SAT EBRW 590/680, math 600/720; SAT submission 0.81 | 9 |
| 2018-2019 | SAT EBRW 590/680, math 600/730, SAT 0.87; ACT composite 25/31, ACT 0.25 | 9 |
| 2019-2020 | SAT EBRW 590/680, math 620/750, SAT 0.90; ACT 25/32, ACT 0.18 | 9 |
| 2020-2021 | SAT EBRW 580/680, math 600/730, SAT 0.90; ACT 25/32, ACT 0.18 | 9 |
| 2021-2022 | SAT EBRW 610/710, math 630/760, SAT 0.45; ACT 27/33, ACT 0.07 | 9 |
| 2022-2023, 2023-2024 | none: reported section and ACT scores were already present | 9 |

Scores are percentiles as printed. p50 columns exist only on the 2022-2023 and 2023-2024 forms (already in the baseline and matching the printed values); no medians were inferred for earlier years. No ED/EA counts exist (C21 is "No"; C22 says early action is offered, with closing 11/1 and notification 1/31, but no application or admit counts are printed; pp12 each year). No SAT composite exists on any form (see removals).

## Corrections and removals, all justified by the source pages

1. **Financial aid used the wrong H2 column in all eight years (32 leaves replaced).** The baseline `percentReceivingAid`, `averageAidPackage`, `averageNeedBasedGrant` and `percentNeedFullyMet` were calculated from the H2 "First-time Full-time Freshmen" column (for example 2023-2024: avg package 14,373, grant 14,849, 3,946/7,769 receiving, 911/3,946 fully met). The site rule and the extraction field definition require the **full-time undergraduate** column (line a, d, h, j, k). Both independent extractors used that column and agree. New values (a / d / h / j / k, then derived share receiving aid and share fully met):

| Year | H2 page | Cohort printed in line a | a / d / h | Avg package (was) | Avg need-based grant (was) | % aid (was) | % need fully met (was) |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| 2016-2017 | 24 | stale header "Fall 2014"; a matches Fall 2016 B1 | 33,939 / 17,988 / 613 | 13,796 (14,927) | 11,399 (12,937) | .5300 (.5265) | .0341 (.0735) |
| 2017-2018 | 23 | "Fall 2016" | 33,939 / 18,102 / 717 | 13,747 (15,044) | 11,124 (12,943) | .5334 (.5283) | .0396 (.0618) |
| 2018-2019 | 24 | "Fall 2017" | 33,619 / 18,264 / 687 | 14,197 (14,822) | 11,517 (13,025) | .5433 (.5201) | .0376 (.0565) |
| 2019-2020 | 24 | "Fall 2018" | 33,981 / 17,686 / 719 | 14,433 (14,538) | 12,215 (13,651) | .5205 (.5263) | .0407 (.0535) |
| 2020-2021 | 24 | "Fall 2019" | 34,233 / 16,956 / 543 | 14,351 (14,647) | 12,535 (14,263) | .4953 (.4679) | .0320 (.0474) |
| 2021-2022 | 24 | "Fall 2020" | 33,769 / 15,373 / 658 | 12,401 (12,429) | 11,867 (12,952) | .4552 (.4204) | .0428 (.0596) |
| 2022-2023 | 22 | "Fall 2021" | 34,361 / 15,877 / 1,826 | 12,663 (12,766) | 12,235 (13,566) | .4621 (.4706) | .1150 (.1743) |
| 2023-2024 | 22 | "Fall 2022" | 34,630 / 16,988 / 2,995 | 13,560 (14,373) | 13,516 (14,849) | .4906 (.5079) | .1763 (.2309) |

   Caveat: Rutgers' H2 reports the aid cohort of the *previous* fall, one year behind the CDS year, in every year from 2017-2018 on (line a is stamped with that cohort and matches that fall's B1 first-time and full-time degree-seeking counts: 2018-2019 6,266/33,619 = Fall 2017). The 2016-2017 form's header still says "Fall 2014 cohort" but line a equals the Fall 2016 B1 counts. The 2017-2018 form repeats the Fall 2016 line-a counts (6,460 / 33,939 / 1,843) as its stamped cohort while rows b to m differ from the 2016-2017 form, so I recorded it as printed. The validator warning the baseline raised for 2022-2023 (average need-based grant 13,566 above average package 12,766) came from the freshman column and is gone with the corrected values.
   The old values are preserved in `before.json` and `merge-audit.json` if the project prefers the freshman population.

2. **SAT composite removed for 2022-2023 and 2023-2024 (6 leaves).** The baseline 1270/1370/1480 and 1270/1380/1480 equal the sum of the section percentiles (630+640, 670+700, 720+760; 630+640, 680+700, 720+760). The SAT Composite percentile row is blank on 2022-2023 p9 and 2023-2024 p9 (visually checked; only the blank score-range table appears), and no other year prints one. The baseline p50s for EBRW, math and ACT are printed and retained.

3. **Residency headcounts removed for all eight years (24 leaves).** The baseline `byResidency` values do not appear in any CDS. They are F1 percentages applied to undergraduate counts: each out-of-state figure equals the F1 undergraduate out-of-state percent (6% in 2016-2017 to 2021-2022, 7% in 2022-2023 and 2023-2024, p17, p16 in 2017-2018) times (B1 undergraduates minus B2 nonresidents), to within rounding, with in-state as the remainder and international copied from B2. The field rule forbids deriving residency from F1 percentages. 2023-2024 p5 does print first-year-only applicant, admit and enrollee residency counts; these are not all-undergraduate headcounts and were not used. B2 nonresident counts remain in `byRace.international`.

## Population and reporting-period caveats

- **Costs follow the site's next-year convention.** Each form prints two G1 tables: the next academic year on the later-added page (pp19, or p18 in 2017-2018) and the CDS year on pp21/20. The site uses the printed next year, which both extractors selected: 2016-2017 AY 2017-2018 $11,619/$3,019/$12,452, 2017-2018 AY 2018-2019 $11,886/$3,088/$12,706, 2018-2019 AY 2019-2020 $12,230/$3,177/$13,075, 2019-2020 AY 2020-2021 $12,230/$2,773/$13,075 (the lower fee is as printed), 2020-2021 AY 2021-2022 $12,536/$3,268/$13,402, 2021-2022 AY 2022-2023 $12,900/$3,363/$13,909, 2022-2023 AY 2023-2024 $13,674/$3,565/$14,715 and 2023-2024 AY 2024-2025 $14,222/$3,707/$15,714. In 2022-2023 and 2023-2024 the "costs not available" box is checked (with a July 31, 2023 date) although figures are printed; I used the printed figures. These are in-state tuition for a public university.
- **SAT scales.** The 2016-2017 form still uses the old SAT (Critical Reading 530/650, Writing 540/660, which are not EBRW and were omitted; math 580/700 is on the old scale, so it is not directly comparable with later years). The 2017-2018 form asks for concordance to the new SAT and prints EBRW. No ACT scores exist in 2016-2017 and 2017-2018 (cells blank); ACT begins in 2018-2019.
- **Test submission rates** apply to enrolled first-year students; the 2021-2022 to 2023-2024 values reflect test-optional/recommended policies (SAT 45%, 50%, 50.9%).
- **Enrollment populations.** `demographics.enrollment.undergraduate` is B1 total undergraduates (degree- plus non-degree-seeking, full- plus part-time); B2 uses the rightmost "Total undergraduates (both degree- and non-degree-seeking)" column, whose total equals B1 (36,168 to 36,588). Gender enrollment is full-time plus part-time (for example 2016-2017 men 3,263+5=3,268); the 2016-2017 annotation "6602 full-time / 5 part-time" next to C1 contradicts the printed rows and was ignored. No other-gender C1 rows exist.
- **Duplicate-looking C1 entry:** 2020-2021 men applied 19,317 equals the 2019-2020 value; the form's total 41,263 equals 19,317 + 21,946, so it is internally consistent and both extractors read it identically.
- The 2022-2023 and 2023-2024 C1 totals (41,654 / 27,612 / 7,780 and 43,347 / 28,326 / 7,681) are printed and equal the gender sums. 2023-2024 C7 interview and talent/ability are "Considered*" because Mason Gross School of the Arts applicants must complete a talent assessment; the preserved profile already shows "considered".
- The 2016-2017 C7 form marks interview and talent "X-MGSA ONLY" under Very Important; the profile uses the newest year only, so it is unaffected.

## Remaining gaps

- No report after 2023-2024 is published on the official archive (see above); no external mirror was needed.
- Not reported on any form and therefore absent: SAT composite percentiles and p50s before 2022-2023, ACT in 2016-2017 and 2017-2018, ED/EA counts, all-undergraduate residency headcounts, and SAT EBRW for 2016-2017.

## Validation

`python -I scripts/cds/validate.py rutgersnewbrunswick`:

```text
rutgersnewbrunswick: ok (0 errors, 0 warnings)
```

All eight reconciled finals have zero unresolved conflicts and zero single-source fields. `git diff --check` is clean. The profile was verified equal to the baseline, no year was dropped, and the only changes to pre-existing numeric leaves are the 32 aid replacements and 30 removals above. Parent verification: `bun run validate` passed for all 100 schools; `bun run typecheck` and `git diff --check` passed. The local route returned HTTP 200 with all eight years and five chart containers; headlines matched the JSON, including N/A for the unreported SAT composite. The SAT composite chart is absent because no verified composite is reported in any year. Interactive browser verification was unavailable after two preview snapshot timeouts, so the authorized HTTP fallback was used.

Evidence (gitignored): `College-Data/rutgersnewbrunswick/` holds `sources.json`, `web/` (live, Wayback and decoded archive page plus `official-links.json`), `work/` (page text and renders), `prompts/` (Codex prompts), `extract/` (both independent extractions, finals, resolutions), `before.json`, `assembled-verified.json` and `merge-audit.json`.
