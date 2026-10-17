from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import INDEX_TS, SCHOOLS_DIR  # noqa: E402


def identifier(slug: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", slug) + "Data"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("--color", required=True, help="primary brand color, e.g. #5F259F")
    parser.add_argument("--aliases", default="", help="comma-separated search aliases")
    args = parser.parse_args()

    if not (SCHOOLS_DIR / f"{args.slug}.json").exists():
        raise SystemExit(f"missing src/data/schools/{args.slug}.json")
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", args.color):
        raise SystemExit("color must be #RRGGBB")

    source = INDEX_TS.read_text(encoding="utf-8")
    if f'"./{args.slug}.json"' in source:
        print(f"{args.slug} already registered")
        return

    name = identifier(args.slug)
    imports = list(re.finditer(r'^import \w+ from "\./[\w-]+\.json";\n', source, re.MULTILINE))
    if not imports:
        raise SystemExit("could not find JSON imports in index.ts")
    at = imports[-1].end()
    source = source[:at] + f'import {name} from "./{args.slug}.json";\n' + source[at:]

    array_end = re.search(r"(export const allSchools: SchoolData\[\] = \[\n(?:.*\n)*?)\];", source)
    if not array_end:
        raise SystemExit("could not find allSchools array")
    at = array_end.end(1)
    source = source[:at] + f"  {name} as SchoolData,\n" + source[at:]

    meta_end = re.search(r"(export const SCHOOL_METADATA: Record<string, SchoolMetadata> = \{\n(?:.*\n)*?)\};", source)
    if not meta_end:
        raise SystemExit("could not find SCHOOL_METADATA")
    aliases = [alias.strip() for alias in args.aliases.split(",") if alias.strip()]
    entry = f"  {args.slug}: {{\n    aliases: {json.dumps(aliases)},\n    color: \"{args.color.upper()}\",\n  }},\n"
    at = meta_end.end(1)
    source = source[:at] + entry + source[at:]

    INDEX_TS.write_text(source, encoding="utf-8")
    print(f"registered {args.slug} as {name}")


if __name__ == "__main__":
    main()
