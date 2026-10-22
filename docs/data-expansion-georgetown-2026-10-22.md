# Georgetown data expansion, 2026-10-22

Expanded `src/data/schools/georgetown.json` from **8 years / 252 numeric leaves** to **10 years / 438 numeric leaves**, excluding the entire profile from both counts. Added 186 numeric leaves: 86 in two new years and 100 in existing years. Every CDS year from 2016-2017 through the newest published 2025-2026 is now represented.

Only the Georgetown school JSON, this document, and gitignored Georgetown evidence were edited. No app code, registry, shared scripts, worktrees, or commits. Existing profile content was preserved exactly. Existing numeric values were preserved except the four separately documented 2021-2022 admissions corrections below.

## Official sources and coverage

Discovery: [Georgetown Office of Assessment and Decision Support CDS archive](https://oads.georgetown.edu/commondataset/). The official page links every target year, so no Wayback or mirror discovery was necessary. All ten PDFs were freshly downloaded using `fetch.py` with the official archive as referer. Page 1 of each downloaded file names Georgetown University and the corresponding CDS year. The 2022-2023 stale running headers are resolved below.

Page numbers below are one-based PDF pages, matching the printed page numbers.

| CDS year / official PDF share URL | Numeric leaves before → after | Added coverage | C1 pages | C9 pages |
| --- | ---: | --- | ---: | --- |
| [2016-2017](https://georgetown.box.com/s/sy6d1d9f6riz5t3q2egojnyzw3qj509q) | 28 → 40 | Six gender admissions fields; six score fields | 6 | 8 |
| [2017-2018](https://georgetown.box.com/s/3azkfk30zxabxqccj0osp0lrhhy2p1s9) | 28 → 42 | Six gender admissions fields; eight score fields | 7 | 9-10 |
| [2018-2019](https://georgetown.box.com/s/4kq8y4ud4d3kwsvxaf37rsvvibhtydd7) | 28 → 42 | Six gender admissions fields; eight score fields | 7 | 9-10 |
| [2019-2020](https://georgetown.box.com/s/sty6w23zh0te8rnsbnndy62afivfdaz1) | 28 → 44 | Six gender admissions fields; ten score fields | 7 | 9-10 |
| [2020-2021](https://georgetown.box.com/s/32o25lslrx69q6n4n12egrd5yudswpl7) | 28 → 44 | Six gender admissions fields; ten score fields | 7 | 10 |
| [2021-2022](https://georgetown.box.com/s/w5ofngecelho4y9rhqdmvjohw0qsvfay) | 28 → 44 | Six gender admissions fields; ten score fields; four corrections | 7 | 10 |
| [2022-2023](https://georgetown.box.com/s/rm2h89oik59skfqe3dcrx1r9j2rs2n1i) | 0 → 41 | New year: admissions, tests, enrollment, race, costs, aid | 7 | 9 |
| [2023-2024](https://georgetown.box.com/s/i6ct2x531j7aso2ka3kvw2blur82embn) | 42 → 48 | Six gender admissions fields | 6 | 8, already populated |
| [2024-2025](https://georgetown.box.com/s/rp4p2ly4ej2tsikv827pl48psmb68quv) | 42 → 48 | Six gender admissions fields | 8 | 11, already populated |
| [2025-2026](https://georgetown.box.com/s/0r8akn4cbm52zjkll6i7uttlb9k36px2) | 0 → 45 | New year: admissions, tests, enrollment, race, costs, aid | 9 | 12 |

Gender fields are `admissions.byGender.{men,women}.{applied,admitted,enrolled}`. Score additions are SAT/ACT submission rates, ACT composite p25/p75, SAT math p25/p75, SAT reading/writing p25/p75 from 2017-2018 onward, and explicitly reported SAT composite p25/p75 from 2019-2020 onward. No composite was calculated by adding section percentiles. The 2025-2026 source also prints all four supported p50 values.

## Independent extraction and assembly

Two GPT/Codex extractions used the source pages and the field definitions emitted by `prompt.py`, with distinct extractor names `primary` and `secondary`. The primary extraction was completed before any secondary values were read. The secondary child used provider `codex`, model `gpt-6.1-sol`, `reasoningEffort=high`, and `serviceTier=default`, matching the inherited options returned by `orchestrator_capabilities`. No Claude model or `crosscheck.py` was used.

For existing years the extraction scope was C1, C9, and any printed C21/C22 counts; for the two new years it covered all allowed fields. `compare.py georgetown <year> --left primary --right secondary` produced **260 agreements, zero single-source fields, and zero conflicts** across ten years. Per-year agreed counts: 14, 14, 14, 16, 16, 19, 54, 23, 26, 64. These include extraction-only raw values and factors and therefore differ from published numeric leaf counts.

`assemble.py` generated a verified candidate. Because it replaces every year represented by a final extraction, its output was saved under `College-Data/georgetown/assembled-verified.json` and selectively merged into a snapshot of the original school data. Missing fields and years were retained from the candidate; existing values and the entire profile were retained from the snapshot, apart from the documented correction. The merge audit records every overlap that differed; the only four were the correction below. New C7 factors agree with the existing profile levels, and that profile was left intact.

Evidence remains gitignored under `College-Data/georgetown/`: `sources.json` records official URLs, resolved static-download URLs, retrieval method, SHA-256, byte count and page count; `official-links.json` and `source-year-verification.json` preserve discovery and year checks; `work/` contains text and rendered pages; `extract/` contains prompts, independent extractions and reconciled finals; `before.json`, `assembled-verified.json`, and `merge-audit.json` preserve assembly provenance.

## Manual source-page decisions and population caveats

There were no extractor disagreements to adjudicate. The following source ambiguities and publication decisions were nevertheless checked directly against the pages and, where layout mattered, rendered images.

1. **2021-2022 all-gender admissions correction, p7.** The source prints all-gender applied **27,629**, admitted **3,311**, and enrolled **1,585**, and explicitly allows totals to include students without reported gender. Existing applied **27,506** and admitted **3,301** equaled only the binary gender sums. Corrected the two totals and their derived acceptance rate **0.1200 → 0.1198** and yield **0.4802 → 0.4787**. Enrollment remains 1,585. Both independent extractions agree on the printed totals. No unknown-gender counts were invented from the differences.

2. **2022-2023 stale running headers, pp1, 3, 7, 9, 18, 20-21.** Page 1 identifies Georgetown and CDS 2022-2023. Despite later headers saying 2021-2022, B1/B2 p3 specify October 19, 2022; C1 p7 and C9 p9 specify fall 2022; G1 p18 specifies 2023-2024 costs; and the H1 selector p20 marks 2022-2023. Enrollment, admissions, scores, expenses and aid differ from the actual 2021-2022 source. These dated tables establish the year; no adjacent-year data were copied.

3. **2022-2023 C1 versus B2, pp3 and 7.** C1 does not print an all-gender total. Following the assembler's established C1 rule, its gender rows produce applied **26,638**, admitted **3,257**, enrolled **1,578** (men 626 + 2; women 948 + 2). B2's separate degree-seeking first-time column totals **1,603**. This source inconsistency remains unresolved; B2 was not substituted for admissions, and no extra 25 students were inferred. B1 all-undergraduate enrollment is **7,900**; B2 race data use the rightmost all-undergraduates column, which includes degree- and non-degree-seeking students and sums to 7,900.

4. **Full-time plus part-time C1 enrollment.** Published gender enrollment uses the sum required by the field definition, not just full-time counts. Nonzero part-time rows were included: 2017-2018 p7 women 858 + 1 = 859; 2018-2019 p7 women 924 + 3 = 927; 2019-2020 p7 men 697 + 1 = 698 and women 882 + 2 = 884; 2020-2021 p7 men 689 + 22 = 711 and women 864 + 17 = 881; 2021-2022 p7 men 631 + 3 = 634 and women 950 + 1 = 951; 2022-2023 p7 as above; 2023-2024 p6 men 630 + 1 = 631; 2024-2025 p8 men 660 + 1 = 661 and women 898 + 2 = 900. In 2025-2026 p9 the explicit gender enrollment totals 673 and 909 are used; women include 908 full-time + 1 part-time. Blank cells were not recoded as zero.

5. **Other/unknown gender, 2024-2025 p8 and 2025-2026 p9.** The 2024-2025 source explicitly prints unknown-gender applied/admitted/enrolled counts 261/28/14, and 2025-2026 prints unknown-sex counts 220/22/7. These were retained as raw extraction evidence. Published admissions totals include them; the site's supported men/women fields need not sum to the totals. Blank another-gender rows were omitted.

6. **2016-2017 old SAT, p8.** The source explicitly requests the old SAT scale. Its Critical Reading 660/760 was omitted because the supported field is Evidence-Based Reading and Writing. The printed SAT math 660/760, SAT submission 73%, ACT composite 30/34 and ACT submission 47% were added. The retained math values are on the old scale, so direct cross-year comparison has that limitation. No score conversion or new-scale reading estimate was attempted.

7. **Unreported test medians/composites.** 2016-2017 p8 and 2017-2018 / 2018-2019 pp9-10 do not report a SAT composite; it remains absent. Medians remain absent through 2022-2023, including the visibly blank p50 column in the 2022-2023 p9 table. The abbreviated Evidence-Based Reading row in that form is the standard C9 SAT reading/writing assessment, distinct from the 2016 old Critical Reading row. In 2025-2026 p12 the unusual SAT composite p25 **1,405** is explicitly printed and was preserved exactly, alongside p50 1,480 and p75 1,530.

8. **Costs use G1's undergraduate column and printed year.** The 2022-2023 CDS p18 reports **2023-2024** tuition $64,896, required fees $186 and undergraduate room/board **$20,458**, not the first-year-only $19,750. The derived sum is $85,540. The 2025-2026 CDS p22 reports **2026-2027** tuition $74,520, fees $212 and undergraduate food/housing **$23,004**, not the first-year-only $22,180. The derived sum is $97,736. These totals follow the site's tuition + required fees + room/board convention, excluding other G5 expenses.

9. **Aid uses all full-time undergraduates.** For 2022-2023 pp20-21, the selected aid year is 2022-2023; H2 A/D/H are **7,143 / 2,347 / 2,347**, J is **$52,089**, and K is **$49,384**. Derived proportions are 0.3286 receiving aid and 1.0 fully met. For 2025-2026 pp25-26, the source selects **2025-2026 estimated** aid; A/D/H are **7,372 / 2,122 / 2,122**, J **$63,415**, K **$58,163**. Derived proportions are 0.2878 and 1.0. First-year columns were not used. H2 populations differ from B1's all-undergraduate headcounts, which include part-time and non-degree students.

10. **2025-2026 enrollment and race, pp3-4.** B1 reports 7,908 undergraduates, 11,997 graduate/professional students and total 19,905. B2 uses the rightmost degree- plus non-degree-seeking undergraduate column (7,908), not the middle degree-seeking-only column (7,618). C7 levels were visually verified at 2022-2023 p8 and 2025-2026 pp10-11; they do not require changing the preserved profile.

## Remaining gaps and retrieval results

- No missing CDS years remain within 2016-2017 through the newest linked 2025-2026. The official archive did not list 2026-2027 at retrieval.
- Early action is offered, but C22 gives dates and policy rather than application/admission counts: 2016-2017 p11; 2017-2018, 2018-2019 and 2019-2020 p12; 2020-2021 and 2021-2022 p13; 2022-2023 p11; 2023-2024 p10; 2024-2025 p14; 2025-2026 p15. C21 does not supply an offered early-decision cohort. No zero ED/EA counts were invented.
- No supported all-undergraduate residency headcounts were found for either new year. F1 percentages and C1 first-year-only residency tables were not used to infer them. Existing legacy residency fields were preserved; this pass does not establish their original provenance.
- Unreported score fields and the 2016 unsupported reading/writing mapping remain absent as described above. The 2022-2023 C1/B2 first-year mismatch remains a source caveat.
- **No unresolved file retrieval failures.** All ten official Box shares resolved to static PDFs and downloaded directly; no HTML response was accepted. Initial sandboxed archive retrieval failed with `ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it`; the authorized network retry succeeded. Initial sandboxed page preparation failed because `C:\Users\grove\AppData\Local\uv\cache\sdists-v9\.git` returned `Access is denied. (os error 5)`; the authorized installed-runtime retry succeeded. Neither failure left a missing source or evidence page.

## Validation

`python -I scripts/cds/validate.py georgetown`:

```text
georgetown: ok (0 errors, 0 warnings)
```

All ten reconciled finals have zero unresolved conflicts and zero single-source fields. A preservation audit confirms the profile is unchanged, no existing year or numeric leaf was deleted, and the only changed existing numeric leaves are the four documented 2021-2022 admissions fields. Scoped `git diff --check` passes. Global schema/type checks and local page review are assigned to the parent agent.
