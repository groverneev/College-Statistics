from __future__ import annotations

from typing import Any

from .models import FieldMeta
from .utils import parse_number, parse_percent


def _empty_year_data() -> dict[str, Any]:
    return {
        "admissions": {
            "applied": 0,
            "admitted": 0,
            "enrolled": 0,
            "acceptanceRate": 0,
            "yield": 0,
        },
        "testScores": {},
        "demographics": {
            "enrollment": {
                "total": 0,
                "undergraduate": 0,
                "graduate": 0,
            },
            "byRace": {
                "international": 0,
                "hispanicLatino": 0,
                "blackAfricanAmerican": 0,
                "white": 0,
                "asian": 0,
                "americanIndianAlaskaNative": 0,
                "nativeHawaiianPacificIslander": 0,
                "twoOrMoreRaces": 0,
                "unknown": 0,
            },
            "byResidency": {
                "inState": 0,
                "outOfState": 0,
                "international": 0,
            },
        },
        "costs": {
            "tuition": 0,
            "fees": 0,
            "roomAndBoard": 0,
            "totalCOA": 0,
        },
        "financialAid": {
            "percentReceivingAid": 0,
            "averageAidPackage": 0,
            "averageNeedBasedGrant": 0,
            "percentNeedFullyMet": 0,
        },
    }


def _set_nested(payload: dict[str, Any], path: str, value: Any) -> None:
    keys = path.split(".")
    current = payload
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value


def _get_nested(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for key in path.split("."):
        current = current.get(key) if isinstance(current, dict) else None
        if current is None:
            return None
    return current


def _set_field(
    data: dict[str, Any],
    field_meta: dict[str, dict[str, Any]],
    path: str,
    value: Any,
    *,
    confidence: float,
    source: str,
    source_ref: str | None = None,
    status: str = "confirmed",
    notes: list[str] | None = None,
) -> None:
    _set_nested(data, path, value)
    field_meta[path] = FieldMeta(
        value=value,
        confidence=round(confidence, 3),
        status=status,
        source=source,
        source_ref=source_ref,
        notes=notes or [],
    ).to_dict()


def _downgrade_field(
    data: dict[str, Any],
    field_meta: dict[str, dict[str, Any]],
    path: str,
    replacement: Any,
    reason: str,
) -> None:
    _set_nested(data, path, replacement)
    existing = field_meta.get(path, {})
    field_meta[path] = FieldMeta(
        value=replacement,
        confidence=min(float(existing.get("confidence", 0.35)), 0.35),
        status="low_confidence",
        source=existing.get("source", "heuristic_guardrail"),
        source_ref=existing.get("source_ref"),
        notes=[*existing.get("notes", []), reason],
    ).to_dict()


def _vision_field_parser(path: str) -> Any:
    percent_fields = {
        "financialAid.percentReceivingAid",
        "financialAid.percentNeedFullyMet",
        "testScores.sat.submissionRate",
        "testScores.act.submissionRate",
        "computed.demographics.outOfStatePercent",
    }
    return parse_percent if path in percent_fields else parse_number


def _finalize_score_blocks(data: dict[str, Any], field_meta: dict[str, dict[str, Any]]) -> None:
    sat_fields = {
        "composite": {
            "p25": _get_nested(data, "testScores.sat.composite.p25"),
            "p50": _get_nested(data, "testScores.sat.composite.p50"),
            "p75": _get_nested(data, "testScores.sat.composite.p75"),
        },
        "readingWriting": {
            "p25": _get_nested(data, "testScores.sat.readingWriting.p25"),
            "p50": _get_nested(data, "testScores.sat.readingWriting.p50"),
            "p75": _get_nested(data, "testScores.sat.readingWriting.p75"),
        },
        "math": {
            "p25": _get_nested(data, "testScores.sat.math.p25"),
            "p50": _get_nested(data, "testScores.sat.math.p50"),
            "p75": _get_nested(data, "testScores.sat.math.p75"),
        },
    }
    sat_present = any(any(value for value in block.values()) for block in sat_fields.values())
    sat_submission = _get_nested(data, "testScores.sat.submissionRate") or 0
    if sat_present or sat_submission:
        sat = {
            "submissionRate": sat_submission,
            "composite": sat_fields["composite"],
            "readingWriting": sat_fields["readingWriting"],
            "math": sat_fields["math"],
        }
        data["testScores"]["sat"] = sat
        field_meta["testScores.sat"] = FieldMeta(
            value=sat,
            confidence=min(
                0.99,
                max(
                    float(field_meta.get("testScores.sat.submissionRate", {}).get("confidence", 0)),
                    float(field_meta.get("testScores.sat.composite.p50", {}).get("confidence", 0)),
                    float(field_meta.get("testScores.sat.readingWriting.p50", {}).get("confidence", 0)),
                    float(field_meta.get("testScores.sat.math.p50", {}).get("confidence", 0)),
                ),
            ),
            status="confirmed",
            source="vision_llm",
            source_ref="C9",
            notes=[],
        ).to_dict()

    act_submission = _get_nested(data, "testScores.act.submissionRate") or 0
    act_composite = {
        "p25": _get_nested(data, "testScores.act.composite.p25"),
        "p50": _get_nested(data, "testScores.act.composite.p50"),
        "p75": _get_nested(data, "testScores.act.composite.p75"),
    }
    if any(act_composite.values()) or act_submission:
        act = {
            "submissionRate": act_submission,
            "composite": act_composite,
        }
        data["testScores"]["act"] = act
        field_meta["testScores.act"] = FieldMeta(
            value=act,
            confidence=min(
                0.99,
                max(
                    float(field_meta.get("testScores.act.submissionRate", {}).get("confidence", 0)),
                    float(field_meta.get("testScores.act.composite.p50", {}).get("confidence", 0)),
                ),
            ),
            status="confirmed",
            source="vision_llm",
            source_ref="C9",
            notes=[],
        ).to_dict()


def _apply_vision_candidates(
    raw_payload: dict[str, Any],
    data: dict[str, Any],
    field_meta: dict[str, dict[str, Any]],
) -> None:
    candidates = raw_payload.get("vision_field_candidates", []) or []
    best_by_field: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        field = candidate.get("field")
        if not field:
            continue
        confidence = float(candidate.get("confidence", 0) or 0)
        existing = best_by_field.get(field)
        if existing and float(existing.get("confidence", 0) or 0) >= confidence:
            continue
        best_by_field[field] = candidate

    for path, candidate in best_by_field.items():
        parser = _vision_field_parser(path)
        parsed = parser(candidate.get("value"))
        if parsed is None:
            continue
        evidence = str(candidate.get("evidence_label", "")).strip()
        page = candidate.get("page")
        section = candidate.get("section")
        source_ref = f"{section} p.{page}"
        if evidence:
            source_ref = f"{source_ref}: {evidence}"
        value = round(float(parsed), 4) if parser is parse_percent else parsed
        _set_field(
            data,
            field_meta,
            path,
            value,
            confidence=min(0.99, max(0.0, float(candidate.get("confidence", 0.0)))),
            source="vision_llm",
            source_ref=source_ref,
            notes=[],
        )


def _derive_admissions(data: dict[str, Any], field_meta: dict[str, dict[str, Any]]) -> None:
    applied = _get_nested(data, "admissions.applied") or 0
    admitted = _get_nested(data, "admissions.admitted") or 0
    enrolled = _get_nested(data, "admissions.enrolled") or 0
    if applied and admitted:
        _set_field(
            data,
            field_meta,
            "admissions.acceptanceRate",
            round(admitted / applied, 4),
            confidence=0.78,
            source="derived",
            status="derived",
            notes=["Derived from admitted / applied."],
        )
    if admitted and enrolled:
        _set_field(
            data,
            field_meta,
            "admissions.yield",
            round(enrolled / admitted, 4),
            confidence=0.78,
            source="derived",
            status="derived",
            notes=["Derived from enrolled / admitted."],
        )


def _derive_costs(data: dict[str, Any], field_meta: dict[str, dict[str, Any]]) -> None:
    tuition = _get_nested(data, "costs.tuition") or 0
    fees = _get_nested(data, "costs.fees") or 0
    room = _get_nested(data, "costs.roomAndBoard") or 0
    if tuition or fees or room:
        _set_field(
            data,
            field_meta,
            "costs.totalCOA",
            tuition + fees + room,
            confidence=0.75,
            source="derived",
            status="derived",
            notes=["Derived from tuition + fees + roomAndBoard."],
        )


def _derive_enrollment(data: dict[str, Any], field_meta: dict[str, dict[str, Any]]) -> None:
    undergraduate = _get_nested(data, "demographics.enrollment.undergraduate") or 0
    graduate = _get_nested(data, "demographics.enrollment.graduate") or 0
    if undergraduate or graduate:
        _set_field(
            data,
            field_meta,
            "demographics.enrollment.total",
            undergraduate + graduate,
            confidence=0.76,
            source="derived",
            status="derived",
            notes=["Derived from undergraduate + graduate enrollment."],
        )

    international = _get_nested(data, "demographics.byRace.international") or 0
    if undergraduate and international and not _get_nested(data, "demographics.byResidency.international"):
        _set_field(
            data,
            field_meta,
            "demographics.byResidency.international",
            international,
            confidence=0.73,
            source="derived",
            status="derived",
            notes=["Mirrors international undergraduate count."],
        )


def _derive_residency_from_vision_percent(data: dict[str, Any], field_meta: dict[str, dict[str, Any]]) -> None:
    out_pct = _get_nested(data, "computed.demographics.outOfStatePercent") or 0
    undergraduate = _get_nested(data, "demographics.enrollment.undergraduate") or 0
    international = _get_nested(data, "demographics.byRace.international") or _get_nested(data, "demographics.byResidency.international") or 0
    if not out_pct or not undergraduate:
        return

    domestic = max(undergraduate - international, 0)
    out_of_state = int(round(domestic * float(out_pct)))
    in_state = max(domestic - out_of_state, 0)
    if not _get_nested(data, "demographics.byResidency.outOfState"):
        _set_field(
            data,
            field_meta,
            "demographics.byResidency.outOfState",
            out_of_state,
            confidence=0.82,
            source="derived",
            status="derived",
            source_ref="computed.demographics.outOfStatePercent",
            notes=["Derived from vision-extracted out-of-state percentage."],
        )
    if not _get_nested(data, "demographics.byResidency.inState"):
        _set_field(
            data,
            field_meta,
            "demographics.byResidency.inState",
            in_state,
            confidence=0.82,
            source="derived",
            status="derived",
            source_ref="computed.demographics.outOfStatePercent",
            notes=["Derived from domestic - out-of-state."],
        )


def _sanitize_document(data: dict[str, Any], field_meta: dict[str, dict[str, Any]]) -> None:
    for path in ["testScores.sat.submissionRate", "testScores.act.submissionRate"]:
        value = _get_nested(data, path)
        if isinstance(value, (int, float)) and (value < 0 or value > 1):
            _downgrade_field(data, field_meta, path, 0, "Submission rate fell outside 0-1, likely a false positive.")

    applied = _get_nested(data, "admissions.applied") or 0
    admitted = _get_nested(data, "admissions.admitted") or 0
    enrolled = _get_nested(data, "admissions.enrolled") or 0
    if applied and (applied < 100 or admitted > applied * 2 or admitted < enrolled):
        _downgrade_field(data, field_meta, "admissions.applied", 0, "Applicant count looked implausible for a CDS total.")
        _downgrade_field(data, field_meta, "admissions.acceptanceRate", 0, "Acceptance rate suppressed because admissions counts were implausible.")

    undergraduate = _get_nested(data, "demographics.enrollment.undergraduate") or 0
    graduate = _get_nested(data, "demographics.enrollment.graduate") or 0
    if 1900 <= undergraduate <= 2100:
        _downgrade_field(
            data,
            field_meta,
            "demographics.enrollment.undergraduate",
            0,
            "Undergraduate enrollment looked like an academic year, not a student count.",
        )
        undergraduate = 0
    if graduate == 1:
        _downgrade_field(
            data,
            field_meta,
            "demographics.enrollment.graduate",
            0,
            "Graduate enrollment looked like a parsing artifact.",
        )
    if undergraduate == 0:
        _downgrade_field(data, field_meta, "demographics.enrollment.total", 0, "Enrollment total suppressed because enrollment extraction was low confidence.")

    race_paths = [
        "demographics.byRace.international",
        "demographics.byRace.hispanicLatino",
        "demographics.byRace.blackAfricanAmerican",
        "demographics.byRace.white",
        "demographics.byRace.asian",
        "demographics.byRace.americanIndianAlaskaNative",
        "demographics.byRace.nativeHawaiianPacificIslander",
        "demographics.byRace.twoOrMoreRaces",
        "demographics.byRace.unknown",
    ]
    race_total = sum((_get_nested(data, path) or 0) for path in race_paths)
    if (undergraduate and race_total > undergraduate * 1.2) or (not undergraduate and race_total):
        for path in race_paths:
            _downgrade_field(data, field_meta, path, 0, "Race breakdown suppressed because totals did not reconcile.")

    sat = data["testScores"].get("sat")
    if sat:
        composite = sat.get("composite", {})
        if any(composite.values()) and not (400 <= composite.get("p25", 0) <= composite.get("p50", 0) <= composite.get("p75", 0) <= 1600):
            data["testScores"].pop("sat", None)
            field_meta["testScores.sat"] = FieldMeta(
                value={},
                confidence=0.3,
                status="low_confidence",
                source="heuristic_guardrail",
                source_ref="C9",
                notes=["SAT percentile ordering was invalid, so the SAT block was suppressed."],
            ).to_dict()

    act = data["testScores"].get("act")
    if act:
        composite = act.get("composite", {})
        if any(composite.values()) and not (1 <= composite.get("p25", 0) <= composite.get("p50", 0) <= composite.get("p75", 0) <= 36):
            data["testScores"].pop("act", None)
            field_meta["testScores.act"] = FieldMeta(
                value={},
                confidence=0.3,
                status="low_confidence",
                source="heuristic_guardrail",
                source_ref="C9",
                notes=["ACT percentile ordering was invalid, so the ACT block was suppressed."],
            ).to_dict()

    for path in ["costs.tuition", "costs.fees", "costs.roomAndBoard"]:
        value = _get_nested(data, path)
        if isinstance(value, (int, float)) and 0 < value < 100:
            _downgrade_field(data, field_meta, path, 0, "Cost value looked like a row number or footnote marker.")
    if not any((_get_nested(data, path) or 0) for path in ["costs.tuition", "costs.fees", "costs.roomAndBoard"]):
        _downgrade_field(data, field_meta, "costs.totalCOA", 0, "Total cost suppressed because component costs were low confidence.")


def _cleanup_internal_fields(data: dict[str, Any], field_meta: dict[str, dict[str, Any]]) -> None:
    data.pop("computed", None)
    for path in [key for key in field_meta if key.startswith("computed.")]:
        field_meta.pop(path, None)


def normalize_document(raw_payload: dict[str, Any], config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    del config
    data = _empty_year_data()
    field_meta: dict[str, dict[str, Any]] = {}
    _apply_vision_candidates(raw_payload, data, field_meta)
    _finalize_score_blocks(data, field_meta)
    _derive_admissions(data, field_meta)
    _derive_costs(data, field_meta)
    _derive_enrollment(data, field_meta)
    _derive_residency_from_vision_percent(data, field_meta)
    _sanitize_document(data, field_meta)
    _derive_costs(data, field_meta)
    _derive_enrollment(data, field_meta)
    _cleanup_internal_fields(data, field_meta)
    return data, field_meta
