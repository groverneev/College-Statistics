from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class FieldMeta:
    value: Any
    confidence: float
    status: str
    source: str
    source_ref: str | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DocumentCandidate:
    school_slug: str
    school_name: str
    year: str
    source_path: str
    classification: dict[str, Any]
    extractors_used: list[str]
    data: dict[str, Any]
    field_meta: dict[str, dict[str, Any]]
    validation: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "school_slug": self.school_slug,
            "school_name": self.school_name,
            "year": self.year,
            "source_path": self.source_path,
            "classification": self.classification,
            "extractors_used": self.extractors_used,
            "data": self.data,
            "field_meta": self.field_meta,
            "validation": self.validation,
        }
