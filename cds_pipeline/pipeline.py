from __future__ import annotations

from pathlib import Path
from typing import Any

from .classifier import classify_pdf
from .config import load_config
from .exporter import export_school_json
from .extractors import VisionLLMExtractor
from .normalizer import normalize_document
from .review import build_review_payload, review_markdown
from .utils import ensure_dir, write_json
from .validator import validate_document


EXTRACTOR_REGISTRY = {
    "VisionLLMExtractor": VisionLLMExtractor,
}


def _merge_raw_payload(target: dict[str, Any], payload: dict[str, Any]) -> None:
    for key, value in payload.items():
        if value in (None, "", [], {}):
            continue
        if key not in target:
            target[key] = value
            continue

        existing = target[key]
        if isinstance(existing, dict) and isinstance(value, dict):
            existing.update(value)
        elif isinstance(existing, list) and isinstance(value, list):
            existing.extend(value)
        elif not existing:
            target[key] = value


def _candidate_workspace(base_dir: str | Path, school_slug: str) -> Path:
    return Path(base_dir) / school_slug


def extract_documents(
    resolved_documents: list[dict[str, str]],
    *,
    explicit_config: str | None = None,
    workspace_dir: str | Path = ".cds_pipeline",
    enable_vision: bool | None = None,
) -> dict[str, Any]:
    if not resolved_documents:
        raise ValueError("No documents resolved for extraction.")

    school_slug = resolved_documents[0]["school_slug"]
    config = load_config(school_slug, explicit_config=explicit_config)
    if enable_vision is not None:
        vision_config = dict(config.get("vision", {}))
        vision_config["enabled"] = enable_vision
        config["vision"] = vision_config
    school_name = config.get("school_name", school_slug.replace("-", " ").title())

    documents: list[dict[str, Any]] = []
    workspace = _candidate_workspace(workspace_dir, school_slug)
    ensure_dir(workspace)

    for resolved in resolved_documents:
        pdf_path = resolved["pdf_path"]
        year = resolved["year"]
        classification = classify_pdf(pdf_path, config)

        raw_payload: dict[str, Any] = {}
        extractors_used: list[str] = []
        extractor_notes: list[str] = []

        for extractor_name in classification["extractor_chain"]:
            extractor_cls = EXTRACTOR_REGISTRY[extractor_name]
            result = extractor_cls().extract(pdf_path, config)
            extractors_used.append(result.extractor)
            extractor_notes.extend(result.notes)
            _merge_raw_payload(raw_payload, result.payload)

        data, field_meta = normalize_document(raw_payload, config)
        validation = validate_document(data, field_meta)
        documents.append(
            {
                "school_slug": school_slug,
                "school_name": school_name,
                "year": year,
                "source_path": pdf_path,
                "classification": classification,
                "extractors_used": extractors_used,
                "extractor_notes": extractor_notes,
                "raw_payload_summary": {
                    "vision_sections": raw_payload.get("vision_sections", {}),
                    "vision_missing_sections": raw_payload.get("vision_missing_sections", []),
                    "vision_notes": raw_payload.get("vision_notes", []),
                    "vision_rendered_page_count": raw_payload.get("vision_rendered_page_count", 0),
                },
                "data": data,
                "field_meta": field_meta,
                "validation": validation,
            }
        )

    ordered_documents = sorted(documents, key=lambda item: item["year"])
    candidate = {
        "school_slug": school_slug,
        "school_name": school_name,
        "workspace": str(workspace),
        "documents": ordered_documents,
        "years": {document["year"]: document["data"] for document in ordered_documents},
    }
    review_payload = build_review_payload(candidate)
    candidate["review"] = review_payload
    candidate["export_preview"] = export_school_json(candidate)

    write_json(workspace / "candidate.json", candidate)
    write_json(workspace / "review.json", review_payload)
    (workspace / "review.md").write_text(review_markdown(review_payload), encoding="utf-8")

    return {
        "workspace": str(workspace),
        "candidate": candidate,
        "review": review_payload,
    }
