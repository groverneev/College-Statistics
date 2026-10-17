from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import check_year, extract_dir, load_json, write_json  # noqa: E402
from fields import FIELDS  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("year")
    parser.add_argument("--accept", nargs="*", default=[], help="keep single-source fields after checking the page")
    parser.add_argument("--drop", nargs="*", default=[], help="discard conflicting or single-source fields")
    parser.add_argument("--set", nargs="*", default=[], metavar="PATH=VALUE", help="record a value read from the page")
    parser.add_argument("--page", type=int, help="page for --set values")
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()

    path = extract_dir(args.slug) / f"{check_year(args.year)}.final.json"
    final = load_json(path)
    resolutions = final.setdefault("resolutions", [])

    for field in args.accept:
        entry = final["single_source"].pop(field, None)
        if entry is None:
            raise SystemExit(f"{field} is not single-source")
        final["values"][field] = {**entry, "resolved": args.reason}
        resolutions.append({"field": field, "action": "accept", "reason": args.reason})

    for field in args.drop:
        final["values"].pop(field, None)
        found = final["single_source"].pop(field, None) or final["conflicts"].pop(field, None)
        if found is None:
            raise SystemExit(f"{field} is not single-source or conflicting")
        resolutions.append({"field": field, "action": "drop", "reason": args.reason})

    for item in args.set:
        field, _, raw = item.partition("=")
        if field not in FIELDS:
            raise SystemExit(f"unknown field {field}")
        value = json.loads(raw) if raw[:1].isdigit() or raw[:1] == "-" else raw
        final["conflicts"].pop(field, None)
        final["single_source"].pop(field, None)
        final["values"][field] = {"value": value, "page": args.page, "resolved": args.reason}
        resolutions.append({"field": field, "action": "set", "value": value, "page": args.page, "reason": args.reason})

    write_json(path, final)
    print(f"{path.name}: {len(final['values'])} values, {len(final['single_source'])} single-source, "
          f"{len(final['conflicts'])} conflicts left")


if __name__ == "__main__":
    main()
