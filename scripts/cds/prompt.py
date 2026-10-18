from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import check_year, extract_dir, load_json, school_dir  # noqa: E402
from fields import FIELDS  # noqa: E402


def find_source(slug: str, year: str) -> Path:
    matches = sorted(school_dir(slug).glob(f"{slug}-cds-{year}.*"))
    if not matches:
        raise SystemExit(f"no downloaded file for {slug} {year}; run fetch.py first")
    return matches[0]


def build_prompt(slug: str, year: str, extractor: str) -> str:
    source = find_source(slug, year)
    work = source.parent / "work" / source.stem
    index_path = work / "index.json"
    if not index_path.exists():
        raise SystemExit(f"missing {index_path}; run pages.py on {source.name} first")
    index = load_json(index_path)
    out = extract_dir(slug) / f"{year}.{extractor}.json"

    sections = "\n".join(
        f"  {code}: pages {pages or 'not found by heading search; scan the text files'}"
        for code, pages in index["sections"].items()
    )
    field_lines = "\n".join(f"  {path}: {meaning}" for path, meaning in FIELDS.items())
    scanned = index.get("scanned_pages") or []

    return f"""You are extracting Common Data Set {year} values for {slug} from {source.name}.

Inputs (read-only):
  page text: {work / 'pages'}/NNN.txt (one file per page, 1-based)
  page images: {work / 'img'}/NNN.png (rendered pages; look at these whenever a table's text layout is ambiguous)
  section index (heading search, may be incomplete):
{sections}
  scanned pages with no text layer: {scanned or 'none'}{' -> read these from the PNGs' if scanned else ''}

If a needed page is not rendered, run:
  uv run scripts/cds/pages.py "{source}" --render <SECTIONS>

Write exactly one file: {out}
Format:
{{
  "year": "{year}",
  "file": "{source.name}",
  "extractor": "{extractor}",
  "values": {{
    "<field path>": {{"value": <number or factor level>, "page": <1-based page>, "evidence": "<short verbatim row text>"}}
  }},
  "notes": ["<anything ambiguous, blank, or estimated in the source>"]
}}

Fields (only these paths are allowed):
{field_lines}

Rules:
- Copy numbers exactly as printed. Never estimate, interpolate, or carry a value from another year.
- Leave a field out when the source cell is blank, N/A, or the section is missing. Do not write null or 0 for blanks.
- Write 0 only when the source prints 0.
- Counts are integers without commas. Dollar amounts are numbers without $ or commas; preserve cents when printed.
- Percentages listed as fractions are fractions between 0 and 1.
- Do not compute acceptance rate, yield, totals, or aid percentages; the assembler derives them.
- Check that the page you cite really is this CDS year ({year}); some files contain prior-year tables.
- If two tables could match a field, pick the one the field description names and explain in notes.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("year")
    parser.add_argument("--extractor", default="claude")
    args = parser.parse_args()
    print(build_prompt(args.slug, check_year(args.year), args.extractor))


if __name__ == "__main__":
    main()
