# Sparse college data expansion using Codex only

Audited all 100 school files and continued with sparse colleges outside the pre-existing Rochester, Swarthmore, Texas A&M, and UC Merced edits. **No Claude model was used in this batch.** Initial child tasks stopped at an account usage limit; after the user's resume instruction, the Codex tasks completed. All work stayed in the main checkout and no commits were created.

| School | Years before | Years after | Numeric fields before | Numeric fields after | Added CDS years |
| --- | ---: | ---: | ---: | ---: | --- |
| Penn State University Park | 5 | 10 | 182 | 345 | 2016-2017 through 2019-2020; 2025-2026 |
| Tulane University | 4 | 10 | 170 | 418 | 2016-2017 through 2021-2022 |
| University of Chicago | 4 | 5 | 172 | 208 | 2025-2026 |

Added **12 school-year records and 447 numeric fields**, including derived totals/rates and excluding C7 profile fields. Penn State and Tulane now cover every CDS year from 2016-2017 through the newest located 2025-2026. Chicago covers 2021-2022 through 2025-2026; its earlier target years predate the first CDS identified by publication-history reporting. Colby remains the sparsest school at one year: no additional verifiable target-period CDS was located, so its record is unchanged. Stevens' official archive currently lists the same four years already present; it was not expanded in this batch.

Each added year was extracted independently by two Codex passes and reconciled with page images or actual archived HTML cells. This does not provide different-model-family independence; it honors the user's instruction not to use Claude. Unsupported fields were not estimated or filled from adjacent years.

Detailed sources, every manual resolution with page numbers, field gaps, and reporting-period caveats:

- [Penn State provenance and source-page decisions](data-expansion-pennstate-2026-10-21.md): 224 agreed fields and eight manually accepted full-time-plus-part-time gender enrollment fields. Five existing cost records were additionally corrected from out-of-state to in-district tuition after two independent checks; 2022-2023 fees retain the printed cents. Existing non-cost data were preserved.
- [Tulane provenance and source-page decisions](data-expansion-tulane-2026-10-21.md): 302 agreements and 27 manually accepted race counts where B1 proves degree-seeking enrollment equals total undergraduate enrollment. Existing years and profile are unchanged.
- [Chicago provenance and source-page decisions](data-expansion-uchicago-2026-10-21.md): 52 agreements; nine degree-seeking-only race counts were dropped because the total-undergraduate column is blank and the populations differ. Existing years are unchanged.

Source caveats remain: blank race/residency data, unreported early-admission counts and SAT statistics, stale form labels, estimated or prior-year aid, and G1 costs from a different reporting year. These limitations are detailed in each school's note and are not treated as reported zeroes.

Verification completed:

- All three scoped CDS validators: **0 errors and 0 warnings**.
- `bun run validate`: **100 school files valid**.
- `bun run typecheck`: passed.
- `git diff --check`: passed.
- All three local school pages loaded successfully; admissions tables include the new years, the chart groups contain data, and the application/enrollment/SAT headlines match the latest school JSON. Chicago's unreported 2025-2026 race summaries display as unavailable.
- Original-year equality checks passed for Tulane and Chicago. Penn State's existing non-cost data were preserved, with the separately documented cost-only corrections.
- Hash checks confirmed the pre-existing Rochester, Swarthmore, Texas A&M, and UC Merced edits were not changed by this batch. Existing documentation was preserved.

Production changes are limited to three school JSON files and the new provenance notes. Download manifests and extraction evidence remain under git-ignored `College-Data/`.
