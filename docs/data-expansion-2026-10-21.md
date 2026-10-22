# Sparse college data expansion

Audited all 100 school files on October 21, 2026. The smallest year counts were Colby (1), Rochester (2), and Swarthmore, Tulane, Chicago, and Stevens (4 each). This update expands Rochester and Swarthmore. No additional Colby CDS from the target period was located through official-site searches, the Wayback PDF index, or the available CDS repositories; its existing 2019-2020 record is unchanged.

| School | Years before | Years after | Numeric fields before | Numeric fields after |
| --- | ---: | ---: | ---: | ---: |
| Swarthmore College | 4 | 10 | 157 | 428 |
| University of Rochester | 2 | 8 | 88 | 256 |

Numeric fields count leaves in `years`, including derived totals and rates. Admissions-factor profiles are excluded from these counts. The update adds 12 school-year records and 439 numeric fields, and adds Swarthmore's 2025-2026 admissions-factor profile. Existing Rochester years are unchanged. Swarthmore's existing years are unchanged except for the SAT correction below.

## Coverage and sources

Each new record was extracted independently with Claude Sonnet 5.5 and Codex gpt-6.1-sol, compared with `scripts/cds/compare.py`, and reconciled against source pages. Page numbers below are 1-based PDF page numbers, including covers. Download manifests, hashes, page text, rendered pages, and extraction/reconciliation files are retained under the git-ignored `College-Data/<slug>/` directories.

Swarthmore now covers every CDS year from **2016-2017 through 2025-2026**. Its [official CDS archive](https://www.swarthmore.edu/institutional-effectiveness-research-assessment/common-data-set) supplies the missing years:

| Added year | Source |
| --- | --- |
| 2016-2017 | [Official archived PDF](https://archive.swarthmore.edu/files/assets/documents/institutional-research/CDS_2016-17-%20Swarthmore%20College.pdf?__raw=1) |
| 2017-2018 | [Official archived PDF](https://archive.swarthmore.edu/files/assets/documents/institutional-research/Swarthmore%20College%202017-18%20CDS.pdf?__raw=1) |
| 2018-2019 | [Official archived PDF](https://archive.swarthmore.edu/files/assets/documents/institutional-research/2018-2019%20Common%20Data%20Set%20Swarthmore%20College.pdf?__raw=1) |
| 2023-2024 | [Official PDF](https://www.swarthmore.edu/sites/default/files/assets/documents/institutional-effectiveness-research-assessment/Swarthmore%20CDS%202023-2024.pdf) |
| 2024-2025 | [PDF linked by the official archive](https://www.swarthmore.edu/sites/default/files/assets/documents/institutional-effectiveness-research-assessment/Swarthmore-CDS-2024-2025-fillable-pdf-version.pdf); the already-downloaded College Transitions copy was used |
| 2025-2026 | [Official PDF](https://www.swarthmore.edu/sites/default/files/assets/documents/institutional-effectiveness-research-assessment/Swarthmore-CDS-2025-26.pdf) |

Rochester now covers **2018-2019 through 2025-2026**, with partial records for the first three years. No 2016-2017 or 2017-2018 report was located in official-site searches, the Wayback PDF index, or the available repositories.

| Added year | Source and coverage |
| --- | --- |
| 2018-2019 | Official A/B/G sections recovered from Wayback: [A](https://web.archive.org/web/20190910212249id_/https://www.rochester.edu/provost/wp-content/uploads/2019/06/CDS-Section-A-18-19-for-website.pdf), [B](https://web.archive.org/web/20190910212251id_/https://www.rochester.edu/provost/wp-content/uploads/2019/06/CDS-Section-B-18-19-for-website-new.pdf), [G](https://web.archive.org/web/20190910212257id_/https://www.rochester.edu/provost/wp-content/uploads/2019/06/CDS-Section-G-18-19-for-website.pdf). Enrollment, race counts, and costs only; matching C/H sections were unavailable. |
| 2019-2020 | [Archived original-file copy](https://api.collegedata.fyi/storage/v1/object/public/sources/university-of-rochester/2020-21/30ae72bf6f747943181444266f82bf0026331c38686bed1ef4295bd8db0a2c2e.pdf), found via [collegedata.fyi](https://www.collegedata.fyi/schools/university-of-rochester/2019-20). Only the explicitly dated 2019-2020 B1/B2 enrollment and race tables on page 2 are included. The assembled mirror contains other years' sections. |
| 2020-2021 | Official [C](https://web.archive.org/web/20211211143822id_/https://www.rochester.edu/provost/wp-content/uploads/2021/10/CDS_2020-2021-C.pdf) and [H](https://web.archive.org/web/20211211143833id_/https://www.rochester.edu/provost/wp-content/uploads/2021/10/CDS_2020-2021-H.pdf) sections recovered from Wayback. Applications, admissions, and aid only. The historical page linked older B/G sections; those were excluded. No test-score or early-admission tables were present in C. |
| 2021-2022 | [Official PDF](https://www.rochester.edu/provost/wp-content/uploads/2022/09/2021-22-Full-Common-Data-Set.pdf) |
| 2022-2023 | [Official PDF](https://www.rochester.edu/provost/wp-content/uploads/2023/05/University-of-Rochester-CDS_2022-2023.pdf) |
| 2023-2024 | [Official PDF](https://www.rochester.edu/provost/wp-content/uploads/2024/05/CDS-2023-2024.pdf) |

## Manual reconciliation and correction

| School/year | PDF pages | Decision |
| --- | --- | --- |
| Swarthmore 2016-2017 | 11 | Omitted SAT Critical Reading 645/720/760 from `sat.readingWriting.p25/p50/p75`: this is the pre-redesign test, not Evidence-Based Reading and Writing. The schema has no separate Critical Reading field. |
| Swarthmore 2025-2026 | 13 | Dropped extractor-computed application/admission/enrollment totals 12,995/977/426. The assembler derives these from the verified men and women rows, as required by the workflow. |
| Swarthmore 2022-2023 (existing record) | 15 | Corrected EBRW p25 from 750 to **710**, p75 from 738 to **770**, and added p50 **750**. The old p25 used the median; the old p75 used the average. The [source](https://archive.swarthmore.edu/files/assets/documents/institutional-research/Swarthmore%20CDS_2022-2023.pdf?__raw=1) explicitly prints 710/750/770 in its 25th/50th/75th columns. |
| Rochester 2019-2020 | 5 | Dropped all nine C1 admissions fields (totals and men/women rows) and all 18 C7 factors from this year because that section explicitly reports Fall 2020. Those factors and the qualifying admissions fields are sourced from the recovered 2020-2021 C section instead. |
| Rochester 2019-2020 | 7-9 | Dropped aid fields A=5,941, D=3,115, H=2,879, average package=$51,250, average need-based grant=$47,250 from this mirror's 2019-2020 record. They are the same H section recovered from the official 2020-2021 page: H1 labels it 2020-21 estimated. The 2018-2019 G section on page 15 was also excluded by both extractors. |
| Rochester 2020-2021 | 1 | Omitted enrolled totals 1,363 (643 men, 720 women). These are labeled full-time only; no matching B1 or part-time counts were recovered. Total enrollment and yield remain unavailable. |
| Rochester 2020-2021 | 2-4 | Accepted H2 full-time-undergraduate COMBINED A=5,941, D=3,115, H=2,879, average package=$51,250, average need-based grant=$47,250. H1 explicitly identifies 2020-21 estimated aid; H2 identifies Fall 2019 recipients. Preserve this reporting-period caveat. |
| Rochester 2021-2022 | 5 | Omitted SAT composite p25=31 and p75=35: the PDF prints ACT-scale values in the SAT row. The ACT composite row is blank, so these were not reassigned to ACT. |
| Rochester 2022-2023 | 18 | Accepted H2 full-time-undergraduate COMBINED A=6,247, D=3,008, H=2,780, average package=$54,616, average need-based grant=$50,333. The heading still says Fall 2020, but every value differs from the 2021-2022 table (A=6,068, D=3,055, H=2,941, package=$53,355, grant=$49,246). Treat the repeated heading as stale and retain values as reported in this CDS. H1 also retains a 2021-22 estimated label; the dates are a source caveat. |

Swarthmore's G1 tables explicitly retain current-year costs while their templates ask for the following year: 2023-2024 page 32, 2024-2025 page 45, and 2025-2026 page 29. The amounts explicitly identified by the source are used. Rochester G1 requests the following year's costs in 2021-2022 and 2022-2023; those printed amounts are used under the site's existing CDS-year convention.

## Remaining limitations and checks

- Rochester 2018-2019 B2, page 2, reports degree-seeking race counts totaling **6,348**, while B1 reports **6,535** total undergraduates. The difference is **187 non-degree students**. Both printed populations are preserved; the CDS validator emits one warning for this difference.
- Rochester 2021-2022 B2 totals 6,568, versus B1's 6,570; both tables are retained as printed.
- Rochester 2022-2023 reports six enrolled students in its unknown-gender column but only one admitted in that column. These printed counts are preserved.
- Rochester's C9 populations are limited to Arts, Sciences & Engineering in 2021-2022 and 2022-2023, and ASE plus dual ASE/Eastman programs in 2023-2024, as the source headings state.
- No residency headcounts were inferred from percentages. Blank, absent, or unsupported fields remain absent.
- `python -I scripts/cds/validate.py swarthmorecollege`: no errors or warnings.
- `python -I scripts/cds/validate.py rochester`: no errors; the one B2/B1 population warning described above.
- `bun run validate`: all 100 school files valid.
- `bun run typecheck`: passed.
- Both local school pages returned HTTP 200. Their five chart sections were present, and the latest-year application and undergraduate enrollment headlines matched the school JSON.
- `git diff --check`: passed. No commits were created.
