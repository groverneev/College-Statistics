from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from .models import SchoolManifest, SectionExtraction, SectionPacket
from .registry import generate_registry
from .specs import spec_for_domain
from .utils import read_json, validate_slug, write_json
from .validator import validate_school_data, validate_section_extraction


PUBLISH_REQUIRED_PATHS = (
    "admissions.applied",
    "admissions.admitted",
    "admissions.enrolled",
    "demographics.enrollment.undergraduate",
    "demographics.enrollment.total",
    "demographics.byRace.international",
    "demographics.byRace.hispanicLatino",
    "demographics.byRace.blackAfricanAmerican",
    "demographics.byRace.white",
    "demographics.byRace.asian",
    "demographics.byRace.americanIndianAlaskaNative",
    "demographics.byRace.nativeHawaiianPacificIslander",
    "demographics.byRace.twoOrMoreRaces",
    "demographics.byRace.unknown",
    "costs.tuition",
    "costs.fees",
    "costs.roomAndBoard",
)


def _set_nested(payload: dict[str, Any], path: str, value: Any) -> None:
    current = payload
    parts = path.split(".")
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    current[parts[-1]] = value


def _get_nested(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _derive(year_data: dict[str, Any]) -> None:
    applied = _get_nested(year_data, "admissions.applied")
    admitted = _get_nested(year_data, "admissions.admitted")
    enrolled = _get_nested(year_data, "admissions.enrolled")
    if isinstance(applied, (int, float)) and applied and isinstance(admitted, (int, float)):
        _set_nested(year_data, "admissions.acceptanceRate", round(admitted / applied, 4))
    if isinstance(admitted, (int, float)) and admitted and isinstance(enrolled, (int, float)):
        _set_nested(year_data, "admissions.yield", round(enrolled / admitted, 4))

    undergraduate = _get_nested(year_data, "demographics.enrollment.undergraduate")
    graduate = _get_nested(year_data, "demographics.enrollment.graduate")
    total = _get_nested(year_data, "demographics.enrollment.total")
    if total is None and isinstance(undergraduate, (int, float)) and isinstance(graduate, (int, float)):
        _set_nested(year_data, "demographics.enrollment.total", int(undergraduate + graduate))

    tuition = _get_nested(year_data, "costs.tuition")
    fees = _get_nested(year_data, "costs.fees")
    room_and_board = _get_nested(year_data, "costs.roomAndBoard")
    room = _get_nested(year_data, "costs.room")
    board = _get_nested(year_data, "costs.board")
    if room_and_board is None and isinstance(room, (int, float)) and isinstance(board, (int, float)):
        room_and_board = int(room + board)
        _set_nested(year_data, "costs.roomAndBoard", room_and_board)
    if all(isinstance(value, (int, float)) for value in (tuition, fees, room_and_board)):
        # This preserves the site's displayed tuition + fees + room/board series.
        # It is not represented as the institution's broader published COA budget.
        _set_nested(year_data, "costs.totalCOA", int(tuition + fees + room_and_board))

    aid_cohort = _get_nested(year_data, "_source.financialAid.cohortSize")
    aid_recipients = _get_nested(year_data, "_source.financialAid.aidRecipientCount")
    financial_need = _get_nested(year_data, "_source.financialAid.financialNeedCount")
    need_fully_met = _get_nested(year_data, "_source.financialAid.needFullyMetCount")
    if isinstance(aid_cohort, (int, float)) and aid_cohort and isinstance(
        aid_recipients, (int, float)
    ):
        _set_nested(
            year_data,
            "financialAid.percentReceivingAid",
            round(aid_recipients / aid_cohort, 4),
        )
    if isinstance(financial_need, (int, float)) and financial_need and isinstance(
        need_fully_met, (int, float)
    ):
        _set_nested(
            year_data,
            "financialAid.percentNeedFullyMet",
            round(need_fully_met / financial_need, 4),
        )

    costs = year_data.get("costs")
    if isinstance(costs, dict):
        costs.pop("room", None)
        costs.pop("board", None)
    year_data.pop("_source", None)

    year_data.setdefault("testScores", {})
    year_data.setdefault("financialAid", {})


def _resolve_manifest(target: str, workspace_dir: str | Path) -> Path:
    path = Path(target)
    if path.is_file():
        return path
    candidate = Path(workspace_dir) / target / "school_manifest.json"
    if candidate.exists():
        return candidate
    raise ValueError(f"Could not find a school manifest for {target}")


def _portable_source_path(value: str) -> str:
    path = Path(value)
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return value


def _normalize_quote(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def _quote_supports_number(quote: str, value: int | float) -> bool:
    for match in re.findall(r"[-+]?\$?\s*\d[\d,]*(?:\.\d+)?%?", quote):
        cleaned = match.replace("$", "").replace(",", "").replace(" ", "")
        is_percent = cleaned.endswith("%")
        if is_percent:
            cleaned = cleaned[:-1]
        try:
            candidate = float(cleaned) / (100 if is_percent else 1)
        except ValueError:
            continue
        if abs(candidate - float(value)) < 1e-9:
            return True
    return False


def _quote_supports_native_sum(quote: str, value: int | float) -> bool:
    values: list[float] = []
    for match in re.findall(r"[-+]?\$?\s*\d[\d,]*(?:\.\d+)?", quote):
        try:
            values.append(float(match.replace("$", "").replace(",", "").replace(" ", "")))
        except ValueError:
            return False
    return len(values) >= 2 and abs(sum(values) - float(value)) < 1e-9


def compile_school(
    target: str,
    *,
    workspace_dir: str | Path = ".cds_pipeline",
    publish: bool = False,
) -> dict[str, Any]:
    manifest_path = _resolve_manifest(target, workspace_dir)
    manifest = SchoolManifest.model_validate(read_json(manifest_path))
    validate_slug(manifest.school_slug)
    document_paths = {document.document_id: document.source_path for document in manifest.documents}
    documents = {document.document_id: document for document in manifest.documents}
    valid_years = {
        document.academic_year for document in manifest.documents if document.academic_year
    }
    extraction_root = (manifest_path.parent / "extractions").resolve()
    routed_evidence_pages: set[tuple[str, str, str, int]] = set()
    for packet_path_value in manifest.packet_paths:
        packet_path = Path(packet_path_value)
        if not packet_path.exists():
            continue
        packet = SectionPacket.model_validate(read_json(packet_path))
        routed_evidence_pages.update(
            (
                packet.academic_year,
                packet.domain,
                packet_page.document_id,
                packet_page.page,
            )
            for packet_page in packet.pages
        )

    years: dict[str, dict[str, Any]] = {}
    profiles: dict[str, dict[str, Any]] = {}
    issues: list[dict[str, str]] = []
    year_blockers: dict[str, list[str]] = {}

    def block_year(academic_year: str, reason: str) -> None:
        year_blockers.setdefault(academic_year, []).append(reason)

    if manifest.review_required:
        issues.append(
            {
                "severity": "warning",
                "kind": "manifest_requires_review",
                "message": "Some acquisition or document analysis items require review; safe complete years are evaluated independently.",
            }
        )
    for document in manifest.documents if manifest.review_required else []:
        if not document.academic_year:
            continue
        reasons: list[str] = []
        if document.ocr_pending_pages:
            reasons.append("routed pages still require OCR")
        if not document.year_verified:
            reasons.append("academic year is not verified")
        if document.year_conflict:
            reasons.append("filename and document year conflict")
        if document.school_match_score < 0.5:
            reasons.append("document weakly matches the requested school")
        for reason in reasons:
            block_year(document.academic_year, reason)
    seen: dict[tuple[str, str], Any] = {}
    for extraction_path_value in manifest.extraction_paths:
        extraction_path = Path(extraction_path_value).resolve()
        if not extraction_path.is_relative_to(extraction_root):
            issues.append(
                {
                    "severity": "error",
                    "kind": "extraction_path_escape",
                    "message": str(extraction_path),
                }
            )
            continue
        if not extraction_path.exists():
            issues.append({"severity": "error", "kind": "missing_extraction", "message": str(extraction_path)})
            continue
        academic_year = extraction_path.parent.name
        if academic_year not in valid_years:
            issues.append(
                {
                    "severity": "error",
                    "kind": "invalid_extraction_year",
                    "message": f"{academic_year} is not a verified manifest document year.",
                }
            )
            continue
        extraction = SectionExtraction.model_validate(read_json(extraction_path))
        has_c7 = any(
            observation.path.startswith("profile.admissionsFactors.")
            and observation.value is not None
            for observation in extraction.observations
        )
        c7_complete = set(spec_for_domain("admissions_factors").metric_paths).issubset(
            {
                observation.path
                for observation in extraction.observations
                if observation.value is not None and not observation.review_required
            }
        )
        c7_verified = any(
            marker in note
            for note in extraction.notes
            for marker in (
                "C7 independently verified",
                "C7 deterministically verified",
                "Manual C7 verification",
                "Structured extraction provider: Codex",
                "Structured extraction provider: openai/",
            )
        )
        if has_c7 and (not c7_verified or not c7_complete):
            issues.append(
                {
                    "severity": "warning",
                    "kind": "unverified_c7_matrix",
                    "message": f"{academic_year} C7 is incomplete or lacks independent adjudication.",
                }
            )
        extraction_validation = validate_section_extraction(extraction.model_dump(mode="json"))
        for issue in extraction_validation["issues"]:
            issues.append(
                {
                    **issue,
                    "severity": "warning",
                    "message": f"{academic_year} {extraction_path.stem}: {issue['message']}",
                }
            )
        for observation in extraction.observations:
            if observation.value is None:
                continue
            if observation.review_required:
                issues.append(
                    {
                        "severity": "warning",
                        "kind": "observation_requires_review",
                        "message": f"{academic_year} {observation.path} was excluded because it requires review.",
                    }
                )
                if observation.path in PUBLISH_REQUIRED_PATHS:
                    block_year(academic_year, f"{observation.path} requires review")
                continue
            evidence_valid = False
            aggregate_values: list[float] = []
            aggregate_evidence_valid = True
            for evidence in observation.evidence:
                document = documents.get(evidence.document_id)
                if document is None or document.academic_year != academic_year:
                    continue
                page = next((item for item in document.pages if item.page == evidence.page), None)
                if page is None:
                    continue
                normalized_quote = _normalize_quote(evidence.quote)
                if not normalized_quote or normalized_quote not in _normalize_quote(page.text):
                    continue
                if isinstance(observation.value, bool):
                    continue
                if isinstance(observation.value, (int, float)):
                    direct_support = _quote_supports_number(evidence.quote, observation.value)
                    summed_c1_support = (
                        observation.method == "native-rule"
                        and observation.notes
                        == "Deterministic sum of the numeric C1 gender columns in the quoted row."
                        and evidence.question_id == "C1"
                        and _quote_supports_native_sum(evidence.quote, observation.value)
                    )
                    normalized_percent_support = (
                        observation.method == "native-rule"
                        and observation.notes
                        == "Percent value normalized from CDS numeric percent cell."
                        and _quote_supports_number(evidence.quote, float(observation.value) * 100)
                    )
                    if not direct_support and not summed_c1_support and not normalized_percent_support:
                        if observation.notes == "Deterministic sum of cited C1 gender cells.":
                            numbers = re.findall(r"[-+]?\$?\s*\d[\d,]*(?:\.\d+)?", evidence.quote)
                            if len(numbers) == 1:
                                aggregate_values.append(
                                    float(numbers[0].replace("$", "").replace(",", "").replace(" ", ""))
                                )
                                continue
                        aggregate_evidence_valid = False
                        continue
                if evidence.question_id and evidence.question_id not in page.question_ids:
                    inherited_continuation = (
                        academic_year,
                        extraction_path.stem,
                        evidence.document_id,
                        evidence.page,
                    ) in routed_evidence_pages
                    if not inherited_continuation:
                        continue
                evidence_valid = True
                break
            if (
                not evidence_valid
                and observation.notes == "Deterministic sum of cited C1 gender cells."
                and aggregate_evidence_valid
                and len(aggregate_values) >= 2
                and abs(sum(aggregate_values) - float(observation.value)) < 1e-9
            ):
                evidence_valid = True
            if not evidence_valid:
                issues.append(
                    {
                        "severity": "warning",
                        "kind": "invalid_source_evidence",
                        "message": f"{academic_year} {observation.path} was excluded because its evidence did not match the manifest.",
                    }
                )
                if observation.path in PUBLISH_REQUIRED_PATHS:
                    block_year(academic_year, f"{observation.path} lacks valid source evidence")
                continue
            key = (academic_year, observation.path)
            if key in seen and seen[key] != observation.value:
                issues.append(
                    {
                        "severity": "warning",
                        "kind": "conflicting_observation",
                        "message": f"{academic_year} {observation.path} has conflicting values.",
                    }
                )
                block_year(academic_year, f"{observation.path} has conflicting values")
                continue
            seen[key] = observation.value
            if observation.path.startswith("profile."):
                if c7_verified and c7_complete:
                    _set_nested(profiles.setdefault(academic_year, {}), observation.path, observation.value)
            else:
                _set_nested(years.setdefault(academic_year, {}), observation.path, observation.value)

    complete_years: dict[str, dict[str, Any]] = {}
    excluded_years: dict[str, list[str]] = {}
    for academic_year, year_data in sorted(years.items()):
        _derive(year_data)
        missing = [path for path in PUBLISH_REQUIRED_PATHS if _get_nested(year_data, path) is None]
        reasons = list(dict.fromkeys(year_blockers.get(academic_year, [])))
        if missing:
            reasons.append("missing required metrics: " + ", ".join(missing))
        if reasons:
            excluded_years[academic_year] = reasons
            issues.append(
                {
                    "severity": "warning",
                    "kind": "excluded_year",
                    "message": f"{academic_year} was excluded: {'; '.join(reasons)}",
                }
            )
        else:
            complete_years[academic_year] = year_data

    school_data: dict[str, Any] = {
        "name": manifest.school_name,
        "slug": manifest.school_slug,
        "years": complete_years,
    }
    if profiles:
        latest_profile_year = sorted(profiles)[-1]
        profile = profiles[latest_profile_year]
        factors = _get_nested(profile, "profile.admissionsFactors")
        if isinstance(factors, dict):
            factors["sourceYear"] = latest_profile_year
            factors["section"] = "C7"
            source_pdf = None
            for extraction_path_value in manifest.extraction_paths:
                path = Path(extraction_path_value)
                if path.parent.name == latest_profile_year and path.stem == "admissions_factors":
                    extraction = SectionExtraction.model_validate(read_json(path))
                    for observation in extraction.observations:
                        if observation.evidence:
                            source_pdf = document_paths.get(observation.evidence[0].document_id)
                            if source_pdf:
                                break
            if source_pdf:
                factors["sourcePdf"] = _portable_source_path(source_pdf)
                school_data["profile"] = {"admissionsFactors": factors}

    validation = validate_school_data(school_data)
    issues.extend(validation["issues"])
    if not complete_years:
        issues.append({"severity": "error", "kind": "no_complete_years", "message": "No complete years can be published."})

    report = {
        "school_name": manifest.school_name,
        "school_slug": manifest.school_slug,
        "compiled_years": sorted(complete_years),
        "excluded_years": excluded_years,
        "issue_count": len(issues),
        "error_count": sum(issue.get("severity") == "error" for issue in issues),
        "warning_count": sum(issue.get("severity") == "warning" for issue in issues),
        "issues": issues,
        "published": False,
    }
    compiled_path = manifest_path.parent / "compiled" / f"{manifest.school_slug}.json"
    report_path = manifest_path.parent / "compiled" / "report.json"
    write_json(compiled_path, school_data)

    if publish:
        if report["error_count"]:
            write_json(report_path, report)
            raise ValueError(f"Publication blocked by {report['error_count']} errors. See {report_path}")
        destination = Path("src/data/schools") / f"{manifest.school_slug}.json"
        write_json(destination, school_data)
        generate_registry()
        report["published"] = True
        report["destination"] = str(destination.resolve())
    write_json(report_path, report)
    report["compiled_path"] = str(compiled_path.resolve())
    report["report_path"] = str(report_path.resolve())
    return report
