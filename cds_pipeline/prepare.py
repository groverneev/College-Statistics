from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import load_config
from .contracts import YEAR_SUBAGENT_OUTPUT_SCHEMA, build_year_subagent_prompt
from .utils import ensure_dir, write_json


def _workspace_path(base_dir: str | Path, school_slug: str) -> Path:
    return Path(base_dir) / school_slug


def prepare_documents(
    resolved_documents: list[dict[str, str]],
    *,
    explicit_config: str | None = None,
    workspace_dir: str | Path = ".cds_pipeline",
    render_dpi: int | None = None,
) -> dict[str, Any]:
    if not resolved_documents:
        raise ValueError("No documents resolved for preparation.")

    school_slug = resolved_documents[0]["school_slug"]
    config = load_config(school_slug, explicit_config=explicit_config)
    school_name = config.get("school_name", school_slug.replace("-", " ").title())
    render_config = config.get("render", {}) if isinstance(config.get("render"), dict) else {}
    dpi = int(render_dpi or render_config.get("dpi", 170))

    workspace = _workspace_path(workspace_dir, school_slug)
    ensure_dir(workspace)

    year_groups: dict[str, list[dict[str, str]]] = {}
    for document in resolved_documents:
        year_groups.setdefault(document["year"], []).append(document)

    year_summaries: list[dict[str, Any]] = []
    for year in sorted(year_groups):
        year_payload = _prepare_year(
            school_slug=school_slug,
            school_name=school_name,
            year=year,
            documents=sorted(year_groups[year], key=lambda item: item["pdf_path"]),
            workspace=workspace,
            dpi=dpi,
        )
        year_summaries.append(
            {
                "year": year_payload["year"],
                "page_count": year_payload["page_count"],
                "manifest_path": year_payload["manifest_path"],
            }
        )

    school_manifest = {
        "school_slug": school_slug,
        "school_name": school_name,
        "workspace": str(workspace.resolve()),
        "year_manifest_paths": [item["manifest_path"] for item in year_summaries],
        "years": year_summaries,
    }
    write_json(workspace / "school_manifest.json", school_manifest)

    return {
        "school_slug": school_slug,
        "school_name": school_name,
        "workspace": str(workspace.resolve()),
        "years": year_summaries,
    }


def _prepare_year(
    *,
    school_slug: str,
    school_name: str,
    year: str,
    documents: list[dict[str, str]],
    workspace: Path,
    dpi: int,
) -> dict[str, Any]:
    try:
        import fitz  # type: ignore
    except Exception as exc:  # pragma: no cover - dependency guard
        raise RuntimeError(f"PyMuPDF is required for PDF rendering: {exc}") from exc

    year_dir = workspace / year
    pages_dir = year_dir / "pages"
    ensure_dir(pages_dir)

    screenshots: list[dict[str, Any]] = []
    screenshot_paths: list[str] = []
    source_pdfs: list[str] = []
    sequence = 1

    for document in documents:
        pdf_path = Path(document["pdf_path"])
        source_pdfs.append(str(pdf_path.resolve()))
        pdf_stub = pdf_path.stem.replace(" ", "_")

        pdf = fitz.open(pdf_path)
        try:
            for page_index in range(len(pdf)):
                page_number = page_index + 1
                pixmap = pdf.load_page(page_index).get_pixmap(dpi=dpi, alpha=False)
                image_path = pages_dir / f"{sequence:03d}-{pdf_stub}-page-{page_number:03d}.png"
                image_path.write_bytes(pixmap.tobytes("png"))
                resolved_image_path = str(image_path.resolve())
                screenshots.append(
                    {
                        "sequence": sequence,
                        "pdf_path": str(pdf_path.resolve()),
                        "pdf_name": pdf_path.name,
                        "pdf_page": page_number,
                        "image_path": resolved_image_path,
                    }
                )
                screenshot_paths.append(resolved_image_path)
                sequence += 1
        finally:
            pdf.close()

    manifest_path = year_dir / "manifest.json"
    manifest = {
        "school_slug": school_slug,
        "school_name": school_name,
        "year": year,
        "source_pdfs": source_pdfs,
        "page_count": len(screenshots),
        "screenshot_paths": screenshot_paths,
        "screenshots": screenshots,
        "subagent_prompt": build_year_subagent_prompt(school_name=school_name, year=year),
        "output_contract": YEAR_SUBAGENT_OUTPUT_SCHEMA,
    }
    write_json(manifest_path, manifest)

    return {
        "year": year,
        "page_count": len(screenshots),
        "manifest_path": str(manifest_path.resolve()),
    }
