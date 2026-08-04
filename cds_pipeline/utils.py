from __future__ import annotations

import json
import re
from hashlib import sha256
from pathlib import Path
from typing import Any


def normalize_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def slugify(value: str) -> str:
    return normalize_token(value)


def validate_slug(value: str) -> str:
    if not value or slugify(value) != value:
        raise ValueError(
            "School slug must be a non-empty canonical lowercase alphanumeric value."
        )
    return value


def humanize_name(value: str) -> str:
    value = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", value)
    value = re.sub(r"[-_]+", " ", value)
    return squish(value).title()


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def squish(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_number(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))

    text = str(value).strip()
    if not text:
        return None

    cleaned = (
        text.replace("$", "")
        .replace(",", "")
        .replace("%", "")
        .replace("\u2212", "-")
        .strip()
    )
    if not cleaned:
        return None

    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None

    return int(round(float(match.group(0))))


def parse_percent(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number / 100 if number > 1 else number

    text = str(value).strip()
    if not text:
        return None
    cleaned = text.replace(",", "").replace("%", "").strip()
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    number = float(match.group(0))
    return number / 100 if number > 1 else number


def canonical_academic_year(first: int, second: int | None = None) -> str | None:
    if not 1990 <= first <= 2100:
        return None
    if second is None:
        second = first + 1
    elif second < 100:
        second = (first // 100) * 100 + second
    if second != first + 1:
        return None
    return f"{first:04d}-{second:04d}"


def extract_year_candidates(value: str, *, allow_short: bool = False) -> list[str]:
    candidates: list[str] = []
    patterns = (
        r"(?<!\d)(20\d{2})\s*[-_/]\s*(20\d{2})(?!\d)",
        r"(?<!\d)(20\d{2})\s*[-_/]\s*(\d{2})(?!\d)",
    )
    for pattern in patterns:
        for first, second in re.findall(pattern, value):
            year = canonical_academic_year(int(first), int(second))
            if year and year not in candidates:
                candidates.append(year)

    if allow_short:
        for first, second in re.findall(r"(?<!\d)(\d{2})\s*[-_/]\s*(\d{2})(?!\d)", value):
            first_year = 2000 + int(first)
            year = canonical_academic_year(first_year, int(second))
            if year and year not in candidates:
                candidates.append(year)
        for first, second in re.findall(
            r"(?i)(?:cds|fy)[_\- ]?(\d{2})(\d{2})(?!\d)", value
        ):
            year = canonical_academic_year(2000 + int(first), int(second))
            if year and year not in candidates:
                candidates.append(year)
    return candidates


def extract_year_from_filename(filename: str) -> str:
    allow_short = bool(re.search(r"(?i)cds|common.data|^\d{2}[-_]\d{2}", filename))
    candidates = extract_year_candidates(filename, allow_short=allow_short)
    if candidates:
        return candidates[0]
    if re.search(r"(?i)cds|common.data", filename):
        match = re.search(r"(?<!\d)(20\d{2})(?!\d)", filename)
        if match:
            year = canonical_academic_year(int(match.group(1)))
            if year:
                return year
    return "unknown"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
