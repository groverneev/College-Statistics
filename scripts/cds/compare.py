from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import SCHOOLS_DIR, check_year, extract_dir, flatten, load_json, write_json  # noqa: E402
from fields import FIELDS, derive_factors, derive_year  # noqa: E402


def same(a, b) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= 1e-6 * max(1, abs(a), abs(b))
    return a == b


def load_extraction(path: Path) -> dict:
    data = load_json(path)
    unknown = sorted(set(data.get("values", {})) - set(FIELDS))
    if unknown:
        raise SystemExit(f"{path.name}: unknown field paths {unknown}")
    return data


def reconcile(slug: str, year: str, left: str, right: str) -> int:
    folder = extract_dir(slug)
    a = load_extraction(folder / f"{year}.{left}.json")
    b = load_extraction(folder / f"{year}.{right}.json")
    av, bv = a["values"], b["values"]

    values: dict = {}
    conflicts: dict = {}
    single: dict = {}
    for path in FIELDS:
        in_a, in_b = path in av, path in bv
        if in_a and in_b:
            if same(av[path]["value"], bv[path]["value"]):
                values[path] = {**av[path], "agreed_by": [left, right]}
            else:
                conflicts[path] = {left: av[path], right: bv[path]}
        elif in_a or in_b:
            who, entry = (left, av[path]) if in_a else (right, bv[path])
            single[path] = {**entry, "only": who}

    final = {
        "year": year,
        "file": a.get("file"),
        "values": values,
        "single_source": single,
        "conflicts": conflicts,
        "notes": {left: a.get("notes", []), right: b.get("notes", [])},
    }
    write_json(folder / f"{year}.final.json", final)

    print(f"{year}: {len(values)} agreed, {len(single)} single-source, {len(conflicts)} conflicts")
    for path, sides in conflicts.items():
        print(f"  CONFLICT {path}: {left}={sides[left]['value']} (p{sides[left].get('page')})"
              f"  {right}={sides[right]['value']} (p{sides[right].get('page')})")
    for path, entry in single.items():
        print(f"  single   {path}: {entry['value']} from {entry['only']} (p{entry.get('page')})")
    return 1 if conflicts or single else 0


def against_site(slug: str, year: str, extractor: str) -> int:
    extraction = load_extraction(extract_dir(slug) / f"{year}.{extractor}.json")
    values = {path: entry["value"] for path, entry in extraction["values"].items()}
    ours = flatten(derive_year(values))
    factors = derive_factors(values)

    school = load_json(SCHOOLS_DIR / f"{slug}.json")
    if year not in school["years"]:
        raise SystemExit(f"{slug}.json has no {year}")
    theirs = flatten(school["years"][year])
    if factors and school.get("profile", {}).get("admissionsFactors", {}).get("sourceYear") == year:
        ours.update({f"factors.{k}": v for k, v in flatten(factors).items()})
        site_factors = school["profile"]["admissionsFactors"]
        theirs.update({f"factors.{k}": v for k, v in flatten({
            "academic": site_factors["academic"], "nonacademic": site_factors["nonacademic"]}).items()})

    match = differ = 0
    for path in sorted(set(ours) | set(theirs)):
        mine, site = ours.get(path), theirs.get(path)
        if mine is not None and site is not None and same(mine, site):
            match += 1
            continue
        differ += 1
        print(f"  {path}: extracted={mine} site={site}")
    print(f"{year}: {match} match, {differ} differ")
    return 1 if differ else 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("year")
    parser.add_argument("--left", default="claude")
    parser.add_argument("--right", default="codex")
    parser.add_argument("--site", metavar="EXTRACTOR", help="diff one extraction against the published school JSON")
    args = parser.parse_args()
    year = check_year(args.year)
    if args.site:
        sys.exit(against_site(args.slug, year, args.site))
    sys.exit(reconcile(args.slug, year, args.left, args.right))


if __name__ == "__main__":
    main()
