from __future__ import annotations

import re
from typing import Any

from .models import FieldMeta
from .utils import parse_number, parse_percent, squish


BUILTIN_FORM_ALIASES: dict[str, list[str]] = {
    "costs.tuition": ["TUIT_STATE_FT_D", "TUIT_STATE_FT_U", "TUITION_IN_STATE"],
    "costs.fees": ["FEES_FT_D", "FEES_FT_U", "REQUIRED_FEES"],
    "costs.roomAndBoard": ["RM_BD_D", "FOOD_HOUS_D", "ROOM_BOARD"],
    "costs.totalCOA": ["TOT_EXPENSE_D", "TOT_EXPENSE_U", "TOTAL_COST"],
}


DEFAULT_TEXT_PATTERNS: dict[str, list[str]] = {
    "admissions.applied": [
        r"Total\s+first[- ]time.*?applicants.*?(\d[\d,]*)",
        r"Number\s+of\s+applicants.*?(\d[\d,]*)",
        r"C1.*?Applicants.*?(\d[\d,]*)",
    ],
    "admissions.admitted": [
        r"Total\s+first[- ]time.*?admitted.*?(\d[\d,]*)",
        r"Number.*?admitted.*?(\d[\d,]*)",
        r"C1.*?Admitted.*?(\d[\d,]*)",
    ],
    "admissions.enrolled": [
        r"Total\s+first[- ]time.*?enrolled.*?(\d[\d,]*)",
        r"Number.*?enrolled.*?(\d[\d,]*)",
        r"C1.*?Enrolled.*?(\d[\d,]*)",
    ],
    "demographics.enrollment.undergraduate": [
        r"Total\s+full[- ]time,\s*first[- ]time.*?undergraduate.*?(\d[\d,]*)",
        r"Total\s+undergraduate\s+enrollment.*?(\d[\d,]*)",
        r"Undergraduate\s+degree-seeking.*?(\d[\d,]*)",
    ],
    "demographics.enrollment.graduate": [
        r"Total\s+graduate\s+enrollment.*?(\d[\d,]*)",
        r"Graduate.*?enrollment.*?(\d[\d,]*)",
    ],
    "demographics.byRace.international": [
        r"Nonresident\s+aliens?.*?(\d[\d,]*)",
        r"International.*?(\d[\d,]*)",
    ],
    "demographics.byRace.hispanicLatino": [r"Hispanic.*?Latino.*?(\d[\d,]*)"],
    "demographics.byRace.blackAfricanAmerican": [r"Black.*?African.*?American.*?(\d[\d,]*)"],
    "demographics.byRace.white": [r"\bWhite\b.*?(\d[\d,]*)"],
    "demographics.byRace.asian": [r"\bAsian\b.*?(\d[\d,]*)"],
    "demographics.byRace.americanIndianAlaskaNative": [r"American\s+Indian.*?Alaska\s+Native.*?(\d[\d,]*)"],
    "demographics.byRace.nativeHawaiianPacificIslander": [r"Native\s+Hawaiian.*?Pacific\s+Islander.*?(\d[\d,]*)"],
    "demographics.byRace.twoOrMoreRaces": [r"Two\s+or\s+more\s+races.*?(\d[\d,]*)"],
    "demographics.byRace.unknown": [r"Race.*?unknown.*?(\d[\d,]*)", r"\bUnknown\b.*?(\d[\d,]*)"],
    "costs.tuition": [r"Tuition.*?\$?([\d,]+)"],
    "costs.fees": [r"Required\s+fees.*?\$?([\d,]+)", r"\bFees\b.*?\$?([\d,]+)"],
    "costs.roomAndBoard": [r"Room\s+(?:and|&)\s+board.*?\$?([\d,]+)"],
    "financialAid.averageAidPackage": [r"Average\s+financial\s+aid.*?\$?([\d,]+)"],
    "financialAid.averageNeedBasedGrant": [r"Average.*?need-based.*?grant.*?\$?([\d,]+)"],
}

PERCENT_TEXT_PATTERNS: dict[str, list[str]] = {
    "financialAid.percentReceivingAid": [
        r"Percent.*?receiving.*?aid.*?(\d+\.?\d*)%?",
        r"(\d+\.?\d*)%.*?receiving.*?need-based",
    ],
    "financialAid.percentNeedFullyMet": [
        r"Percent.*?need\s+fully\s+met.*?(\d+\.?\d*)%?",
        r"(\d+\.?\d*)%.*?need\s+fully\s+met",
    ],
    "testScores.sat.submissionRate": [r"SAT.*?submitted.*?(\d+\.?\d*)%?"],
    "testScores.act.submissionRate": [r"ACT.*?submitted.*?(\d+\.?\d*)%?"],
}

SAT_SECTION_PATTERN = re.compile(
    r"SAT\s+(?:Evidence-Based\s+Reading\s+and\s+Writing|ERW).*?(\d{3}).*?(\d{3}).*?(\d{3}).*?"
    r"SAT\s+Math.*?(\d{3}).*?(\d{3}).*?(\d{3})",
    re.IGNORECASE | re.DOTALL,
)
ACT_SECTION_PATTERN = re.compile(
    r"ACT\s+Composite.*?(\d{2}).*?(\d{2}).*?(\d{2})",
    re.IGNORECASE | re.DOTALL,
)


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


def _form_aliases(config: dict[str, Any], field_path: str) -> list[str]:
    aliases = list(BUILTIN_FORM_ALIASES.get(field_path, []))
    aliases.extend(config.get("form_aliases", {}).get(field_path, []))
    return aliases


def _text_patterns(config: dict[str, Any], field_path: str) -> list[str]:
    patterns = list(DEFAULT_TEXT_PATTERNS.get(field_path, []))
    patterns.extend(config.get("text_patterns", {}).get(field_path, []))
    return patterns


def _percent_patterns(config: dict[str, Any], field_path: str) -> list[str]:
    patterns = list(PERCENT_TEXT_PATTERNS.get(field_path, []))
    patterns.extend(config.get("text_patterns", {}).get(field_path, []))
    return patterns


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


def _find_form_value(form_fields: dict[str, Any], aliases: list[str]) -> tuple[Any, str] | None:
    for alias in aliases:
        if alias in form_fields and str(form_fields[alias]).strip():
            return form_fields[alias], alias
    return None


def _find_text_value(text: str, patterns: list[str], parser: Any) -> tuple[Any, str] | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if not match:
            continue
        parsed = parser(match.group(1))
        if parsed is not None:
            return parsed, pattern
    return None


def _collect_text(raw_payload: dict[str, Any]) -> str:
    pieces: list[str] = []
    for key in ["full_text", "structured_markdown", "ocr_full_text"]:
        value = raw_payload.get(key)
        if value:
            pieces.append(str(value))
    return squish("\n".join(pieces))


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
    if undergraduate and international:
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


def _derive_test_scores(data: dict[str, Any], text: str, field_meta: dict[str, dict[str, Any]]) -> None:
    sat_match = SAT_SECTION_PATTERN.search(text)
    if sat_match:
        sat = {
            "composite": {
                "p25": int(sat_match.group(1)) + int(sat_match.group(4)),
                "p50": int(sat_match.group(2)) + int(sat_match.group(5)),
                "p75": int(sat_match.group(3)) + int(sat_match.group(6)),
            },
            "readingWriting": {
                "p25": int(sat_match.group(1)),
                "p50": int(sat_match.group(2)),
                "p75": int(sat_match.group(3)),
            },
            "math": {
                "p25": int(sat_match.group(4)),
                "p50": int(sat_match.group(5)),
                "p75": int(sat_match.group(6)),
            },
            "submissionRate": _get_nested(data, "testScores.sat.submissionRate") or 0,
        }
        data["testScores"]["sat"] = sat
        field_meta["testScores.sat"] = FieldMeta(
            value=sat,
            confidence=0.72,
            status="confirmed",
            source="text_regex",
            source_ref="SAT_SECTION_PATTERN",
            notes=[],
        ).to_dict()

    act_match = ACT_SECTION_PATTERN.search(text)
    if act_match:
        act = {
            "composite": {
                "p25": int(act_match.group(1)),
                "p50": int(act_match.group(2)),
                "p75": int(act_match.group(3)),
            },
            "submissionRate": _get_nested(data, "testScores.act.submissionRate") or 0,
        }
        data["testScores"]["act"] = act
        field_meta["testScores.act"] = FieldMeta(
            value=act,
            confidence=0.7,
            status="confirmed",
            source="text_regex",
            source_ref="ACT_SECTION_PATTERN",
            notes=[],
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
        graduate = 0
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
        race_total = 0

    if race_total == 0:
        for path in [
            "demographics.byResidency.inState",
            "demographics.byResidency.outOfState",
            "demographics.byResidency.international",
        ]:
            if _get_nested(data, path):
                _downgrade_field(data, field_meta, path, 0, "Residency counts suppressed because enrollment/race extraction was low confidence.")

    sat = data["testScores"].get("sat")
    if sat:
        composite = sat.get("composite", {})
        if composite and not (400 <= composite.get("p25", 0) <= composite.get("p50", 0) <= composite.get("p75", 0) <= 1600):
            data["testScores"].pop("sat", None)
            field_meta["testScores.sat"] = FieldMeta(
                value={},
                confidence=0.3,
                status="low_confidence",
                source="heuristic_guardrail",
                source_ref="SAT_SECTION_PATTERN",
                notes=["SAT percentile ordering was invalid, so the SAT block was suppressed."],
            ).to_dict()

    act = data["testScores"].get("act")
    if act:
        composite = act.get("composite", {})
        if composite and not (1 <= composite.get("p25", 0) <= composite.get("p50", 0) <= composite.get("p75", 0) <= 36):
            data["testScores"].pop("act", None)
            field_meta["testScores.act"] = FieldMeta(
                value={},
                confidence=0.3,
                status="low_confidence",
                source="heuristic_guardrail",
                source_ref="ACT_SECTION_PATTERN",
                notes=["ACT percentile ordering was invalid, so the ACT block was suppressed."],
            ).to_dict()

    for path in ["costs.tuition", "costs.fees", "costs.roomAndBoard"]:
        value = _get_nested(data, path)
        if isinstance(value, (int, float)) and 0 < value < 100:
            _downgrade_field(data, field_meta, path, 0, "Cost value looked like a row number or footnote marker.")
    if not any((_get_nested(data, path) or 0) for path in ["costs.tuition", "costs.fees", "costs.roomAndBoard"]):
        _downgrade_field(data, field_meta, "costs.totalCOA", 0, "Total cost suppressed because component costs were low confidence.")


def normalize_document(raw_payload: dict[str, Any], config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    data = _empty_year_data()
    field_meta: dict[str, dict[str, Any]] = {}
    form_fields = raw_payload.get("form_fields", {})
    text = _collect_text(raw_payload)

    numeric_fields = [
        "admissions.applied",
        "admissions.admitted",
        "admissions.enrolled",
        "demographics.enrollment.undergraduate",
        "demographics.enrollment.graduate",
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
        "financialAid.averageAidPackage",
        "financialAid.averageNeedBasedGrant",
    ]

    for path in numeric_fields:
        form_match = _find_form_value(form_fields, _form_aliases(config, path))
        if form_match:
            parsed = parse_number(form_match[0])
            if parsed is not None:
                _set_field(data, field_meta, path, parsed, confidence=0.97, source="acroform", source_ref=form_match[1])
                continue

        text_match = _find_text_value(text, _text_patterns(config, path), parse_number)
        if text_match:
            _set_field(data, field_meta, path, text_match[0], confidence=0.74, source="text_regex", source_ref=text_match[1])

    for path in [
        "financialAid.percentReceivingAid",
        "financialAid.percentNeedFullyMet",
        "testScores.sat.submissionRate",
        "testScores.act.submissionRate",
    ]:
        text_match = _find_text_value(text, _percent_patterns(config, path), parse_percent)
        if text_match:
            _set_field(data, field_meta, path, round(float(text_match[0]), 4), confidence=0.7, source="text_regex", source_ref=text_match[1])

    _derive_test_scores(data, text, field_meta)
    _derive_admissions(data, field_meta)
    _derive_costs(data, field_meta)
    _derive_enrollment(data, field_meta)
    _sanitize_document(data, field_meta)
    _derive_costs(data, field_meta)
    _derive_enrollment(data, field_meta)

    return data, field_meta
