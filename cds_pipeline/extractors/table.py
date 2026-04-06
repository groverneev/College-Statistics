from __future__ import annotations

from .base import BaseExtractor, ExtractionResult


class TableExtractor(BaseExtractor):
    name = "TableExtractor"

    def extract(self, pdf_path: str, config: dict[str, object]) -> ExtractionResult:
        notes: list[str] = []
        tables: list[dict[str, object]] = []

        try:
            import pdfplumber  # type: ignore

            with pdfplumber.open(pdf_path) as pdf:
                for page_number, page in enumerate(pdf.pages, start=1):
                    for table_index, table in enumerate(page.extract_tables()):
                        normalized_rows: list[list[str]] = []
                        for row in table or []:
                            normalized_rows.append(
                                [str(cell).strip() if cell is not None else "" for cell in row]
                            )
                        if normalized_rows:
                            tables.append(
                                {
                                    "page": page_number,
                                    "table_index": table_index,
                                    "rows": normalized_rows,
                                }
                            )
        except Exception as exc:  # pragma: no cover - dependency/runtime path
            notes.append(f"pdfplumber table extraction failed: {exc}")

        return ExtractionResult(
            extractor=self.name,
            payload={"tables": tables},
            notes=notes,
        )
