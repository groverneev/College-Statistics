from __future__ import annotations

import argparse
import json
from pathlib import Path

from .classifier import classify_pdf
from .exporter import export_school_json
from .pipeline import extract_documents
from .resolver import resolve_target
from .review import build_review_payload, review_markdown
from .utils import read_json, write_json
from .validator import validate_document


def _cmd_classify(args: argparse.Namespace) -> int:
    resolved = resolve_target(args.target)
    results = []
    for item in resolved:
        classification = classify_pdf(item["pdf_path"])
        results.append({**item, "classification": classification})
    print(json.dumps(results, indent=2))
    return 0


def _cmd_extract(args: argparse.Namespace) -> int:
    resolved = resolve_target(args.target)
    result = extract_documents(
        resolved,
        explicit_config=args.config,
        workspace_dir=args.workspace_dir,
    )
    summary = {
        "school_slug": result["candidate"]["school_slug"],
        "school_name": result["candidate"]["school_name"],
        "documents": len(result["candidate"]["documents"]),
        "workspace": result["workspace"],
        "total_issues": result["review"]["total_issue_count"],
    }
    print(json.dumps(summary, indent=2))
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    candidate = read_json(Path(args.candidate_json))
    validations = []
    for document in candidate.get("documents", []):
        validation = validate_document(document["data"], document.get("field_meta", {}))
        validations.append({"year": document.get("year"), "validation": validation})
    print(json.dumps(validations, indent=2))
    return 0


def _cmd_review(args: argparse.Namespace) -> int:
    payload = read_json(Path(args.input_json))
    if payload.get("documents") and payload["documents"][0].get("data") is not None:
        payload = build_review_payload(payload)
    print(review_markdown(payload))
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    candidate = read_json(Path(args.candidate_json))
    exported = export_school_json(candidate)
    output_path = Path(args.output) if args.output else Path("src/data/schools") / f"{exported['slug']}.json"
    write_json(output_path, exported)
    print(json.dumps({"output": str(output_path), "years": len(exported["years"])}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CDS extraction pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    classify_parser = subparsers.add_parser("classify", help="Classify one PDF or a school PDF set")
    classify_parser.add_argument("target")
    classify_parser.set_defaults(func=_cmd_classify)

    extract_parser = subparsers.add_parser("extract", help="Run the full extraction pipeline")
    extract_parser.add_argument("target")
    extract_parser.add_argument("--config", help="Optional config override JSON path")
    extract_parser.add_argument("--workspace-dir", default=".cds_pipeline")
    extract_parser.set_defaults(func=_cmd_extract)

    validate_parser = subparsers.add_parser("validate", help="Validate a candidate.json artifact")
    validate_parser.add_argument("candidate_json")
    validate_parser.set_defaults(func=_cmd_validate)

    review_parser = subparsers.add_parser("review", help="Render a markdown review from candidate/review JSON")
    review_parser.add_argument("input_json")
    review_parser.set_defaults(func=_cmd_review)

    export_parser = subparsers.add_parser("export", help="Export candidate data to site JSON shape")
    export_parser.add_argument("candidate_json")
    export_parser.add_argument("--output")
    export_parser.set_defaults(func=_cmd_export)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
