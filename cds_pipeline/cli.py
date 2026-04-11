from __future__ import annotations

import argparse
import json
from pathlib import Path

from .prepare import prepare_documents
from .resolver import resolve_target
from .utils import read_json
from .validator import validate_school_data, validate_year_submission


def _cmd_prepare(args: argparse.Namespace) -> int:
    resolved = resolve_target(args.target)
    result = prepare_documents(
        resolved,
        explicit_config=args.config,
        workspace_dir=args.workspace_dir,
        render_dpi=args.render_dpi,
    )
    summary = {
        "school_slug": result["school_slug"],
        "school_name": result["school_name"],
        "workspace": result["workspace"],
        "years": [
            {
                "year": item["year"],
                "page_count": item["page_count"],
                "manifest_path": item["manifest_path"],
            }
            for item in result["years"]
        ],
    }
    print(json.dumps(summary, indent=2))
    return 0


def _cmd_extract(args: argparse.Namespace) -> int:
    return _cmd_prepare(args)


def _cmd_validate(args: argparse.Namespace) -> int:
    payload = read_json(Path(args.input_json))
    if isinstance(payload, dict) and "year" in payload and "data" in payload:
        print(json.dumps(validate_year_submission(payload), indent=2))
        return 0

    if isinstance(payload, dict) and "years" in payload:
        print(json.dumps(validate_school_data(payload), indent=2))
        return 0

    raise ValueError("Input JSON must be either a per-year submission payload or a school dataset payload.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CDS screenshot preparation workflow")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare", help="Render PDFs into per-year screenshot workspaces")
    prepare_parser.add_argument("target")
    prepare_parser.add_argument("--config", help="Optional config override JSON path")
    prepare_parser.add_argument("--workspace-dir", default=".cds_pipeline")
    prepare_parser.add_argument("--render-dpi", type=int, help="Optional render DPI override")
    prepare_parser.set_defaults(func=_cmd_prepare)

    extract_parser = subparsers.add_parser("extract", help="Backward-compatible alias for prepare")
    extract_parser.add_argument("target")
    extract_parser.add_argument("--config", help="Optional config override JSON path")
    extract_parser.add_argument("--workspace-dir", default=".cds_pipeline")
    extract_parser.add_argument("--render-dpi", type=int, help="Optional render DPI override")
    extract_parser.set_defaults(func=_cmd_extract)

    validate_parser = subparsers.add_parser("validate", help="Validate a per-year submission or school dataset JSON")
    validate_parser.add_argument("input_json")
    validate_parser.set_defaults(func=_cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
