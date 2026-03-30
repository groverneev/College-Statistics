from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ExtractionResult:
    extractor: str
    payload: dict[str, Any]
    notes: list[str]


class BaseExtractor:
    name = "BaseExtractor"

    def extract(self, pdf_path: str, config: dict[str, Any]) -> ExtractionResult:
        raise NotImplementedError
