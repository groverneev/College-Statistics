from __future__ import annotations

from typing import Any


def build_review_payload(candidate: dict[str, Any]) -> dict[str, Any]:
    years = candidate.get("years", [])
    total_pages = sum(item.get("page_count", 0) for item in years if isinstance(item, dict))
    return {
        "school_slug": candidate.get("school_slug"),
        "school_name": candidate.get("school_name"),
        "year_count": len(years),
        "total_page_count": total_pages,
        "years": years,
    }


def review_markdown(review_payload: dict[str, Any]) -> str:
    lines = [
        f"# Render Summary: {review_payload.get('school_name', review_payload.get('school_slug', 'Unknown'))}",
        "",
        f"- Years: {review_payload.get('year_count', 0)}",
        f"- Total rendered pages: {review_payload.get('total_page_count', 0)}",
        "",
    ]

    for year in review_payload.get("years", []):
        if not isinstance(year, dict):
            continue
        lines.append(f"## {year.get('year', 'unknown')}")
        lines.append(f"- Pages: {year.get('page_count', 0)}")
        lines.append(f"- Manifest: `{year.get('manifest_path', '')}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
