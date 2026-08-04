from __future__ import annotations

from pathlib import Path

from .utils import normalize_token


def resolve_pdf_paths(target: str) -> tuple[Path, list[Path]]:
    path = Path(target)
    if path.exists():
        if path.is_file():
            if path.suffix.lower() != ".pdf":
                raise ValueError(f"Expected a PDF file, got: {path}")
            return path.parent, [path]
        pdfs = sorted(path.rglob("*.pdf"))
        if not pdfs:
            raise ValueError(f"No PDFs found under {path}")
        return path, pdfs

    root = Path("College-Data")
    if not root.exists():
        raise ValueError(f"Target does not exist and College-Data was not found: {target}")
    token = normalize_token(target)
    matches = [
        child
        for child in root.iterdir()
        if child.is_dir()
        and (normalize_token(child.name) == token or token in normalize_token(child.name))
    ]
    if not matches:
        raise ValueError(f"Could not resolve a school or path: {target}")
    best = min(matches, key=lambda item: len(normalize_token(item.name)))
    pdfs = sorted(best.rglob("*.pdf"))
    if not pdfs:
        raise ValueError(f"No PDFs found under {best}")
    return best, pdfs
