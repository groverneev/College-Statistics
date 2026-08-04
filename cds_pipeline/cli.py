from __future__ import annotations

import argparse
import json
from pathlib import Path

from .benchmark import benchmark_local_models
from .compiler import compile_school
from .discovery import discover_school
from .models import DocumentArtifact, SectionExtraction
from .pipeline import add_school
from .registry import generate_registry
from .utils import read_json
from .validator import (
    validate_school_data,
    validate_section_extraction,
    validate_year_submission,
)


def _cmd_add(args: argparse.Namespace) -> int:
    manifest = add_school(
        args.target,
        school_name=args.name,
        school_slug=args.slug,
        workspace_dir=args.workspace_dir,
        jobs=args.jobs,
        ocr_provider=args.ocr,
        extractor=args.extractor,
        model=args.model,
        include_unknown=args.include_unknown,
        discover_if_missing=not args.no_discover,
        archive_url=args.archive_url,
        repository_fallback=not args.no_repository_fallback,
        download_years=None if args.years == 0 else args.years,
        college_data_dir=args.college_data_dir,
    )
    summary = {
        "school_name": manifest.school_name,
        "school_slug": manifest.school_slug,
        "workspace": manifest.workspace,
        "documents": len(manifest.documents),
        "years": sorted({document.academic_year for document in manifest.documents if document.academic_year}),
        "packets": len(manifest.packet_paths),
        "extractions": len(manifest.extraction_paths),
        "extraction_cache_hits": manifest.extraction_cache_hits,
        "extraction_cache_misses": manifest.extraction_cache_misses,
        "rejected_documents": len(manifest.rejected_documents),
        "review_required": manifest.review_required,
        "warnings": manifest.warnings,
    }
    if args.publish:
        if args.extractor == "none":
            raise ValueError("--publish requires a structured extractor.")
        summary["publication"] = compile_school(
            str(Path(manifest.workspace) / "school_manifest.json"),
            workspace_dir=args.workspace_dir,
            publish=True,
        )
    print(json.dumps(summary, indent=2))
    return 2 if manifest.review_required and args.strict else 0


def _cmd_discover(args: argparse.Namespace) -> int:
    manifest = discover_school(
        args.school,
        school_slug=args.slug,
        workspace_dir=args.workspace_dir,
        archive_url=args.archive_url,
        repository_fallback=not args.no_repository_fallback,
    )
    summary = {
        "school_name": manifest.school_name,
        "school_slug": manifest.school_slug,
        "official_site": manifest.official_site,
        "official_archive_pages": manifest.official_archive_pages,
        "candidate_count": len(manifest.candidates),
        "candidates": [candidate.model_dump(mode="json") for candidate in manifest.candidates],
        "warnings": manifest.warnings,
    }
    print(json.dumps(summary, indent=2))
    return 0 if manifest.candidates else 1


def _cmd_validate(args: argparse.Namespace) -> int:
    payload = read_json(Path(args.input_json))
    if "observations" in payload:
        result = validate_section_extraction(payload)
    elif "year" in payload and "data" in payload:
        result = validate_year_submission(payload)
    elif "years" in payload:
        result = validate_school_data(payload)
    else:
        raise ValueError("Expected a section extraction, year submission, or school dataset JSON file.")
    print(json.dumps(result, indent=2))
    return 1 if result["error_count"] else 0


def _cmd_registry(args: argparse.Namespace) -> int:
    result = generate_registry(check=args.check)
    print(json.dumps(result, indent=2))
    return 1 if args.check and result["changed"] else 0


def _cmd_compile(args: argparse.Namespace) -> int:
    result = compile_school(
        args.target,
        workspace_dir=args.workspace_dir,
        publish=args.publish,
    )
    print(json.dumps(result, indent=2))
    return 1 if result["error_count"] else 0


def _cmd_schema(args: argparse.Namespace) -> int:
    schemas = {
        "document": DocumentArtifact.model_json_schema(),
        "section_extraction": SectionExtraction.model_json_schema(),
    }
    print(json.dumps(schemas[args.name], indent=2))
    return 0


def _cmd_benchmark(args: argparse.Namespace) -> int:
    result = benchmark_local_models(args.packet_dir, args.gold, models=args.models)
    if args.output:
        from .utils import write_json

        write_json(Path(args.output), result)
    print(json.dumps(result, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evidence-first Common Data Set ingestion")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Ingest, route, OCR, and optionally extract a school")
    add_parser.add_argument("target", help="School slug, PDF, or directory")
    add_parser.add_argument("--name", help="Canonical school name")
    add_parser.add_argument("--slug", help="Canonical school slug")
    add_parser.add_argument("--workspace-dir", default=".cds_pipeline")
    add_parser.add_argument("--jobs", type=int, default=4)
    add_parser.add_argument(
        "--ocr",
        choices=["auto", "none", "ollama", "unlimited", "paddle", "mistral"],
        default="auto",
    )
    add_parser.add_argument(
        "--extractor",
        choices=["none", "auto", "local", "codex", "openai"],
        default="none",
    )
    add_parser.add_argument("--model", help="Override the selected extractor's default model")
    add_parser.add_argument("--include-unknown", action="store_true")
    add_parser.add_argument("--no-discover", action="store_true", help="Require target to already exist locally")
    add_parser.add_argument("--archive-url", help="Known official CDS archive page")
    add_parser.add_argument("--no-repository-fallback", action="store_true")
    add_parser.add_argument("--years", type=int, default=8, help="Number of recent years to download; 0 means all")
    add_parser.add_argument("--college-data-dir", default="College-Data")
    add_parser.add_argument("--strict", action="store_true", help="Exit nonzero when review is required")
    add_parser.add_argument(
        "--publish",
        action="store_true",
        help="Compile, validate, write the school dataset, and regenerate the registry",
    )
    add_parser.set_defaults(func=_cmd_add)

    discover_parser = subparsers.add_parser("discover", help="Find official and fallback CDS source URLs")
    discover_parser.add_argument("school")
    discover_parser.add_argument("--slug")
    discover_parser.add_argument("--workspace-dir", default=".cds_pipeline")
    discover_parser.add_argument("--archive-url")
    discover_parser.add_argument("--no-repository-fallback", action="store_true")
    discover_parser.set_defaults(func=_cmd_discover)

    validate_parser = subparsers.add_parser("validate", help="Run blocking semantic validation")
    validate_parser.add_argument("input_json")
    validate_parser.set_defaults(func=_cmd_validate)

    compile_parser = subparsers.add_parser("compile", help="Compile reviewed observations into site data")
    compile_parser.add_argument("target", help="School slug or school_manifest.json path")
    compile_parser.add_argument("--workspace-dir", default=".cds_pipeline")
    compile_parser.add_argument("--publish", action="store_true", help="Write into src/data/schools and update the registry")
    compile_parser.set_defaults(func=_cmd_compile)

    registry_parser = subparsers.add_parser("registry", help="Generate static school imports from JSON files")
    registry_parser.add_argument("--check", action="store_true")
    registry_parser.set_defaults(func=_cmd_registry)

    schema_parser = subparsers.add_parser("schema", help="Print a pipeline JSON Schema")
    schema_parser.add_argument("name", choices=["document", "section_extraction"])
    schema_parser.set_defaults(func=_cmd_schema)

    benchmark_parser = subparsers.add_parser(
        "benchmark", help="Score local Ollama models against curated CDS packets"
    )
    benchmark_parser.add_argument("packet_dir")
    benchmark_parser.add_argument("--gold", required=True)
    benchmark_parser.add_argument("--models", nargs="+", default=["gemma4:12b"])
    benchmark_parser.add_argument("--output")
    benchmark_parser.set_defaults(func=_cmd_benchmark)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
