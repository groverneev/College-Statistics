from __future__ import annotations

import io

from .base import BaseExtractor, ExtractionResult


class OcrFallbackExtractor(BaseExtractor):
    name = "OcrFallbackExtractor"

    def extract(self, pdf_path: str, config: dict[str, object]) -> ExtractionResult:
        notes: list[str] = []
        ocr_texts: list[str] = []

        try:
            import fitz  # type: ignore
            import pytesseract  # type: ignore
            from PIL import Image  # type: ignore

            document = fitz.open(pdf_path)
            for page in document:
                pixmap = page.get_pixmap(dpi=160, alpha=False)
                image = Image.open(io.BytesIO(pixmap.tobytes("png")))
                ocr_texts.append(pytesseract.image_to_string(image))
            document.close()
        except Exception as exc:  # pragma: no cover - optional dependency path
            notes.append(f"OCR unavailable or failed: {exc}")

        return ExtractionResult(
            extractor=self.name,
            payload={
                "ocr_page_texts": ocr_texts,
                "ocr_full_text": "\n".join(ocr_texts),
            },
            notes=notes,
        )
