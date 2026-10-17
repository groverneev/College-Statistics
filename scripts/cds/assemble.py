from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import SCHOOLS_DIR, YEAR_RE, extract_dir, load_json, school_dir, write_json  # noqa: E402
from fields import derive_factors, derive_year  # noqa: E402


def final_values(path: Path, allow_single: bool) -> dict:
    final = load_json(path)
    if final.get("conflicts"):
        raise SystemExit(f"{path.name}: unresolved conflicts {sorted(final['conflicts'])}")
    if final.get("single_source") and not allow_single:
        raise SystemExit(
            f"{path.name}: single-source fields {sorted(final['single_source'])}; "
            "confirm each against the page and move it into values (or drop it)"
        )
    entries = {**final.get("single_source", {}), **final["values"]} if allow_single else final["values"]
    return {key: entry["value"] for key, entry in entries.items()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("--name", help="required when creating a new school")
    parser.add_argument("--allow-single", action="store_true")
    args = parser.parse_args()

    target = SCHOOLS_DIR / f"{args.slug}.json"
    school = load_json(target) if target.exists() else None
    if school is None:
        if not args.name:
            raise SystemExit("new school: pass --name")
        school = {"name": args.name, "slug": args.slug, "years": {}}

    finals = sorted(extract_dir(args.slug).glob("*.final.json"))
    if not finals:
        raise SystemExit("no *.final.json files; run compare.py first")

    factors_by_year: dict[str, dict] = {}
    for path in finals:
        year = path.name.split(".")[0]
        if not YEAR_RE.match(year):
            continue
        values = final_values(path, args.allow_single)
        school["years"][year] = derive_year(values)
        if factors := derive_factors(values):
            factors_by_year[year] = factors
        print(f"{year}: {len(values)} values")

    school["years"] = dict(sorted(school["years"].items()))

    if factors_by_year:
        year = max(factors_by_year)
        current = school.get("profile", {}).get("admissionsFactors", {})
        if current.get("sourceYear", "") <= year:
            source = next(iter(sorted(school_dir(args.slug).glob(f"{args.slug}-cds-{year}.*"))), None)
            school.setdefault("profile", {})["admissionsFactors"] = {
                "sourceYear": year,
                "sourcePdf": f"College-Data/{args.slug}/{source.name}" if source else "",
                "section": "C7",
                **factors_by_year[year],
            }

    ordered = {"name": school["name"], "slug": school["slug"]}
    if "profile" in school:
        ordered["profile"] = school["profile"]
    ordered["years"] = school["years"]
    write_json(target, ordered)
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
