from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .utils import normalize_token


CONFIG_DIR = Path(__file__).resolve().parent / "configs"


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(slug: str, explicit_config: str | None = None) -> dict[str, Any]:
    default_path = CONFIG_DIR / "default.json"
    config = json.loads(default_path.read_text(encoding="utf-8"))

    school_config = CONFIG_DIR / f"{normalize_token(slug)}.json"
    if school_config.exists():
        config = _deep_merge(config, json.loads(school_config.read_text(encoding="utf-8")))

    if explicit_config:
        explicit_path = Path(explicit_config)
        config = _deep_merge(config, json.loads(explicit_path.read_text(encoding="utf-8")))

    config.setdefault("school_slug", normalize_token(slug))
    config.setdefault("school_name", slug.replace("-", " ").title())
    return config
