# Tulane University CDS expansion - 2026-10-21

## Scope and coverage

Added six previously missing CDS years: **2016-2017, 2017-2018, 2018-2019,
2019-2020, 2020-2021, and 2021-2022**. Coverage increases from four to ten
years, continuously from 2016-2017 through 2025-2026.

The pre-existing 2022-2023, 2023-2024, 2024-2025, and 2025-2026 year objects
and the admissions-factor profile are preserved exactly. No app code, school
registry, other school's data, existing documentation, worktrees, or commits
are part of this task.

There are **329 source-field entries** across the six reconciled extractions,
including 108 historical C7 factors and 18 raw H2 inputs. Assembly adds **248
numeric year-data fields**, including derived values. Each new year contains
admissions, test scores, enrollment/race, costs, and financial aid.

## Sources

Discovery: [Tulane Office of Assessment and Institutional Research CDS archive](https://oair.tulane.edu/common-data-set),
checked 2026-10-21 (America/Los_Angeles). This official page provides every
target year and identifies 2025-2026 as the latest CDS. No 2026-2027 CDS was
listed or found in the current-year search. Official files were available, so
direct-file search, Wayback, and mirrors were unnecessary under the skill's
stop-per-year source order.

- [2016-2017 official PDF](https://tulane.box.com/s/34zrujbd4l4h0tucxte5nafzpethoqa4): 31 pages; SHA-256 `93f4944d0ea3cec74df52932af03702118416a593126fc5ecd998148f596b922`.
- [2017-2018 official PDF](https://tulane.box.com/s/3cujcy9px4mfgmigvz3fm68wb1eh0jj2): 32 pages; SHA-256 prefix `1e648e8f8017092e`.
- [2018-2019 official PDF](https://tulane.box.com/s/zwm37ymscy77bx5oh0elusqfcsnl66sz): 30 pages; SHA-256 prefix `9677f29d382c3741`.
- [2019-2020 official PDF](https://tulane.box.com/s/zdns25egfljq26bpvb2kf4f1g21bpvn0): 32 pages; SHA-256 prefix `cd685305707a35c8`.
- [2020-2021 official PDF](https://tulane.box.com/s/skhjuruyk0v39tmr2vhoqerunce8anan): 40 pages; SHA-256 prefix `dd0d031ae5ad4d9f`.
- [2021-2022 official PDF](https://tulane.box.com/s/h7ez09u7tx68wsvxcgt4wt41nwl9vjml): 41 pages; SHA-256 prefix `509d9af1842b19b2`.

Each PDF's first page identifies Tulane University and the correct CDS year.
The previous run's 2016-2017 download was reused. The other five were fetched
with `fetch.py`, using the archive page as referer. Full hashes, resolved Box
URLs, retrieval times, sizes, and page counts are in
`College-Data/tulane/sources.json`. The archive HTML is saved beside it.
All six fetched-file hashes also match the pre-existing `CDS_<year>.pdf`
artifacts byte for byte.

## Extraction and verification

Only Codex was used. No Claude model or Claude CLI was invoked.

`pages.py` generated searchable text and table images. The active Codex agent
read the source pages and wrote `<year>.primary.json`, with a source page and
evidence for each field. Separate `crosscheck.py` Codex CLI runs used
`gpt-6.1-sol` to write `<year>.codex.json` independently from the source files.
Primary extraction did not use those outputs as input. `compare.py --left
primary --right codex` reconciled them. This is two independent Codex passes,
not verification by different model families.

The source-page images were inspected for C7 column placements, B2 population
columns, G1 undergraduate versus first-year costs, H2 full-time-undergraduate
columns, test percentile rows, and stale cohort labels. Per-field evidence,
extractor notes, and reconciliation decisions remain in
`College-Data/tulane/extract/`. The primary transcription helper and original
published JSON snapshot also remain under `College-Data/tulane/`.

## Manual resolutions and source caveats

- **2016-2017, 2017-2018, 2018-2019, B1/B2 p3:** The nine rightmost
  Total Undergraduates race cells are blank; their total cell is a template
  zero. The independent extractor therefore omitted them. Accepted the nine
  printed Degree-Seeking Undergraduates counts per year after checking that
  B1 degree-seeking and total undergraduate counts are identical in every
  gender/attendance column, with no other undergraduates. B2 sums to B1:
  6,377, 6,571, and 6,773. All **27** accepts have explicit reasons in the final
  JSON files. The blank cells are not asserted to contain numbers.
- **2016-2017 C9 p8:** Old SAT Critical Reading 620/710 and Writing 640/720
  are not Evidence-Based Reading and Writing. Omitted `readingWriting` and
  the unreported SAT composite. Retained printed SAT Math 630/710 and ACT
  Composite 29/33. No concordance or percentile addition was performed.
- **2016-2017 C21 p10:** ED is marked No and its counts are blank; no ED
  counts were added. C22 p11 offers EA but supplies no application/admit counts.
- **2017-2018 C9 pp9-10 and 2018-2019 C9 p9:** SAT composite percentiles
  are absent. Retained reported section and ACT percentiles; did not sum SAT
  sections. No p50/median test scores appear in any added year.
- **2019-2020 C1 p6:** The form header says 2019-2020 but the cohort prose
  says Fall 2018. Retained its different current-form values: men/women
  applied 15,647/26,538, admitted 1,999/3,432, enrolled 721/1,100. The actual
  2018-2019 form p7 has 14,621/24,195 applications. C1 enrolled genders differ
  from B1 p3 (722/1,099) by one each; retained each table in its own domain.
- **2020-2021 C9 p12:** Prose says Fall 2019 under the 2020-2021 header.
  Retained SAT 30% (542), ACT 68% (1,229), SAT Composite 1360/1470,
  EBRW 650/730, Math 690/770, ACT Composite 30/33. These differ from the
  actual 2019-2020 C9 p8: SAT 26% (480), ACT 72% (1,320), Composite
  1370/1480. The submission counts are consistent with the current C1 cohort
  of 1,801 after percentage rounding.
- **2020-2021 C21 p15:** Retained ED 3,976 applications / 922 admits despite
  the stale Fall 2019 label. The actual 2019-2020 C21 p10 is 2,163 / 720.
- **G1 undergraduate column:** 2016-2017 p17 reports following-year
  2017-2018 tuition/fees/room-board **47,130 / 3,880 / 14,446**; its first-year
  room-board 13,844 was excluded. 2017-2018 p17 reports 2018-2019
  **50,780 / 4,040 / 15,190**. 2018-2019 p17 reports 2019-2020
  **52,760 / 4,040 / 16,464**; first-year room-board 15,774 was excluded.
  The 2019-2020 p17, 2020-2021 p22, and 2021-2022 p22 forms mark next-year
  costs unavailable and retain printed costs **52,760 / 4,040 / 16,464**,
  **54,766 / 4,086 / 16,232**, and **56,684 / 4,130 / 16,778**, respectively.
  Preserved the numbers actually printed. Source forms can repeat costs;
  these are not newly inferred next-year estimates.
- **H2 full-time-undergraduate column:** 2016-2017 p19 A/D/H =
  **6,793 / 2,142 / 1,407**, J/K = **45,124 / 33,003**;
  2017-2018 pp19-20 **6,540 / 2,105 / 1,461**, **47,540 / 34,996**;
  2018-2019 p19 **7,346 / 2,307 / 1,246**, **47,129 / 36,085**;
  2019-2020 p20 **7,593 / 2,290 / 1,101**, **47,419 / 37,297**;
  2020-2021 p26 **7,661 / 2,215 / 1,335**, **50,930 / 39,617**;
  2021-2022 p26 **7,941 / 2,290 / 1,342**, **51,783 / 40,292**.
  H2 A is retained even where it differs from B1; it is the denominator for
  D/A. H/D determines the share of aid recipients whose need is fully met;
  H2 I is a different statistic. H1 marks current-year aid estimates on
  2016-2017 p19, 2017-2018 p19, 2018-2019 p19, 2019-2020 p19,
  2020-2021 p25, and 2021-2022 p25.

## Gaps

No missing CDS years remain between 2016-2017 and the newest published
2025-2026. Field gaps remain where the source does not report the value:
all-undergraduate residency headcounts, EA application/admit counts, medians,
the 2016-2017 EBRW measure, and 2016-2017 through 2018-2019 SAT composites.
Do not infer residency headcounts from F1 percentages. Historical C7 values
are retained as evidence but do not replace the existing 2025-2026 profile.

## Validation

- Independent comparison: 2016-2017 **41 agreed + 9 manually accepted**;
  2017-2018 **45 + 9**; 2018-2019 **45 + 9**; 2019-2020 **56 + 0**;
  2020-2021 **56 + 0**; 2021-2022 **59 + 0**. Total: **302 agreements,
  27 source-page resolutions, zero numeric conflicts**, and no unresolved
  single-source fields. All six Codex CLI extraction runs completed.
- `python -I scripts/cds/assemble.py tulane --name 'Tulane University'`
  used `fields.py` derivation rules and wrote all six new years.
- `python -I scripts/cds/validate.py tulane`: **0 errors, 0 warnings**.
- Scoped `git diff --check`: passed.
- Preservation audit: all four original year objects and the complete profile
  compare equal to the pre-expansion snapshot. The school JSON diff contains
  additions only. New-year numeric field counts are **37, 41, 41, 43, 43, 43**
  in chronological order, totaling **248**. Audit details are saved in
  `College-Data/tulane/validation-summary.json`.
- Global validation, typecheck, and dev-page review are left to the parent
  task as instructed. No commits were made.

Source caveats above remain even though the validator reports no warnings:
stale cohort labels, estimated aid, H2/B1 population differences, and costs
retained while next-year costs were unavailable.
