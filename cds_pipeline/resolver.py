from __future__ import annotations

from pathlib import Path
import json

from .utils import extract_year_from_filename, normalize_token


def _college_data_root() -> Path:
    return Path("College-Data")


def _config_path(slug: str) -> Path:
    return Path(__file__).resolve().parent / "configs" / f"{normalize_token(slug)}.json"


def _configured_directory_aliases(slug: str) -> list[str]:
    path = _config_path(slug)
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    aliases = payload.get("source_hints", {}).get("directory_names", [])
    if not isinstance(aliases, list):
        return []
    return [normalize_token(str(alias)) for alias in aliases if str(alias).strip()]


def _configured_slug_for_directory(token: str) -> str | None:
    config_dir = Path(__file__).resolve().parent / "configs"
    if not config_dir.exists():
        return None

    normalized_token = normalize_token(token)
    for config_path in config_dir.glob("*.json"):
        slug = normalize_token(config_path.stem)
        aliases = set(_configured_directory_aliases(slug))
        if normalized_token in aliases:
            return slug
    return None


def resolve_target(target: str) -> list[dict[str, str]]:
    path = Path(target)
    if path.exists():
        return _resolve_path(path)
    return _resolve_school_slug(target)


def _resolve_path(path: Path) -> list[dict[str, str]]:
    if path.is_file():
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a PDF file, got: {path}")
        slug = _configured_slug_for_directory(path.parent.name) or normalize_token(path.parent.name or path.stem)
        return [
            {
                "pdf_path": str(path),
                "school_slug": slug,
                "year": extract_year_from_filename(path.name),
            }
        ]

    pdfs = sorted(p for p in path.iterdir() if p.suffix.lower() == ".pdf")
    if not pdfs:
        raise ValueError(f"No PDFs found in {path}")

    slug = _configured_slug_for_directory(path.name) or normalize_token(path.name)
    return [
        {
            "pdf_path": str(pdf),
            "school_slug": slug,
            "year": extract_year_from_filename(pdf.name),
        }
        for pdf in pdfs
    ]


def _resolve_school_slug(slug: str) -> list[dict[str, str]]:
    normalized = normalize_token(slug)
    root = _college_data_root()
    if not root.exists():
        raise ValueError("College-Data directory not found")

    configured_aliases = set(_configured_directory_aliases(normalized))
    matches: list[Path] = []
    for child in root.iterdir():
        if not child.is_dir():
            continue
        token = normalize_token(child.name)
        if token in configured_aliases:
            matches.append(child)
            continue
        if token == normalized or normalized in token or token in normalized:
            matches.append(child)

    if not matches:
        raise ValueError(f"Could not resolve school slug: {slug}")

    best = sorted(matches, key=lambda item: len(normalize_token(item.name)))[0]
    resolved = _resolve_path(best)
    for item in resolved:
        item["school_slug"] = normalized
    return resolved
