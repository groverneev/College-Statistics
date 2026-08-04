from __future__ import annotations

from pathlib import Path
import re
from urllib.parse import parse_qs, urlparse

from .discovery import USER_AGENT, _requests, _unwrap_google_redirect
from .models import DiscoveryManifest, DownloadRecord, SourceCandidate
from .utils import read_json, sha256_file, validate_slug, write_json


MAX_PDF_BYTES = 100 * 1024 * 1024


def _has_pdf_signature(path: Path) -> bool:
    try:
        with path.open("rb") as stream:
            return stream.read(5) == b"%PDF-"
    except OSError:
        return False


def _direct_download_url(url: str) -> str:
    url = _unwrap_google_redirect(url)
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host.endswith("drive.google.com"):
        match = re.search(r"/file/d/([^/]+)", parsed.path)
        file_id = match.group(1) if match else parse_qs(parsed.query).get("id", [None])[0]
        if file_id:
            return f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"
    if host.endswith("box.com") or host.endswith("app.box.com"):
        match = re.search(r"/s/([a-zA-Z0-9]+)", parsed.path)
        if match:
            organization = host.split(".")[0]
            return f"https://{organization}.box.com/shared/static/{match.group(1)}.pdf"
    return url


def _candidate_groups(
    candidates: list[SourceCandidate], years: int | None
) -> list[list[SourceCandidate]]:
    by_year: dict[str, list[SourceCandidate]] = {}
    unknown: list[SourceCandidate] = []
    for candidate in candidates:
        if candidate.academic_year:
            by_year.setdefault(candidate.academic_year, []).append(candidate)
        else:
            unknown.append(candidate)
    selected: list[list[SourceCandidate]] = []
    for academic_year in sorted(by_year, reverse=True):
        ranked = sorted(
            by_year[academic_year],
            key=lambda item: (item.official, item.score),
            reverse=True,
        )
        selected.append(ranked)
        if years is not None and len(selected) >= years:
            break
    if not selected and unknown:
        selected.append(sorted(unknown, key=lambda item: (item.official, item.score), reverse=True))
    return selected


def _download_pdf(candidate: SourceCandidate, destination: Path) -> DownloadRecord:
    requests = _requests()
    resolved_url = _direct_download_url(candidate.url)
    destination.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(
        resolved_url,
        timeout=90,
        stream=True,
        allow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    part_path = destination.with_suffix(destination.suffix + ".part")
    try:
        total = 0
        with part_path.open("wb") as stream:
            for chunk in response.iter_content(1024 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > MAX_PDF_BYTES:
                    raise ValueError(f"Download exceeded {MAX_PDF_BYTES} bytes: {candidate.url}")
                stream.write(chunk)
        if not _has_pdf_signature(part_path):
            raise ValueError(
                f"Downloaded content was not a PDF ({response.headers.get('content-type')}): {candidate.url}"
            )
        part_path.replace(destination)
    except Exception:
        part_path.unlink(missing_ok=True)
        raise
    finally:
        response.close()
    return DownloadRecord(
        source_url=candidate.url,
        resolved_url=str(response.url),
        discovery_source=candidate.discovery_source,
        official=candidate.official,
        academic_year=candidate.academic_year,
        local_path=str(destination.resolve()),
        sha256=sha256_file(destination),
        size_bytes=destination.stat().st_size,
        content_type=response.headers.get("content-type"),
    )


def download_discovered_sources(
    discovery: DiscoveryManifest,
    *,
    college_data_dir: str | Path = "College-Data",
    years: int | None = 8,
) -> tuple[Path, list[DownloadRecord], list[str]]:
    school_slug = validate_slug(discovery.school_slug)
    destination_dir = Path(college_data_dir) / school_slug
    candidate_groups = _candidate_groups(discovery.candidates, years)
    records: list[DownloadRecord] = []
    warnings: list[str] = []
    prior_by_year: dict[str | None, DownloadRecord] = {}
    prior_manifest_path = destination_dir / "sources.json"
    if prior_manifest_path.exists():
        try:
            for payload in read_json(prior_manifest_path).get("downloads", []):
                record = DownloadRecord.model_validate(payload)
                prior_by_year[record.academic_year] = record
        except Exception:
            prior_by_year = {}
    for candidates in candidate_groups:
        first = candidates[0]
        year_token = first.academic_year or f"unknown-{len(records) + 1}"
        destination = destination_dir / f"{school_slug}-cds-{year_token}.pdf"
        prior = prior_by_year.get(first.academic_year)
        if (
            prior is not None
            and prior.source_url in {candidate.url for candidate in candidates}
            and _has_pdf_signature(destination)
            and sha256_file(destination) == prior.sha256
        ):
            records.append(prior.model_copy(update={"local_path": str(destination.resolve())}))
            continue
        failures: list[str] = []
        for candidate in candidates:
            try:
                records.append(_download_pdf(candidate, destination))
                break
            except Exception as exc:
                failures.append(f"{candidate.url}: {exc}")
        else:
            warnings.append(
                f"Failed to download {first.academic_year or first.url} from every discovered source: "
                + " | ".join(failures)
            )

    source_manifest = {
        "school_name": discovery.school_name,
        "school_slug": discovery.school_slug,
        "official_site": discovery.official_site,
        "downloads": [record.model_dump(mode="json") for record in records],
        "warnings": warnings,
    }
    write_json(destination_dir / "sources.json", source_manifest)
    return destination_dir, records, warnings
