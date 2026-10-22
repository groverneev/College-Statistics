# Colby College data expansion, 2026-10-22

**Result: no new data added.** `src/data/schools/colbycollege.json` is unchanged (1 year, 41 numeric leaves, excluding the profile). Of the target years 2016-2017 through 2025-2026, only 2019-2020 has a retrievable Common Data Set, and it was already on the site. No other CDS year after 2015-2016 could be found officially, from a mirror, or in the Wayback Machine.

No app code, registry, shared scripts, worktrees, or commits were touched. Only this document and gitignored `College-Data/colbycollege/` evidence were written.

## Year coverage

| CDS year | Status | Source |
| --- | --- | --- |
| 2016-2017 | **Missing** | None found |
| 2017-2018 | **Missing** | None found |
| 2018-2019 | **Missing** | None found |
| 2019-2020 | Already on site, re-verified | [collegedata.fyi archive PDF](https://api.collegedata.fyi/storage/v1/object/public/sources/colby/2019-20/004c7ad5028d9eba38c2baf6bd0bbcba9e9e50627e3e6d1657174205f33ad42b.pdf) (SHA-256 `004c7ad5…d33ad42b`, 32 pages). Cover reads "Common Data Set 2019-2020" and A1 names Colby College. Also the only file College Transitions links ([Drive copy](https://drive.google.com/file/d/1jsGkWYBrDSeg9RZMKVUM-9uMzA50rZi4/view)). |
| 2020-2021 | **Missing** | None found |
| 2021-2022 | **Missing** | None found |
| 2022-2023 | **Missing** | A Google Groups thread mentions a file "Colby College CDS 2022-2023.pdf" but gives no link. |
| 2023-2024 | **Missing** | None found |
| 2024-2025 | **Missing** | None found |
| 2025-2026 | **Missing** | None found |

The 2019-2020 file is not a Colby-hosted copy: it is a third-party archive, so it is non-official in `sources.json`. It was not re-downloaded or re-extracted this run.

## What was searched

- **Colby official site.** `colby.edu` returns HTTP 403 to every direct fetch (bot wall, with and without a browser user agent and referer), so Colby pages were read only through the Wayback Machine.
  - The IR page as archived July 2017 (`web.archive.org/web/20170726000532/http://www.colby.edu/administration_cs/ir/`) lists CDS files from 2001 through **2015-2016** (`Final-15-16-CDS.pdf`) and nothing newer.
  - The CDX index for `colby.edu/wp-content/uploads/*` filtered to names containing "cds" returns the same set, 2001 through `Final-15-16-CDS.pdf`. Those files were all migrated to `wp-content/uploads/2018/06/`. No 2016-2017 or later file exists in the index. Guessed names (`Final-16-17-CDS`, `CDS_2020-2021`, and similar) returned nothing.
  - The current IR "External Surveys" page ([archived 2025-09-12](https://web.archive.org/web/2025/https://www.colby.edu/people/offices-directory/institutional-research/sample-page/)) links only a 2008 US News submission, with no CDS.
  - `afa.colby.edu/apply/college-profile/` (archived 2026-01-23) has no CDS link.
- **Mirrors.**
  - [College Transitions repository](https://www.collegetransitions.com/dataverse/common-data-set-repository/): Colby has cells for 2017-18 through 2025-26 but only the 2019-20 cell has a link.
  - The National Test Prep archive has an empty Colby row.
  - [collegedata.fyi](https://www.collegedata.fyi/schools/colby): 2019-20 only.
  - Kaggle and CollegeVine pages give no file links.
- **Web search** (standard and extended) found nothing newer than 2015-2016 on `colby.edu`. Third-party posts state that Colby has not published a CDS since 2016 ([Koppelman Group](https://www.koppelmangroup.com/blog/2023/11/23/how-to-get-into-colby-college)); the 2019-2020 file shows Colby still completes the form but does not post it.

Discovery files are kept in `College-Data/colbycollege/discovery/`.

## Extraction, reconciliation, values resolved by hand

No new extraction was run, since there were no new files. The two-extractor Claude/Codex step and `compare.py`/`resolve.py` therefore had nothing to reconcile, and no values were resolved manually. As a consistency check, `derive_year()` applied to the existing `2019-2020.final.json` (54 agreed values, 0 conflicts, 0 single-source) reproduces the site's 2019-2020 JSON exactly, so no fields were missing for that year.

## Validation

- `python -I scripts/cds/validate.py colbycollege`: ok (0 errors, 0 warnings).

## Remaining limitations

- Nine of ten target years have no obtainable source. If the user can supply the files (Colby's IR office or a family/applicant copy), run the add-college workflow from step 3 for each; 2022-2023 is known to exist somewhere.
- The only year on site comes from an unofficial archive, not `colby.edu`.
