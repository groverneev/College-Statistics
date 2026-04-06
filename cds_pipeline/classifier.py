from __future__ import annotations

from typing import Any

import fitz  # type: ignore


def classify_pdf(pdf_path: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
    document = fitz.open(pdf_path)
    try:
        page_count = len(document)
    finally:
        document.close()
    extractor_chain = ["VisionLLMExtractor"]

    return {
        "document_type": "vision_pdf",
        "page_count": page_count,
        "extractor_chain": extractor_chain,
    }
