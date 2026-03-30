from __future__ import annotations

from typing import Any


def build_review_payload(candidate: dict[str, Any]) -> dict[str, Any]:
    documents = []
    for document in candidate.get("documents", []):
        documents.append(
            {
                "year": document.get("year"),
                "source_path": document.get("source_path"),
                "document_type": document.get("classification", {}).get("document_type"),
                "extractors_used": document.get("extractors_used", []),
                "issue_count": document.get("validation", {}).get("issue_count", 0),
                "issues": document.get("validation", {}).get("issues", []),
                "low_confidence_fields": document.get("validation", {}).get("low_confidence_fields", []),
            }
        )

    total_issues = sum(item.get("issue_count", 0) for item in documents)
    return {
        "school_slug": candidate.get("school_slug"),
        "school_name": candidate.get("school_name"),
        "document_count": len(documents),
        "total_issue_count": total_issues,
        "documents": documents,
    }


def review_markdown(review_payload: dict[str, Any]) -> str:
    lines = [
        f"# Review Summary: {review_payload.get('school_name', review_payload.get('school_slug', 'Unknown'))}",
        "",
        f"- Documents: {review_payload.get('document_count', 0)}",
        f"- Total validation issues: {review_payload.get('total_issue_count', 0)}",
        "",
    ]

    for document in review_payload.get("documents", []):
        lines.append(f"## {document.get('year', 'unknown')}")
        lines.append(f"- Source: `{document.get('source_path', '')}`")
        lines.append(f"- Document type: `{document.get('document_type', 'unknown')}`")
        extractors = ", ".join(document.get("extractors_used", [])) or "none"
        lines.append(f"- Extractors used: {extractors}")
        lines.append(f"- Validation issues: {document.get('issue_count', 0)}")

        low_conf = document.get("low_confidence_fields", [])
        if low_conf:
            lines.append("- Low-confidence fields:")
            for item in low_conf[:12]:
                lines.append(
                    f"  - `{item.get('field')}` ({item.get('status')}, confidence {item.get('confidence')}) from {item.get('source')}"
                )

        issues = document.get("issues", [])
        if issues:
            lines.append("- Issues:")
            for issue in issues[:12]:
                lines.append(f"  - {issue.get('message')}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
