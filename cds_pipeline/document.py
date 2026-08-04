from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
from typing import Any

from .models import (
    BoundingBox,
    DocumentArtifact,
    PIPELINE_VERSION,
    PageArtifact,
    TableArtifact,
    WordArtifact,
)
from .specs import DOMAIN_SPECS, domains_for_page, extract_question_ids
from .utils import extract_year_candidates, extract_year_from_filename, sha256_file


MIN_NATIVE_TEXT_CHARS = 100
MIN_NATIVE_TEXT_QUALITY = 0.55


def _text_quality(text: str) -> float:
    compact = "".join(character for character in text if not character.isspace())
    if not compact:
        return 0.0
    readable = sum(character.isalnum() or character in "$%.,:;()[]-/&'\"" for character in compact)
    density = min(1.0, len(compact) / MIN_NATIVE_TEXT_CHARS)
    return round((readable / len(compact)) * density, 4)


def _is_native_text(text: str) -> bool:
    return len(text.strip()) >= MIN_NATIVE_TEXT_CHARS and _text_quality(text) >= MIN_NATIVE_TEXT_QUALITY


def _extract_words(page: Any) -> list[WordArtifact]:
    words: list[WordArtifact] = []
    for item in page.get_text("words", sort=True):
        if len(item) < 5 or not str(item[4]).strip():
            continue
        words.append(
            WordArtifact(
                text=str(item[4]),
                bbox=BoundingBox(x0=item[0], y0=item[1], x1=item[2], y1=item[3]),
                block=int(item[5]) if len(item) > 5 else None,
                line=int(item[6]) if len(item) > 6 else None,
            )
        )
    return words


def _extract_tables(page: Any) -> tuple[list[TableArtifact], list[str]]:
    warnings: list[str] = []
    tables: list[TableArtifact] = []
    try:
        finder = page.find_tables()
        for table in finder.tables:
            bbox = None
            if table.bbox:
                bbox = BoundingBox(
                    x0=table.bbox[0],
                    y0=table.bbox[1],
                    x1=table.bbox[2],
                    y1=table.bbox[3],
                )
            rows = [
                [None if value is None else str(value).strip() for value in row]
                for row in table.extract()
            ]
            tables.append(TableArtifact(bbox=bbox, rows=rows))
    except Exception as exc:
        warnings.append(f"Native table extraction failed: {exc}")
    return tables, warnings


def _classify_document(texts: list[str], question_ids: set[str]) -> tuple[str, float]:
    sample = "\n".join(texts[:8]).lower()
    phrase_score = 0.65 if "common data set" in sample else 0.0
    target_ids = set().union(*(spec.question_ids for spec in DOMAIN_SPECS))
    anchor_hits = len(question_ids.intersection(target_ids))
    anchor_score = min(0.35, anchor_hits * 0.035)
    section_letters = {question[0] for question in question_ids}
    section_score = 0.1 if len(section_letters.intersection({"B", "C", "G", "H"})) >= 3 else 0.0
    # Spreadsheet-generated CDS files often collapse "Common Data Set" into
    # image lettering or omit it entirely, while retaining the stable section
    # question identifiers. That multi-section signature is stronger evidence
    # than filename or keyword matching.
    strong_cds_signature = anchor_hits >= 5 and len(
        section_letters.intersection({"B", "C", "G", "H"})
    ) >= 3
    score = min(1.0, phrase_score + anchor_score + section_score)
    if strong_cds_signature:
        score = max(score, 0.85)
    if score >= 0.55:
        return "cds", round(score, 3)
    supplemental_terms = (
        "tuition",
        "financial aid",
        "enrollment report",
        "institutional research",
    )
    if any(term in sample for term in supplemental_terms):
        return "supplemental", round(max(score, 0.35), 3)
    return "unknown", round(score, 3)


def _school_match_score(school_name: str, texts: list[str]) -> float:
    stopwords = {
        "the",
        "of",
        "at",
        "and",
        "university",
        "college",
        "school",
        "campus",
        "state",
    }
    name_tokens = {
        token
        for token in re.findall(r"[a-z0-9]+", school_name.lower())
        if token not in stopwords and len(token) >= 3
    }
    if not name_tokens:
        return 0.0
    body_tokens = set(re.findall(r"[a-z0-9]+", "\n".join(texts[:8]).lower()))
    return round(len(name_tokens.intersection(body_tokens)) / len(name_tokens), 3)


def _detect_academic_year(
    texts: list[str], filename: str
) -> tuple[str | None, list[str], list[str], bool, bool]:
    warnings: list[str] = []
    body_counts: Counter[str] = Counter()
    for index, text in enumerate(texts[:8]):
        weight = 4 if "common data set" in text.lower() else max(1, 3 - index // 3)
        for candidate in extract_year_candidates(text, allow_short=False):
            body_counts[candidate] += weight

    filename_year = extract_year_from_filename(filename)
    candidates = [year for year, _ in body_counts.most_common()]
    if filename_year != "unknown" and filename_year not in candidates:
        candidates.append(filename_year)

    if body_counts:
        chosen = body_counts.most_common(1)[0][0]
        if filename_year != "unknown" and filename_year != chosen:
            warnings.append(
                f"Filename suggests {filename_year}, but document body suggests {chosen}."
            )
        return chosen, candidates, warnings, True, filename_year != "unknown" and filename_year != chosen
    if filename_year != "unknown":
        start_year = filename_year[:4]
        body = "\n".join(texts)
        reporting_hits = len(
            re.findall(
                rf"\b(?:Fall|October\s+15,?)\s+{re.escape(start_year)}\b",
                body,
                flags=re.IGNORECASE,
            )
        )
        has_core_cds_sections = bool(
            re.search(r"(?m)^\s*B1\.", body) and re.search(r"(?m)^\s*C1\.", body)
        )
        if reporting_hits >= 2 and has_core_cds_sections:
            return filename_year, candidates, warnings, True, False
        warnings.append("Academic year was inferred from the filename because the body had no clear year.")
        return filename_year, candidates, warnings, False, False
    warnings.append("Academic year could not be determined.")
    return None, candidates, warnings, False, False


def refresh_document_identity(artifact: DocumentArtifact) -> DocumentArtifact:
    texts = [page.text for page in artifact.pages]
    all_questions = {
        question for page in artifact.pages for question in page.question_ids
    }
    document_type, classification_score = _classify_document(texts, all_questions)
    academic_year, year_candidates, year_warnings, year_verified, year_conflict = (
        _detect_academic_year(texts, artifact.filename)
    )
    artifact.document_type = document_type
    artifact.classification_score = classification_score
    artifact.school_match_score = _school_match_score(artifact.school_name, texts)
    artifact.academic_year = academic_year
    artifact.year_candidates = year_candidates
    artifact.year_verified = year_verified
    artifact.year_conflict = year_conflict
    artifact.question_ids = sorted(all_questions)
    for warning in year_warnings:
        if warning not in artifact.warnings:
            artifact.warnings.append(warning)
    return artifact


def _render_page(page: Any, path: Path, dpi: int) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    pixmap = page.get_pixmap(dpi=dpi, alpha=False)
    path.write_bytes(pixmap.tobytes("png"))
    return str(path.resolve())


def analyze_pdf(
    pdf_path: Path,
    *,
    school_name: str,
    school_slug: str,
    document_dir: Path,
    render_dpi: int = 180,
    render_visual_evidence: bool = True,
) -> DocumentArtifact:
    try:
        import fitz  # type: ignore
    except Exception as exc:  # pragma: no cover - dependency guard
        raise RuntimeError(f"PyMuPDF is required. Install it with: pip install pymupdf>=1.27: {exc}") from exc

    digest = sha256_file(pdf_path)
    document_id = f"sha256:{digest}"
    cache_path = document_dir / "document.json"
    if cache_path.exists():
        try:
            cached = DocumentArtifact.model_validate_json(cache_path.read_text(encoding="utf-8"))
            if cached.sha256 == digest and cached.pipeline_version == PIPELINE_VERSION:
                return cached
        except Exception:
            pass

    pdf = fitz.open(pdf_path)
    try:
        texts = [page.get_text("text", sort=True) for page in pdf]
        page_questions = [extract_question_ids(text) for text in texts]
        all_questions = {question for questions in page_questions for question in questions}
        document_type, classification_score = _classify_document(texts, all_questions)
        school_match_score = _school_match_score(school_name, texts)
        academic_year, year_candidates, year_warnings, year_verified, year_conflict = (
            _detect_academic_year(texts, pdf_path.name)
        )

        native_pages = [_is_native_text(text) for text in texts]
        text_page_count = sum(native_pages)
        scanned_document = bool(texts) and text_page_count < max(1, len(texts) * 0.2)

        page_domains = [domains_for_page(text, questions) for text, questions in zip(texts, page_questions)]
        routed_indexes = {index for index, domains in enumerate(page_domains) if domains}
        # A CDS table often continues onto the next page without repeating its question number.
        continuation_indexes = {index + 1 for index in routed_indexes if index + 1 < len(texts)}
        routed_indexes.update(continuation_indexes)
        for index in sorted(continuation_indexes):
            if (
                index > 0
                and not page_questions[index]
                and page_domains[index - 1]
                and (not page_domains[index] or "continued" in texts[index].lower())
            ):
                page_domains[index] = list(page_domains[index - 1])

        if scanned_document:
            routed_indexes = set(range(len(texts)))

        pages: list[PageArtifact] = []
        ocr_pending: list[int] = []
        image_dir = document_dir / "page-images"
        for index in sorted(routed_indexes):
            page = pdf[index]
            native = native_pages[index]
            requires_ocr = not native
            visual_domain = any(
                spec.name in page_domains[index] and spec.visual_evidence for spec in DOMAIN_SPECS
            )
            image_path = None
            if requires_ocr or (render_visual_evidence and visual_domain):
                image_path = _render_page(page, image_dir / f"page-{index + 1:03d}.png", render_dpi)
            if requires_ocr:
                ocr_pending.append(index + 1)

            tables: list[TableArtifact] = []
            table_warnings: list[str] = []
            if native:
                tables, table_warnings = _extract_tables(page)

            pages.append(
                PageArtifact(
                    page=index + 1,
                    width=float(page.rect.width),
                    height=float(page.rect.height),
                    text=texts[index],
                    text_chars=len(texts[index].strip()),
                    text_quality=_text_quality(texts[index]),
                    question_ids=page_questions[index],
                    domains=page_domains[index],
                    words=_extract_words(page) if native else [],
                    tables=tables,
                    image_path=image_path,
                    ocr_required=requires_ocr,
                    warnings=table_warnings,
                )
            )

        warnings = list(year_warnings)
        if document_type == "unknown":
            warnings.append("Document was not recognized as a CDS or supported supplemental source.")
        if school_match_score < 0.5:
            warnings.append(
                f"Document text weakly matches the requested institution ({school_match_score:.2f})."
            )
        if scanned_document:
            warnings.append("Document is image-based and requires OCR before section routing is reliable.")

        artifact = DocumentArtifact(
            document_id=document_id,
            source_path=str(pdf_path.resolve()),
            filename=pdf_path.name,
            sha256=digest,
            size_bytes=pdf_path.stat().st_size,
            page_count=len(pdf),
            school_name=school_name,
            school_slug=school_slug,
            school_match_score=school_match_score,
            academic_year=academic_year,
            year_candidates=year_candidates,
            year_verified=year_verified,
            year_conflict=year_conflict,
            document_type=document_type,
            classification_score=classification_score,
            text_page_count=text_page_count,
            question_ids=sorted(all_questions),
            routed_pages=sorted(index + 1 for index in routed_indexes),
            ocr_pending_pages=ocr_pending,
            pages=pages,
            warnings=warnings,
        )
        document_dir.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(artifact.model_dump_json(indent=2) + "\n", encoding="utf-8")
        return artifact
    finally:
        pdf.close()
