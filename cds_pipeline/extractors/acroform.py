from __future__ import annotations

from pypdf import PdfReader

from .base import BaseExtractor, ExtractionResult


class AcroFormExtractor(BaseExtractor):
    name = "AcroFormExtractor"

    def extract(self, pdf_path: str, config: dict[str, object]) -> ExtractionResult:
        reader = PdfReader(pdf_path)
        fields = reader.get_fields() or {}
        form_fields = {
            key: str(value.get("/V", "")).strip()
            for key, value in fields.items()
            if str(value.get("/V", "")).strip()
        }
        page_texts = [page.extract_text() or "" for page in reader.pages]

        return ExtractionResult(
            extractor=self.name,
            payload={
                "form_fields": form_fields,
                "page_texts": page_texts,
                "full_text": "\n".join(page_texts),
            },
            notes=[],
        )
