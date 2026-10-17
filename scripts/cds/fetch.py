# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf>=1.26"]
# ///
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import check_year, load_json, school_dir, write_json  # noqa: E402

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)


def resolve_url(url: str) -> str:
    drive = re.search(r"drive\.google\.com/(?:file/d/|open\?id=|uc\?id=)([\w-]+)", url)
    if drive:
        return f"https://drive.usercontent.google.com/download?id={drive.group(1)}&export=download&confirm=t"
    box = re.search(r"(https://[\w.]*box\.com/s/[\w]+)", url)
    if box:
        return box.group(1).replace("/s/", "/shared/static/")
    return url


def headers(referer: str | None) -> dict[str, str]:
    result = {"User-Agent": USER_AGENT, "Accept": "application/pdf,application/octet-stream,*/*"}
    if referer:
        result["Referer"] = referer
    return result


def sniff(path: Path) -> str | None:
    head = path.read_bytes()[:8]
    if head.startswith(b"%PDF"):
        return "pdf"
    if head.startswith(b"PK"):
        return "xlsx"
    if head.startswith(b"\xd0\xcf\x11\xe0"):
        return "xls"
    return None


def try_urllib(url: str, dest: Path, referer: str | None) -> None:
    request = urllib.request.Request(url, headers=headers(referer))
    with urllib.request.urlopen(request, timeout=90) as response, dest.open("wb") as out:
        shutil.copyfileobj(response, out)


def try_curl(url: str, dest: Path, referer: str | None) -> None:
    curl = shutil.which("curl")
    if not curl:
        raise RuntimeError("curl not found")
    command = [curl, "-fsSL", "--retry", "2"]
    for key, value in headers(referer).items():
        command += ["-H", f"{key}: {value}"]
    subprocess.run(command + ["-o", str(dest), url], check=True, timeout=180, capture_output=True)


def wayback(url: str) -> str:
    query = "https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(
        {"url": url, "output": "json", "filter": "statuscode:200", "fl": "timestamp", "limit": "-1"}
    )
    request = urllib.request.Request(query, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        rows = json.loads(response.read() or b"[]")
    if len(rows) < 2:
        raise RuntimeError("no Wayback capture")
    return f"https://web.archive.org/web/{rows[-1][0]}id_/{url}"


def download(url: str, dest: Path, referer: str | None) -> tuple[str, str]:
    attempts = [("direct", lambda: url, try_urllib), ("curl", lambda: url, try_curl), ("wayback", lambda: wayback(url), try_curl)]
    failures = []
    for label, target, method in attempts:
        for attempt in range(2):
            try:
                dest.unlink(missing_ok=True)
                method(target(), dest, referer)
                if not dest.exists():
                    raise RuntimeError("no file written")
                if kind := sniff(dest):
                    return kind, label
                snippet = dest.read_bytes()[:200].decode("utf-8", "replace")
                title = re.search(r"<title>([^<]*)", snippet)
                failures.append(f"{label}: got HTML ({title.group(1) if title else snippet[:60]!r})")
            except Exception as error:
                failures.append(f"{label}: {error}")
            time.sleep(1 + attempt)
    raise SystemExit(f"could not download {url}\n  " + "\n  ".join(failures))


def merge(parts: list[Path], dest: Path) -> int:
    import pymupdf

    merged = pymupdf.open()
    for part in parts:
        with pymupdf.open(part) as doc:
            merged.insert_pdf(doc)
    merged.save(dest)
    return merged.page_count


def page_count(path: Path) -> int | None:
    if path.suffix != ".pdf":
        return None
    import pymupdf

    with pymupdf.open(path) as doc:
        return doc.page_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("year")
    parser.add_argument("urls", nargs="+", help="one URL, or several section PDFs to merge in order")
    parser.add_argument("--name", required=True)
    parser.add_argument("--mirror", help="discovery source when the file is not hosted by the school")
    parser.add_argument("--referer", help="page that links the file; some sites block requests without it")
    args = parser.parse_args()

    year = check_year(args.year)
    folder = school_dir(args.slug)
    folder.mkdir(parents=True, exist_ok=True)

    parts_meta = []
    with tempfile.TemporaryDirectory() as tmp:
        parts: list[Path] = []
        kinds = set()
        for number, url in enumerate(args.urls, start=1):
            part = Path(tmp) / f"part{number:02d}"
            resolved = resolve_url(url)
            kind, via = download(resolved, part, args.referer)
            kinds.add(kind)
            parts.append(part)
            data = part.read_bytes()
            parts_meta.append({
                "source_url": url,
                "resolved_url": resolved,
                "fetched_via": via,
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
            })
            print(f"  part {number}: {len(data):,} bytes via {via}")

        if len(parts) > 1:
            if kinds != {"pdf"}:
                raise SystemExit("can only merge PDF parts")
            dest = folder / f"{args.slug}-cds-{year}.pdf"
            merge(parts, dest)
        else:
            dest = folder / f"{args.slug}-cds-{year}.{kinds.pop()}"
            shutil.move(str(parts[0]), dest)

    for stale in folder.glob(f"{args.slug}-cds-{year}.*"):
        if stale != dest:
            stale.unlink()

    data = dest.read_bytes()
    entry = {
        "source_url": args.urls[0] if len(args.urls) == 1 else None,
        "discovery_source": args.mirror or "official",
        "official": args.mirror is None,
        "academic_year": year,
        "local_path": str(dest),
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
        "page_count": page_count(dest),
        "parts": parts_meta,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    sources_path = folder / "sources.json"
    sources = load_json(sources_path) if sources_path.exists() else {
        "school_name": args.name,
        "school_slug": args.slug,
        "downloads": [],
    }
    sources["downloads"] = [d for d in sources["downloads"] if d.get("academic_year") != year]
    sources["downloads"].append(entry)
    sources["downloads"].sort(key=lambda d: d["academic_year"])
    write_json(sources_path, sources)

    print(f"saved {dest.name}  {entry['size_bytes']:,} bytes  {entry['page_count']} pages  sha256 {entry['sha256'][:16]}")


if __name__ == "__main__":
    main()
