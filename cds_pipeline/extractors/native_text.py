from __future__ import annotations

from pypdf import PdfReader

from .base import BaseExtractor, ExtractionResult


class NativeTextExtractor(BaseExtractor):
    name = "NativeTextExtractor"

    def extract(self, pdf_path: str, config: dict[str, object]) -> ExtractionResult:
        notes: list[str] = []
        blocks: list[dict[str, object]] = []
        page_texts: list[str] = []

        try:
            import fitz  # type: ignore

            document = fitz.open(pdf_path)
            for page_index, page in enumerate(document):
                page_texts.append(page.get_text("text"))
                for block in page.get_text("blocks"):
                    x0, y0, x1, y1, text, *_ = block
                    text_value = str(text).strip()
                    if text_value:
                        blocks.append(
                            {
                                "page": page_index + 1,
                                "bbox": [x0, y0, x1, y1],
                                "text": text_value,
                            }
                        )
            document.close()
        except Exception as exc:  # pragma: no cover - optional dependency path
            notes.append(f"PyMuPDF unavailable or failed: {exc}")
            reader = PdfReader(pdf_path)
            page_texts = [page.extract_text() or "" for page in reader.pages]

        return ExtractionResult(
            extractor=self.name,
            payload={
                "page_texts": page_texts,
                "full_text": "\n".join(page_texts),
                "blocks": blocks,
            },
            notes=notes,
        )
