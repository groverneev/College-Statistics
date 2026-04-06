from __future__ import annotations

from typing import Any

from pypdf import PdfReader


def classify_pdf(pdf_path: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
    reader = PdfReader(pdf_path)
    page_text_lengths: list[int] = []
    image_count = 0
    table_signals = 0

    for page in reader.pages:
        text = page.extract_text() or ""
        page_text_lengths.append(len(text))
        image_count += len(page.images)
        if any(token in text for token in ["G1", "H2", "B2", "C9", "Required Fees", "Room and Board"]):
            table_signals += 1

    fields = reader.get_fields() or {}
    page_count = len(reader.pages)
    avg_text = sum(page_text_lengths) / page_count if page_count else 0

    if fields:
        doc_type = "acroform"
    elif avg_text < 80 and image_count >= max(1, page_count // 2):
        doc_type = "scanned"
    elif table_signals >= max(1, page_count // 4):
        doc_type = "layout_sensitive"
    else:
        doc_type = "native_text"

    extractor_chain_map = {
        "acroform": [
            "AcroFormExtractor",
            "VisionLLMExtractor",
            "TableExtractor",
            "NativeTextExtractor",
            "StructuredLayoutExtractor",
            "OcrFallbackExtractor",
        ],
        "native_text": [
            "VisionLLMExtractor",
            "TableExtractor",
            "NativeTextExtractor",
            "StructuredLayoutExtractor",
            "OcrFallbackExtractor",
        ],
        "layout_sensitive": [
            "VisionLLMExtractor",
            "TableExtractor",
            "StructuredLayoutExtractor",
            "NativeTextExtractor",
            "OcrFallbackExtractor",
        ],
        "scanned": [
            "VisionLLMExtractor",
            "OcrFallbackExtractor",
            "TableExtractor",
            "StructuredLayoutExtractor",
            "NativeTextExtractor",
        ],
    }

    hints = config.get("source_hints", {}) if config else {}
    preferred = hints.get("preferred_extractor")
    extractor_chain = extractor_chain_map[doc_type]
    vision_enabled = bool((config or {}).get("vision", {}).get("enabled", True))
    if not vision_enabled:
        extractor_chain = [name for name in extractor_chain if name != "VisionLLMExtractor"]
    if preferred and preferred in extractor_chain:
        extractor_chain = [preferred, *[name for name in extractor_chain if name != preferred]]

    return {
        "document_type": doc_type,
        "page_count": page_count,
        "avg_text_chars": round(avg_text, 2),
        "image_count": image_count,
        "field_count": len(fields),
        "table_signals": table_signals,
        "extractor_chain": extractor_chain,
    }
