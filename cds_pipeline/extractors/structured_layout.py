from __future__ import annotations

from .base import BaseExtractor, ExtractionResult


class StructuredLayoutExtractor(BaseExtractor):
    name = "StructuredLayoutExtractor"

    def extract(self, pdf_path: str, config: dict[str, object]) -> ExtractionResult:
        notes: list[str] = []
        markdown = ""

        try:
            from docling.document_converter import DocumentConverter  # type: ignore

            converter = DocumentConverter()
            result = converter.convert(pdf_path)
            markdown = result.document.export_to_markdown()
        except Exception as exc:  # pragma: no cover - optional dependency path
            notes.append(f"Docling unavailable or failed: {exc}")

        return ExtractionResult(
            extractor=self.name,
            payload={"structured_markdown": markdown},
            notes=notes,
        )
