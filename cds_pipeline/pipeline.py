from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

from .document import analyze_pdf, refresh_document_identity
from .discovery import discover_school
from .downloader import download_discovered_sources
from .extractor import extractor_chain
from .models import (
    BoundingBox,
    DocumentArtifact,
    MetricObservation,
    PacketPage,
    SchoolManifest,
    SectionExtraction,
    SectionPacket,
    TableArtifact,
)
from .native import blocking_paths, extract_packet_native
from .ocr import create_ocr_provider, provider_setup_help
from .resolver import resolve_pdf_paths
from .specs import domains_for_page, extract_question_ids, spec_for_domain, text_for_question_ids
from .utils import humanize_name, read_json, sha256_file, slugify, validate_slug, write_json


EXTRACTION_CACHE_VERSION = "5"


def _document_workspace(workspace: Path, school_slug: str, pdf_path: Path) -> Path:
    return workspace / school_slug / "documents" / sha256_file(pdf_path)[:16]


def _run_ocr(artifact: DocumentArtifact, provider_name: str) -> DocumentArtifact:
    provider = create_ocr_provider(provider_name)
    if provider is None:
        return artifact
    pending: list[int] = []
    for page in artifact.pages:
        if not page.ocr_required:
            continue
        if not page.image_path or not Path(page.image_path).exists():
            page.warnings.append("OCR was required, but no rendered page image exists.")
            pending.append(page.page)
            continue
        try:
            result = provider.extract_page(Path(page.image_path))
        except Exception as exc:
            page.warnings.append(f"OCR failed with {provider.name}: {exc}")
            pending.append(page.page)
            continue
        page.text = result.text
        page.text_chars = len(result.text.strip())
        page.text_quality = 1.0 if result.text.strip() else 0.0
        page.extraction_method = result.method
        page.ocr_confidence = result.confidence
        page.ocr_required = False
        page.question_ids = extract_question_ids(result.text)
        page.domains = domains_for_page(result.text, page.question_ids)
        page.tables = []
        for table in result.tables:
            rows = table.get("rows") if isinstance(table, dict) else None
            if isinstance(rows, list):
                page.tables.append(TableArtifact(rows=rows, method=result.method))
    artifact.ocr_pending_pages = pending
    return refresh_document_identity(artifact)


def _build_packets(
    documents: list[DocumentArtifact],
    *,
    workspace: Path,
    school_name: str,
    school_slug: str,
) -> list[str]:
    grouped: dict[tuple[str, str], list[PacketPage]] = {}
    for document in documents:
        if document.document_type != "cds" or not document.academic_year:
            continue
        pages = sorted(document.pages, key=lambda item: item.page)
        detected_ids = [extract_question_ids(page.text) for page in pages]
        for index, page in enumerate(pages):
            current_question_ids = detected_ids[index]
            inherited_question_ids: list[str] = []
            if not current_question_ids:
                previous = next(
                    (detected_ids[item] for item in range(index - 1, -1, -1) if detected_ids[item]),
                    [],
                )
                following = next(
                    (detected_ids[item] for item in range(index + 1, len(pages)) if detected_ids[item]),
                    [],
                )
                if (
                    previous
                    and following
                    and pages[index + 1].page - page.page <= 1
                    and {item[0] for item in previous + following if item}
                    == {previous[0][0]}
                ):
                    # CDS sections frequently continue onto an unnumbered page.
                    # When it is bracketed by adjacent questions from the same
                    # lettered section, inherit the preceding question instead
                    # of trusting broad keywords such as "first-time".
                    inherited_question_ids = previous
            if current_question_ids or page.extraction_method != "native":
                current_domains = domains_for_page(page.text, current_question_ids)
            elif inherited_question_ids:
                current_domains = domains_for_page(page.text, inherited_question_ids)
            elif page.domains:
                # Native multi-page sections often omit the repeated question ID.
                # Keep inherited text continuations even when the PDF table finder
                # cannot reconstruct a formal table (common for flattened forms).
                current_domains = list(page.domains)
            else:
                current_domains = []
            for domain in current_domains:
                spec = spec_for_domain(domain)
                routed_text = (
                    page.text
                    if inherited_question_ids
                    else text_for_question_ids(page.text, spec.question_ids)
                )
                if current_question_ids and not routed_text:
                    continue
                grouped.setdefault((document.academic_year, domain), []).append(
                    PacketPage(
                        document_id=document.document_id,
                        source_path=document.source_path,
                        page=page.page,
                        text=routed_text,
                        question_ids=sorted(
                            set(current_question_ids or inherited_question_ids).intersection(
                                spec.question_ids
                            )
                        ),
                        words=page.words,
                        tables=page.tables,
                        image_path=page.image_path,
                        extraction_method=page.extraction_method,
                    )
                )

    packet_paths: list[str] = []
    packet_root = workspace / school_slug / "packets"
    factor_years = sorted(
        academic_year for academic_year, domain in grouped if domain == "admissions_factors"
    )
    retained_factor_years = set(factor_years[-2:])
    for (academic_year, domain), pages in sorted(grouped.items()):
        if domain == "admissions_factors" and academic_year not in retained_factor_years:
            continue
        unique_pages: dict[tuple[str, int], PacketPage] = {
            (page.document_id, page.page): page for page in pages
        }
        packet = SectionPacket(
            school_name=school_name,
            school_slug=school_slug,
            academic_year=academic_year,
            domain=domain,
            metric_paths=list(spec_for_domain(domain).metric_paths),
            pages=sorted(unique_pages.values(), key=lambda item: (item.source_path, item.page)),
        )
        path = packet_root / academic_year / f"{domain}.json"
        write_json(path, packet.model_dump(mode="json"))
        packet_paths.append(str(path.resolve()))
    return packet_paths


def _extract_packets(
    packet_paths: list[str],
    *,
    extractor_name: str,
    model: str | None,
    jobs: int,
) -> tuple[list[str], int]:
    output_paths: list[str] = []
    cache_hits = 0
    chain = extractor_chain(extractor_name, model=model)
    worker_count = max(1, jobs)
    if any(provider_name == "local" for provider_name, _ in chain):
        worker_count = min(
            worker_count,
            max(1, int(os.environ.get("CDS_LOCAL_EXTRACTION_JOBS", "1"))),
        )

    cache_config = {
        "extraction_cache_version": EXTRACTION_CACHE_VERSION,
        "extractor": extractor_name,
        "model": model,
        "local_model": os.environ.get("CDS_LOCAL_EXTRACTION_MODEL", "gemma4:12b"),
        "vision_model": os.environ.get("CDS_LOCAL_VISION_MODEL", "qwen3.5:9b"),
        "local_context": os.environ.get("CDS_OLLAMA_CONTEXT", "16384"),
        "codex_enabled": os.environ.get("CDS_ENABLE_CODEX_FALLBACK", ""),
        "hosted_model": model or "gpt-5-mini",
        "providers": [provider_name for provider_name, _ in chain],
    }

    def extract_one(packet_path: str) -> tuple[str, bool]:
        path = Path(packet_path)
        packet = SectionPacket.model_validate(read_json(path))
        output_path = Path(str(path).replace("\\packets\\", "\\extractions\\").replace("/packets/", "/extractions/"))
        cache_path = output_path.with_suffix(".cache.json")
        signature_payload = {
            **cache_config,
            "pipeline_version": packet.pipeline_version,
            "packet_sha256": sha256_file(path),
        }
        signature = sha256(
            json.dumps(signature_payload, sort_keys=True).encode("utf-8")
        ).hexdigest()
        if cache_path.exists():
            try:
                cached = read_json(cache_path)
                if cached.get("signature") == signature:
                    extraction = SectionExtraction.model_validate(cached["extraction"])
                    write_json(output_path, extraction.model_dump(mode="json"))
                    return str(output_path.resolve()), True
            except (KeyError, TypeError, ValueError):
                pass
        native_extraction, native_complete = extract_packet_native(packet)
        extraction = native_extraction if native_complete else None
        failures: list[str] = []
        if not native_complete:
            native_paths = {observation.path for observation in native_extraction.observations}
            for provider_name, extract in chain:
                try:
                    candidate = extract(packet)
                except Exception as exc:
                    failures.append(f"{provider_name}: {exc}")
                    continue
                candidate.observations = [
                    observation
                    for observation in candidate.observations
                    if observation.path not in native_paths
                ]
                candidate.observations = (
                    native_extraction.observations + candidate.observations
                )
                candidate.notes = native_extraction.notes + candidate.notes
                extraction = candidate
                required_paths = blocking_paths(packet)
                returned_paths = {
                    observation.path
                    for observation in candidate.observations
                    if observation.value is not None and not observation.review_required
                }
                if not any(
                    observation.review_required for observation in candidate.observations
                ) and required_paths.issubset(returned_paths):
                    break
                failures.append(
                    f"{provider_name}: returned review-required or incomplete observations"
                )
        if extraction is None:
            raise RuntimeError(
                f"Every structured extractor failed for {packet.academic_year}/{packet.domain}: "
                + " | ".join(failures)
            )
        returned_paths = {
            observation.path
            for observation in extraction.observations
            if observation.value is not None and not observation.review_required
        }
        observations_by_path = {
            observation.path: observation for observation in extraction.observations
        }
        for missing_path in sorted(blocking_paths(packet) - returned_paths):
            existing = observations_by_path.get(missing_path)
            if existing is not None:
                existing.review_required = True
                existing.notes = "Required metric was not recovered by any configured extractor."
                continue
            extraction.observations.append(
                MetricObservation(
                    path=missing_path,
                    value=None,
                    evidence=[],
                    method="llm",
                    confidence=0,
                    review_required=True,
                    notes="Required metric was not recovered by any configured extractor.",
                )
            )
        if failures:
            extraction.notes.append("Extractor fallback history: " + " | ".join(failures))
        write_json(output_path, extraction.model_dump(mode="json"))
        write_json(
            cache_path,
            {
                "signature": signature,
                "config": signature_payload,
                "extraction": extraction.model_dump(mode="json"),
            },
        )
        return str(output_path.resolve()), False

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(extract_one, path) for path in packet_paths]
        for future in as_completed(futures):
            output_path, hit = future.result()
            output_paths.append(output_path)
            cache_hits += int(hit)
    return sorted(output_paths), cache_hits


def add_school(
    target: str,
    *,
    school_name: str | None = None,
    school_slug: str | None = None,
    workspace_dir: str | Path = ".cds_pipeline",
    jobs: int = 4,
    ocr_provider: str = "auto",
    extractor: str = "none",
    model: str | None = None,
    include_unknown: bool = False,
    discover_if_missing: bool = True,
    archive_url: str | None = None,
    repository_fallback: bool = True,
    download_years: int | None = 8,
    college_data_dir: str | Path = "College-Data",
) -> SchoolManifest:
    workspace = Path(workspace_dir)
    acquisition_warnings: list[str] = []
    target_path = Path(target)
    if target_path.exists():
        source_root, pdf_paths = resolve_pdf_paths(target)
        name = school_name or humanize_name(source_root.name)
        slug = validate_slug(school_slug or slugify(name))
    else:
        if not discover_if_missing:
            raise ValueError(
                f"Target is not an explicit local path and discovery is disabled: {target}"
            )
        name = school_name or humanize_name(target)
        slug = validate_slug(school_slug or slugify(name))
        discovery = discover_school(
            name,
            school_slug=slug,
            workspace_dir=workspace,
            archive_url=archive_url,
            repository_fallback=repository_fallback,
        )
        source_root, records, download_warnings = download_discovered_sources(
            discovery,
            college_data_dir=college_data_dir,
            years=download_years,
        )
        acquisition_warnings.extend(discovery.warnings)
        acquisition_warnings.extend(download_warnings)
        if not records:
            raise ValueError(
                f"No verified PDF candidates could be downloaded for {name}. "
                f"Inspect {workspace / slug / 'discovery.json'} or provide --archive-url."
            )
        # The downloader may reuse a directory that already contains older CDS
        # files.  Only analyze the records selected for this invocation; scanning
        # the directory again would silently defeat --years and redo the entire
        # local archive.
        pdf_paths = [Path(record.local_path) for record in records]

    # PyMuPDF's table finder can leak table state across documents when invoked
    # concurrently in threads. Native document analysis is inexpensive relative
    # to model inference, so keep it serial for deterministic evidence artifacts.
    documents = [
        analyze_pdf(
            pdf_path,
            school_name=name,
            school_slug=slug,
            document_dir=_document_workspace(workspace, slug, pdf_path),
        )
        for pdf_path in pdf_paths
    ]
    documents.sort(key=lambda item: (item.academic_year or "9999", item.filename))

    if any(document.ocr_pending_pages for document in documents):
        for index, document in enumerate(documents):
            documents[index] = _run_ocr(document, ocr_provider)
            cache_path = (
                workspace
                / slug
                / "documents"
                / document.sha256[:16]
                / "document.json"
            )
            write_json(cache_path, documents[index].model_dump(mode="json"))

    rejected: list[dict[str, Any]] = []
    accepted: list[DocumentArtifact] = []
    for document in documents:
        if document.document_type == "unknown" and not include_unknown:
            rejected.append(
                {
                    "source_path": document.source_path,
                    "reason": (
                        "ocr_required_before_classification"
                        if document.ocr_pending_pages
                        else "not_recognized_as_cds"
                    ),
                    "classification_score": document.classification_score,
                    "ocr_pending_pages": document.ocr_pending_pages,
                }
            )
        else:
            accepted.append(document)

    packet_paths = _build_packets(
        accepted,
        workspace=workspace,
        school_name=name,
        school_slug=slug,
    )
    extraction_paths: list[str] = []
    extraction_cache_hits = 0
    if extractor != "none":
        extraction_paths, extraction_cache_hits = _extract_packets(
            packet_paths,
            extractor_name=extractor,
            model=model,
            jobs=jobs,
        )

    extraction_review = 0
    for extraction_path in extraction_paths:
        extraction_result = SectionExtraction.model_validate(read_json(Path(extraction_path)))
        extraction_review += sum(
            observation.review_required for observation in extraction_result.observations
        )

    warnings: list[str] = list(acquisition_warnings)
    if extraction_review:
        warnings.append(
            f"{extraction_review} extracted observations require review or escalation."
        )
    ocr_pending = sum(len(document.ocr_pending_pages) for document in accepted)
    if ocr_pending:
        warnings.append(f"{ocr_pending} routed pages still require OCR.")
        warnings.extend(provider_setup_help())
    missing_years = sum(document.academic_year is None for document in accepted)
    if missing_years:
        warnings.append(f"{missing_years} accepted documents have no verified academic year.")
    unverified_years = sum(
        document.academic_year is not None and not document.year_verified for document in accepted
    )
    if unverified_years:
        warnings.append(
            f"{unverified_years} accepted documents have a filename-only academic year and require review."
        )
    year_conflicts = sum(document.year_conflict for document in accepted)
    if year_conflicts:
        warnings.append(
            f"{year_conflicts} documents have conflicting filename and body academic years."
        )
    weak_school_matches = sum(document.school_match_score < 0.5 for document in accepted)
    if weak_school_matches:
        warnings.append(
            f"{weak_school_matches} documents weakly match the requested institution and require review."
        )
    cds_documents = [document for document in accepted if document.document_type == "cds"]
    available_domains = {
        domain
        for document in cds_documents
        for page in document.pages
        for domain in page.domains
    }
    expected_domains = {
        "enrollment",
        "admissions",
        "admissions_factors",
        "test_scores",
        "costs",
        "financial_aid",
    }
    missing_domains = sorted(expected_domains - available_domains)
    if not cds_documents:
        warnings.append("No complete Common Data Set document was recognized.")
    elif missing_domains:
        warnings.append("Required CDS sections were not found: " + ", ".join(missing_domains) + ".")

    manifest = SchoolManifest(
        school_name=name,
        school_slug=slug,
        workspace=str((workspace / slug).resolve()),
        documents=accepted,
        packet_paths=packet_paths,
        extraction_paths=extraction_paths,
        extraction_cache_hits=extraction_cache_hits,
        extraction_cache_misses=len(extraction_paths) - extraction_cache_hits,
        rejected_documents=rejected,
        review_required=bool(
            rejected
            or ocr_pending
            or missing_years
            or unverified_years
            or year_conflicts
            or weak_school_matches
            or not cds_documents
            or missing_domains
            or extraction_review
        ),
        warnings=warnings,
    )
    write_json(workspace / slug / "school_manifest.json", manifest.model_dump(mode="json"))
    return manifest
