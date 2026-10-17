from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "College-Data"
SCHOOLS_DIR = ROOT / "src" / "data" / "schools"
INDEX_TS = SCHOOLS_DIR / "index.ts"

YEAR_RE = re.compile(r"^(\d{4})-(\d{4})$")


def school_dir(slug: str) -> Path:
    return RAW_DIR / slug


def extract_dir(slug: str) -> Path:
    return school_dir(slug) / "extract"


def work_dir(slug: str) -> Path:
    return school_dir(slug) / "work"


def check_year(year: str) -> str:
    match = YEAR_RE.match(year)
    if not match or int(match.group(2)) != int(match.group(1)) + 1:
        raise SystemExit(f"year must look like 2024-2025, got {year!r}")
    return year


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def get_path(data: dict, dotted: str) -> Any:
    node: Any = data
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def set_path(data: dict, dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    node = data
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def flatten(data: Any, prefix: str = "") -> dict[str, Any]:
    if not isinstance(data, dict):
        return {prefix: data}
    out: dict[str, Any] = {}
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        out.update(flatten(value, path))
    return out
