from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


PIPELINE_VERSION = "3.4"


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class WordArtifact(BaseModel):
    text: str
    bbox: BoundingBox
    block: int | None = None
    line: int | None = None


class TableArtifact(BaseModel):
    bbox: BoundingBox | None = None
    rows: list[list[str | None]] = Field(default_factory=list)
    method: str = "pymupdf"


class PageArtifact(BaseModel):
    page: int
    width: float
    height: float
    text: str = ""
    text_chars: int = 0
    text_quality: float = 0.0
    extraction_method: str = "native"
    question_ids: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    words: list[WordArtifact] = Field(default_factory=list)
    tables: list[TableArtifact] = Field(default_factory=list)
    image_path: str | None = None
    ocr_required: bool = False
    ocr_confidence: float | None = None
    warnings: list[str] = Field(default_factory=list)


class DocumentArtifact(BaseModel):
    pipeline_version: str = PIPELINE_VERSION
    document_id: str
    source_path: str
    filename: str
    sha256: str
    size_bytes: int
    page_count: int
    school_name: str
    school_slug: str
    school_match_score: float = 0.0
    academic_year: str | None = None
    year_candidates: list[str] = Field(default_factory=list)
    year_verified: bool = False
    year_conflict: bool = False
    document_type: Literal["cds", "supplemental", "unknown"] = "unknown"
    classification_score: float = 0.0
    text_page_count: int = 0
    question_ids: list[str] = Field(default_factory=list)
    routed_pages: list[int] = Field(default_factory=list)
    ocr_pending_pages: list[int] = Field(default_factory=list)
    pages: list[PageArtifact] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class PacketPage(BaseModel):
    document_id: str
    source_path: str
    page: int
    text: str
    question_ids: list[str] = Field(default_factory=list)
    words: list[WordArtifact] = Field(default_factory=list)
    tables: list[TableArtifact] = Field(default_factory=list)
    image_path: str | None = None
    extraction_method: str = "native"


class SectionPacket(BaseModel):
    pipeline_version: str = PIPELINE_VERSION
    school_name: str
    school_slug: str
    academic_year: str
    domain: str
    metric_paths: list[str]
    pages: list[PacketPage]


class SourceEvidence(BaseModel):
    document_id: str
    page: int
    question_id: str | None = None
    quote: str = Field(min_length=1, max_length=240)
    bbox: BoundingBox | None = None


MetricValue = int | float | str | bool


class MetricObservation(BaseModel):
    path: str
    value: MetricValue | None
    unit: str | None = None
    population: str | None = None
    evidence: list[SourceEvidence]
    method: Literal["native-rule", "llm", "manual", "derived"] = "llm"
    confidence: float = Field(ge=0, le=1)
    review_required: bool = False
    notes: str | None = None


class SectionExtraction(BaseModel):
    observations: list[MetricObservation]
    notes: list[str] = Field(default_factory=list)


class SchoolManifest(BaseModel):
    pipeline_version: str = PIPELINE_VERSION
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    school_name: str
    school_slug: str
    workspace: str
    documents: list[DocumentArtifact]
    packet_paths: list[str] = Field(default_factory=list)
    extraction_paths: list[str] = Field(default_factory=list)
    rejected_documents: list[dict[str, Any]] = Field(default_factory=list)
    review_required: bool = False
    warnings: list[str] = Field(default_factory=list)


class SourceCandidate(BaseModel):
    url: str
    label: str = ""
    academic_year: str | None = None
    discovery_source: Literal["official_site", "college_transitions", "user"]
    discovery_url: str
    official: bool = False
    score: float = 0.0
    notes: list[str] = Field(default_factory=list)


class DiscoveryManifest(BaseModel):
    pipeline_version: str = PIPELINE_VERSION
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    school_name: str
    school_slug: str
    official_site: str | None = None
    official_archive_pages: list[str] = Field(default_factory=list)
    candidates: list[SourceCandidate] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class DownloadRecord(BaseModel):
    source_url: str
    resolved_url: str
    discovery_source: str
    official: bool
    academic_year: str | None = None
    local_path: str
    sha256: str
    size_bytes: int
    content_type: str | None = None
