from __future__ import annotations

from typing import Any


def export_school_json(candidate: dict[str, Any]) -> dict[str, Any]:
    years: dict[str, Any] = {}
    for document in candidate.get("documents", []):
        years[document["year"]] = document["data"]

    return {
        "name": candidate.get("school_name"),
        "slug": candidate.get("school_slug"),
        "years": dict(sorted(years.items())),
    }
