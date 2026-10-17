# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf>=1.26", "openpyxl>=3.1"]
# ///
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import write_json  # noqa: E402

WANTED = ["B1", "B2", "C1", "C7", "C9", "C21", "C22", "F1", "G1", "G5", "H1", "H2", "H2A"]
HEADING = re.compile(r"^\s*([A-J]\d{1,2}A?)(?:[.:)\s]|$)", re.MULTILINE)
LOOSE_HEADING = re.compile(r"([A-J]\d{1,2}A?) {2,}\S")
SCANNED_CHARS = 80


def fill_missing(sections: dict[str, list[int]], texts: list[str]) -> None:
    for code in WANTED:
        if sections.get(code):
            continue
        pages = [i for i, text in enumerate(texts, start=1) if code in LOOSE_HEADING.findall(text)]
        if pages:
            sections[code] = pages


def dump_pdf(path: Path, out: Path, dpi: int, render: set[str], render_all: bool) -> dict:
    import pymupdf

    doc = pymupdf.open(path)
    pages_dir = out / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    sections: dict[str, list[int]] = {}
    scanned: list[int] = []
    texts: list[str] = []

    for index, page in enumerate(doc, start=1):
        text = page.get_text("text", sort=True)
        texts.append(text)
        (pages_dir / f"{index:03d}.txt").write_text(text, encoding="utf-8")
        if len(text.strip()) < SCANNED_CHARS:
            scanned.append(index)
        for code in set(HEADING.findall(text)):
            sections.setdefault(code, []).append(index)
    fill_missing(sections, texts)

    to_render = set(scanned)
    if render_all:
        to_render = set(range(1, doc.page_count + 1))
    for code in render:
        for number in sections.get(code, []):
            to_render.update(n for n in (number, number + 1) if n <= doc.page_count)
    if to_render:
        img_dir = out / "img"
        img_dir.mkdir(exist_ok=True)
        for number in sorted(to_render):
            doc[number - 1].get_pixmap(dpi=dpi).save(img_dir / f"{number:03d}.png")

    return {
        "file": path.name,
        "kind": "pdf",
        "page_count": doc.page_count,
        "scanned_pages": scanned,
        "rendered_pages": sorted(to_render),
        "sections": {code: sections.get(code, []) for code in WANTED},
    }


def dump_xlsx(path: Path, out: Path) -> dict:
    import openpyxl

    book = openpyxl.load_workbook(path, data_only=True, read_only=True)
    pages_dir = out / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    sections: dict[str, list[int]] = {}
    texts: list[str] = []
    for index, sheet in enumerate(book.worksheets, start=1):
        lines = []
        for row in sheet.iter_rows(values_only=True):
            cells = ["" if v is None else str(v) for v in row]
            if any(cells):
                lines.append("\t".join(cells).rstrip())
        text = f"# sheet: {sheet.title}\n" + "\n".join(lines)
        (pages_dir / f"{index:03d}.txt").write_text(text, encoding="utf-8")
        texts.append(text)
        for code in set(HEADING.findall(text)):
            sections.setdefault(code, []).append(index)
    fill_missing(sections, texts)
    return {
        "file": path.name,
        "kind": "xlsx",
        "page_count": len(book.worksheets),
        "scanned_pages": [],
        "rendered_pages": [],
        "sections": {code: sections.get(code, []) for code in WANTED},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("--out", type=Path, help="defaults to College-Data/<slug>/work/<file stem>")
    parser.add_argument("--render", default="", help="comma-separated sections to render as PNG, e.g. C1,C9")
    parser.add_argument("--render-all", action="store_true")
    parser.add_argument("--dpi", type=int, default=110)
    args = parser.parse_args()

    path = args.file.resolve()
    out = args.out or path.parent / "work" / path.stem
    out.mkdir(parents=True, exist_ok=True)
    render = {code.strip().upper() for code in args.render.split(",") if code.strip()}

    if path.suffix.lower() == ".pdf":
        index = dump_pdf(path, out, args.dpi, render, args.render_all)
    elif path.suffix.lower() in {".xlsx", ".xlsm"}:
        index = dump_xlsx(path, out)
    else:
        raise SystemExit(f"unsupported file type: {path.suffix}")

    write_json(out / "index.json", index)
    print(json.dumps({"out": str(out), **index}, indent=1))


if __name__ == "__main__":
    main()
