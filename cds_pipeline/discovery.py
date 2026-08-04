from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from hashlib import sha256
import os
from pathlib import Path
import re
import time
from urllib.parse import parse_qs, unquote, urljoin, urlparse
from xml.etree import ElementTree

from .models import DiscoveryManifest, SourceCandidate
from .utils import extract_year_candidates, normalize_token, slugify, validate_slug, write_json


COLLEGE_TRANSITIONS_URL = (
    "https://www.collegetransitions.com/dataverse/common-data-set-repository/"
)
USER_AGENT = "CollegeStatisticsBot/3.1 (+https://collegestatistics.org)"
RELEVANT_URL_TOKENS = (
    "common-data",
    "common_data",
    "commondataset",
    "commondata",
    "institutional-research",
    "institutional_research",
    "institutional-effectiveness",
    "factbook",
    "facts-and-figures",
)


def _requests() -> object:
    try:
        import requests
    except Exception as exc:
        raise RuntimeError(
            "Source discovery requires requests and BeautifulSoup: "
            "python -m pip install requests beautifulsoup4"
        ) from exc
    return requests


def _soup(html: str) -> object:
    try:
        from bs4 import BeautifulSoup
    except Exception as exc:
        raise RuntimeError(
            "Source discovery requires BeautifulSoup: python -m pip install beautifulsoup4"
        ) from exc
    return BeautifulSoup(html, "html.parser")


@dataclass
class CachedHttpClient:
    cache_dir: Path
    cache_ttl_seconds: int = 24 * 60 * 60

    def __post_init__(self) -> None:
        requests = _requests()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def get_text(self, url: str, *, use_cache: bool = True, timeout: int = 30) -> str:
        cache_path = self.cache_dir / f"{sha256(url.encode('utf-8')).hexdigest()}.txt"
        if use_cache and cache_path.exists() and time.time() - cache_path.stat().st_mtime < self.cache_ttl_seconds:
            return cache_path.read_text(encoding="utf-8")
        response = self.session.get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        text = response.text
        if use_cache:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(text, encoding="utf-8")
        return text


def _canonical_site(value: str) -> str:
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        value = f"https://{value}"
    parsed = urlparse(value)
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def _name_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalize_token(left), normalize_token(right)).ratio()


def resolve_official_site(school_name: str, client: CachedHttpClient) -> str | None:
    requests = _requests()
    response = client.session.get(
        "https://api.data.gov/ed/collegescorecard/v1/schools.json",
        params={
            "api_key": os.environ.get("COLLEGE_SCORECARD_API_KEY", "DEMO_KEY"),
            "school.name": school_name,
            "fields": "school.name,school.school_url,id",
        },
        timeout=30,
    )
    response.raise_for_status()
    results = response.json().get("results", [])
    ranked = sorted(
        (
            (_name_similarity(school_name, str(item.get("school.name", ""))), item)
            for item in results
            if item.get("school.school_url")
        ),
        reverse=True,
        key=lambda item: item[0],
    )
    if not ranked or ranked[0][0] < 0.72:
        return None
    return _canonical_site(str(ranked[0][1]["school.school_url"]))


def _unwrap_google_redirect(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc.endswith("google.com") and parsed.path == "/url":
        query = parse_qs(parsed.query).get("q")
        if query:
            return unquote(query[0])
    return url


def _download_like(url: str, label: str) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    lowered = f"{url} {label}".lower()
    return (
        ".pdf" in parsed.path.lower()
        or "[pdf]" in label.lower()
        or host.endswith("box.com")
        or host.endswith("app.box.com")
        or host.endswith("drive.google.com")
        or host.endswith("docs.google.com")
        or "download" in lowered and "common data" in lowered
    )


def _link_score(url: str, label: str, *, official: bool) -> float:
    lowered = f"{url} {label}".lower()
    score = 0.6 if official else 0.25
    if "common data set" in lowered or "common-data-set" in lowered or "common_data_set" in lowered:
        score += 0.25
    if re.search(r"(?i)(?:^|[/_.-])cds(?:[/_.-]|\d)", lowered):
        score += 0.1
    if ".pdf" in urlparse(url).path.lower():
        score += 0.05
    return min(1.0, score)


def extract_candidates_from_page(
    html: str,
    *,
    page_url: str,
    official: bool,
    discovery_source: str = "official_site",
) -> tuple[list[SourceCandidate], list[str]]:
    soup = _soup(html)
    candidates: list[SourceCandidate] = []
    unsupported: list[str] = []
    for anchor in soup.find_all("a", href=True):
        label = anchor.get_text(" ", strip=True)
        url = _unwrap_google_redirect(urljoin(page_url, str(anchor["href"])))
        context = f"{label} {url}"
        years = extract_year_candidates(context, allow_short=True)
        cds_like = bool(
            re.search(r"(?i)common\s*data\s*set|common[-_]?data[-_]?set|(?:^|\W)cds(?:\W|$)", context)
        )
        if not cds_like:
            continue
        if not _download_like(url, label):
            if years and url not in unsupported:
                unsupported.append(url)
            continue
        candidates.append(
            SourceCandidate(
                url=url,
                label=label,
                academic_year=years[0] if years else None,
                discovery_source=discovery_source,  # type: ignore[arg-type]
                discovery_url=page_url,
                official=official,
                score=_link_score(url, label, official=official),
            )
        )
    return candidates, unsupported


def _parse_sitemap(xml_text: str) -> list[str]:
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError:
        return []
    return [element.text.strip() for element in root.iter() if element.tag.endswith("loc") and element.text]


def _sitemap_seeds(site: str, client: CachedHttpClient) -> list[str]:
    seeds = [urljoin(site, "/sitemap.xml")]
    try:
        robots = client.get_text(urljoin(site, "/robots.txt"), timeout=15)
    except Exception:
        return seeds
    for match in re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots):
        if match not in seeds:
            seeds.append(match)
    return seeds


def _crawl_sitemaps(site: str, client: CachedHttpClient, *, max_sitemaps: int = 20) -> list[str]:
    queue = _sitemap_seeds(site, client)
    seen: set[str] = set()
    page_urls: list[str] = []
    while queue and len(seen) < max_sitemaps:
        sitemap_url = queue.pop(0)
        if sitemap_url in seen:
            continue
        seen.add(sitemap_url)
        try:
            locations = _parse_sitemap(client.get_text(sitemap_url, timeout=30))
        except Exception:
            continue
        for location in locations:
            if location.lower().split("?", 1)[0].endswith((".xml", ".xml.gz")):
                if location not in seen:
                    queue.append(location)
            else:
                page_urls.append(location)
    return page_urls


def discover_official_candidates(
    school_name: str,
    site: str,
    client: CachedHttpClient,
    *,
    archive_url: str | None = None,
) -> tuple[list[SourceCandidate], list[str], list[str]]:
    warnings: list[str] = []
    archive_pages: list[str] = []
    candidates: list[SourceCandidate] = []

    page_urls = [archive_url] if archive_url else []
    if not archive_url:
        sitemap_urls = _crawl_sitemaps(site, client)
        relevant = [
            url for url in sitemap_urls if any(token in url.lower() for token in RELEVANT_URL_TOKENS)
        ]
        page_urls.extend(sorted(relevant, key=lambda url: ("common" not in url.lower(), len(url)))[:40])

    # Some sites have no accessible sitemap. Inspect the home page and follow
    # only links whose labels/URLs suggest institutional data.
    if not page_urls:
        page_urls.append(site)
    checked: set[str] = set()
    for page_url in page_urls:
        if not page_url or page_url in checked:
            continue
        checked.add(page_url)
        try:
            html = client.get_text(page_url, timeout=30)
        except Exception:
            continue
        found, unsupported = extract_candidates_from_page(
            html, page_url=page_url, official=True, discovery_source="official_site"
        )
        if found or unsupported:
            archive_pages.append(page_url)
        candidates.extend(found)
        if unsupported:
            warnings.append(
                f"Official archive {page_url} contains {len(unsupported)} non-PDF CDS links that require a future connector."
            )

        if page_url == site and not found:
            soup = _soup(html)
            for anchor in soup.find_all("a", href=True):
                context = f"{anchor.get_text(' ', strip=True)} {anchor['href']}".lower()
                if any(token.replace("-", " ") in context.replace("-", " ") for token in RELEVANT_URL_TOKENS):
                    child_url = urljoin(site, str(anchor["href"]))
                    if urlparse(child_url).netloc == urlparse(site).netloc and child_url not in checked:
                        try:
                            child_html = client.get_text(child_url, timeout=30)
                        except Exception:
                            continue
                        child_found, child_unsupported = extract_candidates_from_page(
                            child_html,
                            page_url=child_url,
                            official=True,
                            discovery_source="official_site",
                        )
                        if child_found or child_unsupported:
                            archive_pages.append(child_url)
                        candidates.extend(child_found)

    deduped = {(candidate.url, candidate.academic_year): candidate for candidate in candidates}
    return list(deduped.values()), sorted(set(archive_pages)), warnings


def discover_repository_candidates(
    school_name: str,
    client: CachedHttpClient,
) -> tuple[list[SourceCandidate], list[str]]:
    html = client.get_text(COLLEGE_TRANSITIONS_URL, timeout=60)
    soup = _soup(html)
    table = soup.find("table")
    if table is None:
        return [], ["College Transitions repository table was not found."]
    rows = table.find_all("tr")
    if not rows:
        return [], ["College Transitions repository table was empty."]
    headers = [cell.get_text(" ", strip=True) for cell in rows[0].find_all(["th", "td"])]
    ranked: list[tuple[float, object]] = []
    for row in rows[1:]:
        cells = row.find_all(["th", "td"])
        if not cells:
            continue
        name = cells[0].get_text(" ", strip=True)
        ranked.append((_name_similarity(school_name, name), row))
    ranked.sort(key=lambda item: item[0], reverse=True)
    if not ranked or ranked[0][0] < 0.72:
        return [], [f"{school_name} was not found in the College Transitions repository."]

    cells = ranked[0][1].find_all(["th", "td"])
    candidates: list[SourceCandidate] = []
    for index, cell in enumerate(cells[1:], start=1):
        if index >= len(headers):
            continue
        years = extract_year_candidates(headers[index], allow_short=True)
        academic_year = years[0] if years else None
        anchor = cell.find("a", href=True)
        if anchor is None:
            continue
        url = _unwrap_google_redirect(str(anchor["href"]))
        candidates.append(
            SourceCandidate(
                url=url,
                label=f"{school_name} {headers[index]} CDS",
                academic_year=academic_year,
                discovery_source="college_transitions",
                discovery_url=COLLEGE_TRANSITIONS_URL,
                official=False,
                score=0.5,
                notes=["Repository mirror; document identity must be verified after download."],
            )
        )
    return candidates, []


def discover_school(
    school_name: str,
    *,
    school_slug: str | None = None,
    workspace_dir: str | Path = ".cds_pipeline",
    archive_url: str | None = None,
    repository_fallback: bool = True,
) -> DiscoveryManifest:
    slug = validate_slug(school_slug or slugify(school_name))
    workspace = Path(workspace_dir)
    client = CachedHttpClient(workspace / "_http_cache")
    warnings: list[str] = []
    official_site = None
    try:
        official_site = _canonical_site(archive_url) if archive_url else resolve_official_site(school_name, client)
    except Exception as exc:
        warnings.append(f"Could not resolve the official institution site: {exc}")

    official_candidates: list[SourceCandidate] = []
    archive_pages: list[str] = []
    if official_site:
        found, archive_pages, official_warnings = discover_official_candidates(
            school_name,
            official_site,
            client,
            archive_url=archive_url,
        )
        official_candidates.extend(found)
        warnings.extend(official_warnings)
    else:
        warnings.append("No official institution website was resolved.")

    repository_candidates: list[SourceCandidate] = []
    if repository_fallback:
        found, repository_warnings = discover_repository_candidates(school_name, client)
        repository_candidates.extend(found)
        warnings.extend(repository_warnings)

    # Prefer an official link for each year, while retaining repository years
    # missing from the institution archive.
    selected: dict[tuple[str | None, str], SourceCandidate] = {}
    for candidate in official_candidates + repository_candidates:
        key = (candidate.academic_year, candidate.url)
        selected[key] = candidate
    candidates = sorted(
        selected.values(),
        key=lambda item: (item.academic_year or "0000", item.official, item.score),
        reverse=True,
    )
    manifest = DiscoveryManifest(
        school_name=school_name,
        school_slug=slug,
        official_site=official_site,
        official_archive_pages=archive_pages,
        candidates=candidates,
        warnings=warnings,
    )
    write_json(workspace / slug / "discovery.json", manifest.model_dump(mode="json"))
    return manifest
