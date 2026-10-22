# Sparse college expansion, October 22, 2026

Audited all 100 school JSON files by numeric fields per existing year, excluding profiles. Ohio State (31.25 fields/year) and Georgetown (31.5) were the sparsest records. Earlier research had already documented unavailable additional years for Colby, Stevens, and Chicago. This batch used only GPT/Codex subagents, including independent extraction and reconciliation for both selected schools.

Ohio State expanded from 8 to 10 years and from 250 to 442 numeric fields. Added 2016-2017 and 2025-2026, plus missing historical gender admissions, test scores, aid figures, and Early Action counts. Georgetown expanded from 8 to 10 years and from 252 to 438 numeric fields. Added 2022-2023 and 2025-2026, plus missing historical gender admissions and test scores. Both schools now cover every CDS year from 2016-2017 through the newest report listed by their official archives, 2025-2026.

Together this adds four school-year records and 378 numeric fields, including derived totals and rates. No existing numeric field was deleted. Existing profiles were preserved exactly. There are also 21 documented corrections: 17 Ohio State aid/cost fields and four Georgetown admissions totals/rates. The page-specific source decisions, official URLs, reconciliation results, and remaining gaps are in the individual reports:

- [Ohio State sources, corrections, and limitations](data-expansion-ohiostate-2026-10-22.md).
- [Georgetown sources, corrections, and limitations](data-expansion-georgetown-2026-10-22.md).

Ohio State retains legacy residency estimates and older cost blocks that this expansion did not independently establish. Its scoped validator reports one tuition-decline warning where a corrected undergraduate tuition amount meets the retained older cost convention. Georgetown's scoped validator reports no warnings. Both scoped validators report zero errors. Unsupported source blanks and unavailable measures remain absent; they were not estimated or replaced with zero.

Parent verification:

- `bun run validate`: all 100 school files valid.
- `bun run typecheck`: passed.
- `git diff --check`: passed.
- Baseline comparison: no numeric deletions; exactly 192 Ohio State and 186 Georgetown additions, with exactly the 21 corrections documented above; profiles unchanged.
- Both local pages loaded on the existing development server at port 3457. Each rendered six chart containers and 17 chart marks, with all ten years in its admissions table.
- Georgetown's latest headlines match its JSON: 26,822 applications, 13.5% acceptance, 1,589 enrolled, SAT 1405-1530. Ohio State's match: 81,392 applications, 49.2% acceptance, 8,248 enrolled, SAT 1300-1440.
- The original UC Santa Cruz/Santa Barbara JSON files and their pre-existing provenance note retain their baseline SHA-256 hashes. Concurrent unrelated school edits were left alone.

Source manifests, rendered pages, independent extraction files, resolutions, and merge audits remain under gitignored `College-Data/`. Work stayed in the main checkout. No commits were created.
