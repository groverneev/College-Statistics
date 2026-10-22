# Penn State University Park CDS expansion - 2026-10-21

Expanded Penn State from five to ten CDS years, continuously covering **2016-2017 through 2025-2026**. Added **163 numeric fields**, bringing the year-data total from 182 to 345. Counts include derived totals and rates, excluding admissions-factor profiles. The 2025-2026 C7 profile replaces the previous source attribution; its 18 factor ratings are unchanged.

Only Codex was used. No Claude model, commits, worktrees, application code, or school-registration changes were involved. Existing years' non-cost data remain equal to the original school JSON. Five existing cost records were corrected to the workflow's public-school tuition basis after a separate independent source check.

## Sources and years added

The [official Penn State CDS archive](https://opair.psu.edu/institutional-research/projects/cds/) currently lists 2020-2021 through 2025-2026. Historical reports were recovered from the university's hosted files, Wayback's original HTML, and one original-file mirror.

| Added CDS year | Numeric fields | Source |
| --- | ---: | --- |
| 2016-2017 | 28 | [Wayback snapshot of the official University Park all-sections HTML CDS](https://web.archive.org/web/20171023160347id_/https://budget.psu.edu/CDSRedesign/cds.aspx?reportindicator=allSections&Location=UP&AY=20162017&displayNewTuition=y) |
| 2017-2018 | 30 | [Official university-hosted PDF](https://cpb-us-e1.wpmucdn.com/sites.psu.edu/dist/d/114442/files/2022/11/CDS-2017-2018-University-Park-1.pdf) |
| 2018-2019 | 30 | [Original-file mirror](https://drive.google.com/file/d/1JTypD30eBPVzpfZedkmOcCGLTFUwpAdY/view), linked by the [College Transitions repository](https://www.collegetransitions.com/dataverse/common-data-set-repository) |
| 2019-2020 | 30 | [Official university-hosted PDF](https://bpb-us-e1.wpmucdn.com/sites.psu.edu/dist/d/114442/files/2019/04/CDS-2019-2020-University-Park.pdf) |
| 2025-2026 | 45 | [Official PDF, version 3](https://opair.psu.edu/files/2026/09/CDS_2025_2026_UniversityPark_v3.pdf) |

Every source identifies Penn State University Park and the correct CDS year internally. The 2016-2017 source is HTML, not a PDF: extraction `page: 1` explicitly denotes the single archived HTML document. Its heading and selected aid-year input were also verified in the collaborative browser. The 2017-2018 PDF has a corrupted embedded-font text encoding; source-page images were used, excluding appended old-version tables. The 2018-2019 mirror identifies the year in its institutional-enrollment and admissions tables; no figures came from an aggregator's summary.

Original downloads, SHA-256 hashes, URLs, retrieval information, HTML, page text, rendered images, independent extractions, and reconciliation evidence are retained in git-ignored `College-Data/pennstate/`. `sources.json` includes the 2016-2017 HTML entry with its actual format. The recovered HTML is not represented as an original PDF.

## Independent extraction and manual decisions

The parent Codex agent independently transcribed `<year>.manual.json`; a separate Codex child independently wrote `<year>.codex.json` without reading manual, final, or published school JSON values. Both used `scripts/cds/fields.py` definitions. This is two independent Codex passes, not different model families. Source images and actual HTML cells were used to address layout and population ambiguities.

`compare.py --left manual --right codex` produced **224 agreed fields, eight single-source fields, and zero numeric conflicts**. All eight single-source fields were the enrolled gender counts below. The second extractor omitted them because C1 prints separate attendance-status rows; the field definition explicitly requests full-time plus part-time. After checking both rows, the values were accepted with `resolve.py`, leaving no unresolved fields. All-gender totals and rates were derived by the assembler.

| CDS year | Source location | Accepted men enrolled | Accepted women enrolled |
| --- | --- | ---: | ---: |
| 2016-2017 | HTML C1, document 1 | 4,296 full-time + 37 part-time = **4,333** | 4,149 + 17 = **4,166** |
| 2017-2018 | PDF p8, C1 | 3,906 + 19 = **3,925** | 3,926 + 12 = **3,938** |
| 2018-2019 | PDF p5, C1 | 4,056 + 14 = **4,070** | 3,999 + 6 = **4,005** |
| 2019-2020 | PDF p7, C1 | 4,135 + 15 = **4,150** | 4,170 + 11 = **4,181** |

Other source-page checks and omissions:

- **Historical B2:** 2016-2017 HTML B2, 2017-2018 pp4-5, 2018-2019 pp2-3, and 2019-2020 p3 leave the total-undergraduate race column blank. Degree-seeking-only counts are a narrower population and were omitted by both extractions. B1 still supplies total enrollment for every added year. The existing 2020-2021/2021-2022 degree-seeking race data were not changed; their existing caveat is retained.
- **2016-2017 C9, HTML:** Critical Reading 530/630 belongs to the pre-redesign SAT; it is not published as Evidence-Based Reading and Writing. Retained printed Math 560/670, ACT Composite 25/29, SAT submission 67.90%, and ACT submission 22.29%. No SAT composite was inferred.
- **2017-2018 p12; 2018-2019 p9; 2019-2020 p10:** retained the printed section and ACT percentiles. SAT composite is absent or blank and was not calculated by summing percentiles. No historical medians were invented.
- **2016-2017 HTML C7 and 2017-2018 p10:** religious affiliation is N/A and omitted. These incomplete historical factor sets do not replace the complete latest profile.
- **2025-2026 p10, C1:** the residency table explicitly prints totals **106,547 applied, 58,952 admitted, 9,148 enrolled**. Gender inputs also include **121 unknown-sex applicants, 63 admits, and one enrolled**. These are first-year residency counts, not all-undergraduate residency counts, so they do not populate `demographics.byResidency`.
- **2025-2026 pp5-6:** B1 gives **42,822 undergraduates, 7,748 graduate students, 50,570 overall**. B2 has a populated total-undergraduates column; those nine race counts are used and sum to 42,822.
- **2025-2026 pp12-14:** all 18 C7 factors were visually checked; C9 prints SAT Composite **1280/1340/1410**, EBRW **630/670/710**, Math **630/670/720**, ACT Composite **28/30/32**, SAT submission **28.60%**, and ACT submission **4.98%**.
- **ED/EA and residency:** ED is not offered; qualifying EA application/admit counts and all-undergraduate residency headcounts are unreported. These fields remain absent. F1 percentages were not converted into headcounts for any new year.

## Cost corrections to existing years

The original 2020-2021 through 2024-2025 records used the G1 out-of-state tuition row. New years follow the workflow's public-school in-state/in-district rule, so keeping those original entries would create false jumps in the cost trend. Current official PDFs were downloaded, and two independent Codex passes checked the **Undergraduates** column and page images before applying cost-only corrections. Both passes agreed on all 15 source amounts. The audit is in `existing-costs.manual.json`, `existing-costs.codex.json`, and `existing-cost-corrections.json`.

| CDS year | Official source and PDF page | Tuition before | In-district tuition after | Fees | Food/housing | Recomputed three-component total |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2020-2021 | [PDF](https://opair.psu.edu/files/2022/11/CDS_2020-2021_MASTER_UP-1.pdf), p18 | $35,946 | **$18,368** | $530 | $12,744 | $31,642 |
| 2021-2022 | [PDF](https://opair.psu.edu/files/2022/11/CDS_2021-2022_MASTER_University-Park.pdf), p18 | $35,946 | **$18,368** | $530 | $12,744 | $31,642 |
| 2022-2023 | [PDF](https://opair.psu.edu/files/2023/07/CDS_2022-2023_University-Park_Final.pdf), p25 | $38,102 | **$19,286** | **$549.48** | $12,984 | $32,819.48 |
| 2023-2024 | [PDF](https://opair.psu.edu/files/2024/10/CDS_2023-2024_UniversityPark_Final1.pdf), pp37-38 | $39,626 | **$19,672** | $562 | $13,030 | $33,264 |
| 2024-2025 | [PDF, version 2](https://opair.psu.edu/files/2025/06/CDS_2024_2025_UniversityPark_v2.pdf), p25 | $41,212 | **$20,066** | $578 | $15,044 | $35,688 |

For 2022-2023, p25 visibly prints conflicting undergraduate tuition: **$19,286 in-district** and **$18,286 in-state/out-of-district**. The explicitly reported in-district cell is permitted by the field definition and is used; the other cell was not silently repaired. The $549 fee was corrected to the printed **$549.48**, preserving cents. Room/board and all other existing-year sections remain unchanged. Derived monetary totals follow the existing assembler's numeric-sum convention; the table displays currency to cents.

## Reporting periods and remaining limitations

Records are keyed by CDS year. G1 costs and H2 aid retain their own printed reporting periods:

- **2016-2017:** HTML G1 explicitly labels 2017-2018 costs; H1 selects **2015-2016 final** aid. H2 full-time-undergraduate A/D/H = 39,294/17,685/1,423; J/K = $11,498/$7,685.
- **2017-2018:** G1 p21 explicitly labels **2017-2018** costs while the next year's costs are unavailable. H1 p23 selects **2016-2017 final**; H2 p24 A/D/H = 39,883/17,527/5,234; J/K = $10,783/$6,629.
- **2018-2019:** G1 p17 labels **2019-2020** costs. H1 p18 selects **2017-2018 final**; H2 p19 A/D/H = 39,683/17,399/5,370; J/K = $11,007/$6,599.
- **2019-2020:** G0 requests 2020-2021 but G1 p18 explicitly labels its populated costs **2019-2020**. H1 p21 selects **2018-2019 final**; H2 p22 A/D/H = 39,267/16,985/5,466; J/K = $11,497/$6,755.
- **2020-2021:** G1 p18 explicitly reports **2021-2022** costs.
- **2021-2022, 2022-2023, 2023-2024:** G1 requests the following year but marks those costs unavailable. Populated fallback cells are retained as printed; they are not asserted to be final next-year rates. For 2023-2024 the actual table is on p38; its availability instructions are on p37.
- **2024-2025:** p25's red note explicitly says the data reflect **2024-2025 costs** because 2025-2026 costs are unavailable.
- **2025-2026:** G1 p27 explicitly reports **2026-2027** costs ($20,878 tuition, $640 fees, $15,968 food/housing). H1 p30 selects **2024-2025 Final**; H2 pp31-32 A/D/H = 41,448/15,350/6,421; J/K = $15,591/$9,703. H2's population differs from B1 and is retained as reported.

No CDS year is missing in the target interval. Blank race columns, historical SAT composites/medians, ED/EA counts, and unreported residency headcounts remain absent. Prior 2020-2021 through 2024-2025 residency estimates already present in the site were left unchanged, with their original methodology caveat clarified in the profile notes. No new residency estimates were introduced.

## Validation

- `python -I scripts/cds/validate.py pennstate`: **0 errors, 0 warnings** after cost normalization.
- `bun run validate`: **all 100 school files valid**.
- `bun run typecheck`: passed.
- `git diff --check`: passed.
- Equality checks confirmed existing Penn State non-cost year data, all original Tulane/Chicago years, and the four pre-existing user-edited schools were preserved.
- Local school-page verification and the combined completion report are recorded in [the Codex-only expansion summary](data-expansion-codex-only-2026-10-21.md).
