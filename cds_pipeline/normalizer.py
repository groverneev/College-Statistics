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


def _normalize_label(value: str) -> str:
    return squish(value).lower()


def _table_rows(raw_payload: dict[str, Any]) -> list[dict[str, Any]]:
    return raw_payload.get("tables", []) or []


def _find_table_by_header(raw_payload: dict[str, Any], header_token: str) -> dict[str, Any] | None:
    header_token = _normalize_label(header_token)
    for table in _table_rows(raw_payload):
        rows = table.get("rows", [])
        if not rows:
            continue
        first_row = " ".join(str(cell) for cell in rows[0] if cell)
        if header_token in _normalize_label(first_row):
            return table
    return None


def _find_table_with_first_row_tokens(raw_payload: dict[str, Any], *tokens: str) -> dict[str, Any] | None:
    normalized_tokens = [_normalize_label(token) for token in tokens]
    for table in _table_rows(raw_payload):
        rows = table.get("rows", [])
        if not rows:
            continue
        first_cell = _normalize_label(str(rows[0][0])) if rows[0] else ""
        if normalized_tokens and first_cell != normalized_tokens[0]:
            continue
        first_row = _normalize_label(" ".join(str(cell) for cell in rows[0] if cell))
        if all(token in first_row for token in normalized_tokens):
            return table
    return None


def _find_row_value(table: dict[str, Any] | None, row_token: str, column_index: int = -1) -> int | None:
    if not table:
        return None
    row_token = _normalize_label(row_token)
    for row in table.get("rows", []):
        if row and row_token in _normalize_label(" ".join(row)):
            cells = row[1:] if len(row) > 1 else row
            candidates = cells if column_index == -1 else [row[column_index]] if len(row) > column_index else []
            numbers = [parse_number(cell) for cell in candidates]
            numbers = [value for value in numbers if value is not None]
            if numbers:
                return numbers[-1]
    return None


def _sum_row_values(table: dict[str, Any] | None, row_token: str) -> int | None:
    if not table:
        return None
    row_token = _normalize_label(row_token)
    for row in table.get("rows", []):
        if row and row_token in _normalize_label(" ".join(row)):
            numbers = [parse_number(cell) for cell in row[1:]]
            numbers = [value for value in numbers if value is not None]
            if numbers:
                return sum(numbers)
    return None


def _extract_georgetown_from_tables(
    raw_payload: dict[str, Any],
    data: dict[str, Any],
    field_meta: dict[str, dict[str, Any]],
) -> None:
    applicants = _find_table_by_header(raw_payload, "First-Time, First-Year Student Applicants")
    admits = _find_table_by_header(raw_payload, "First-Time, First-Year Student Admits")
    enrollees = _find_table_by_header(raw_payload, "First-Time, First-Year Student Enrollees by Status")
    residency = None
    for table in _table_rows(raw_payload):
        rows = table.get("rows", [])
        if rows and "in-state" in _normalize_label(" ".join(rows[0])) and "international" in _normalize_label(" ".join(rows[0])):
            residency = table
            break

    applied = sum(
        value or 0
        for value in [
            _find_row_value(applicants, "men who applied"),
            _find_row_value(applicants, "women who applied"),
            _find_row_value(applicants, "another gender who applied"),
            _find_row_value(applicants, "unknown gender who applied"),
        ]
    )
    admitted = sum(
        value or 0
        for value in [
            _find_row_value(admits, "men who were admitted"),
            _find_row_value(admits, "women who were admitted"),
            _find_row_value(admits, "another gender who were admitted"),
            _find_row_value(admits, "unknown gender who were admitted"),
        ]
    )
    enrolled = sum(
        value or 0
        for value in [
            _find_row_value(enrollees, "full-time, first-time, first-year men who enrolled"),
            _find_row_value(enrollees, "part-time, first-time, first-year men who enrolled"),
            _find_row_value(enrollees, "full-time, first-time, first-year women who enrolled"),
            _find_row_value(enrollees, "part-time, first-time, first-year women who enrolled"),
            _find_row_value(enrollees, "full-time, first-time, first-year another gender who enrolled"),
            _find_row_value(enrollees, "part-time, first-time, first-year another gender who enrolled"),
            _find_row_value(enrollees, "full-time, first-time, first-year unknown gender who enrolled"),
            _find_row_value(enrollees, "part-time, first-time, first-year unknown gender who enrolled"),
        ]
    )
    if applied:
        _set_field(data, field_meta, "admissions.applied", applied, confidence=0.95, source="table", source_ref="C1 applicants table")
    if admitted:
        _set_field(data, field_meta, "admissions.admitted", admitted, confidence=0.95, source="table", source_ref="C1 admits table")
    if enrolled:
        _set_field(data, field_meta, "admissions.enrolled", enrolled, confidence=0.95, source="table", source_ref="C1 enrollees table")

    if residency:
        residency_rows = residency.get("rows", [])
        for row in residency_rows:
            text = _normalize_label(" ".join(row))
            if "who enrolled" in text:
                if len(row) >= 5:
                    _set_field(data, field_meta, "demographics.byResidency.international", parse_number(row[4]) or 0, confidence=0.84, source="table", source_ref="C1 residency table")
                break

    ug_full = _find_table_with_first_row_tokens(raw_payload, "Undergraduate Students: Full-Time")
    ug_part = _find_table_with_first_row_tokens(raw_payload, "Undergraduate Students: Part-Time")
    grad_all = _find_table_with_first_row_tokens(raw_payload, "Graduate Students: All", "Men", "Women")

    undergraduate = sum(
        value or 0
        for value in [
            _sum_row_values(ug_full, "Total degree-seeking"),
            _sum_row_values(ug_part, "Total degree-seeking"),
        ]
    )
    graduate = _sum_row_values(grad_all, "Total Graduate Students") or 0
    if undergraduate:
        _set_field(data, field_meta, "demographics.enrollment.undergraduate", undergraduate, confidence=0.94, source="table", source_ref="B1 undergraduate degree-seeking tables")
    if graduate:
        _set_field(data, field_meta, "demographics.enrollment.graduate", graduate, confidence=0.9, source="table", source_ref="B1 graduate degree-seeking tables")
    if undergraduate or graduate:
        _set_field(data, field_meta, "demographics.enrollment.total", undergraduate + graduate, confidence=0.9, source="derived", status="derived", source_ref="B1 degree-seeking totals")

    race_table = None
    for table in _table_rows(raw_payload):
        rows = table.get("rows", [])
        if rows and "degree-seeking undergraduates" in _normalize_label(" ".join(rows[0])):
            race_table = table
            break
    if race_table:
        race_map = {
            "nonresidents": "international",
            "hispanic/latino": "hispanicLatino",
            "black or african american": "blackAfricanAmerican",
            "white, non-hispanic": "white",
            "american indian or alaska native": "americanIndianAlaskaNative",
            "asian, non-hispanic": "asian",
            "native hawaiian or other pacific islander": "nativeHawaiianPacificIslander",
            "two or more races": "twoOrMoreRaces",
            "race and/or ethnicity unknown": "unknown",
        }
        for row in race_table.get("rows", [])[1:]:
            label = _normalize_label(row[0] if row else "")
            for token, field_name in race_map.items():
                if token in label and len(row) >= 3:
                    value = parse_number(row[2])
                    if value is not None:
                        _set_field(data, field_meta, f"demographics.byRace.{field_name}", value, confidence=0.93, source="table", source_ref="B2 race table")
                    break

    scores_0 = None
    scores_1 = None
    for table in _table_rows(raw_payload):
        rows = table.get("rows", [])
        if rows and len(rows[0]) == 2 and parse_percent(rows[0][0]) is not None and parse_number(rows[0][1]) is not None:
            scores_0 = table
            break
    for table in _table_rows(raw_payload):
        rows = table.get("rows", [])
        if rows and "assessment" in _normalize_label(" ".join(rows[0])) and "25th percentile" in _normalize_label(" ".join(rows[0])):
            scores_1 = table
            break
    if scores_0 and len(scores_0.get("rows", [])) >= 2:
        sat_rate = parse_percent(scores_0["rows"][0][0])
        act_rate = parse_percent(scores_0["rows"][1][0])
        if sat_rate is not None:
            _set_field(data, field_meta, "testScores.sat.submissionRate", round(sat_rate, 4), confidence=0.9, source="table", source_ref="C9 submission table")
        if act_rate is not None:
            _set_field(data, field_meta, "testScores.act.submissionRate", round(act_rate, 4), confidence=0.9, source="table", source_ref="C9 submission table")
    if scores_1:
        sat = {}
        act = {}
        for row in scores_1.get("rows", [])[1:]:
            if not row:
                continue
            label = _normalize_label(row[0])
            values = [parse_number(cell) for cell in row[1:4]]
            if len(values) < 3 or any(value is None for value in values):
                continue
            if "sat composite" in label:
                sat["composite"] = {"p25": values[0], "p50": values[1], "p75": values[2]}
            elif "sat evidence-based" in label:
                sat["readingWriting"] = {"p25": values[0], "p50": values[1], "p75": values[2]}
            elif "sat math" in label:
                sat["math"] = {"p25": values[0], "p50": values[1], "p75": values[2]}
            elif "act composite" in label:
                act["composite"] = {"p25": values[0], "p50": values[1], "p75": values[2]}
        if sat:
            sat["submissionRate"] = _get_nested(data, "testScores.sat.submissionRate") or 0
            data["testScores"]["sat"] = sat
            field_meta["testScores.sat"] = FieldMeta(value=sat, confidence=0.92, status="confirmed", source="table", source_ref="C9 percentile table", notes=[]).to_dict()
        if act:
            act["submissionRate"] = _get_nested(data, "testScores.act.submissionRate") or 0
            data["testScores"]["act"] = act
            field_meta["testScores.act"] = FieldMeta(value=act, confidence=0.92, status="confirmed", source="table", source_ref="C9 percentile table", notes=[]).to_dict()

    costs_private = _find_table_by_header(raw_payload, "PRIVATE INSTITUTIONS")
    costs_all = None
    for table in _table_rows(raw_payload):
        rows = table.get("rows", [])
        if rows and "for all institutions" in _normalize_label(" ".join(rows[0:8][0])):
            costs_all = table
            break
        if rows and "required fees:" in _normalize_label(" ".join(sum(rows[:10], []))):
            costs_all = table
    if costs_private:
        tuition = _find_row_value(costs_private, "Tuition:")
        if tuition is not None:
            _set_field(data, field_meta, "costs.tuition", tuition, confidence=0.94, source="table", source_ref="G1 private tuition table")
    if costs_all:
        fees = _find_row_value(costs_all, "Required Fees:")
        room_and_board = _find_row_value(costs_all, "Food and housing")
        if fees is not None:
            _set_field(data, field_meta, "costs.fees", fees, confidence=0.94, source="table", source_ref="G1 fees table")
        if room_and_board is not None:
            _set_field(data, field_meta, "costs.roomAndBoard", room_and_board, confidence=0.94, source="table", source_ref="G1 food and housing table")

    aid_counts = None
    aid_averages = None
    for table in _table_rows(raw_payload):
        rows = table.get("rows", [])
        joined = _normalize_label(" ".join(sum(rows[:3], []))) if rows else ""
        if "number of enrolled students awarded aid" in joined:
            aid_counts = table
        if rows and rows[0] and rows[0][0] == "I":
            aid_averages = table
    f1_table = None
    for table in _table_rows(raw_payload):
        rows = table.get("rows", [])
        if rows:
            first_row = _normalize_label(" ".join(str(cell) for cell in rows[0] if cell))
            if "first-time" in first_row and "year students" in first_row and "undergraduates" in first_row:
                f1_table = table
                break
    if f1_table and undergraduate:
        out_pct = None
        for row in f1_table.get("rows", []):
            if row and "percent who are from out of state" in _normalize_label(row[0]):
                out_pct = parse_percent(row[1]) if len(row) > 1 else None
                break
        international = _get_nested(data, "demographics.byRace.international") or 0
        if out_pct is not None:
            domestic = max(undergraduate - international, 0)
            out_of_state = int(round(domestic * out_pct))
            in_state = max(domestic - out_of_state, 0)
            _set_field(data, field_meta, "demographics.byResidency.outOfState", out_of_state, confidence=0.86, source="table", source_ref="F1 out-of-state percentage")
            _set_field(data, field_meta, "demographics.byResidency.inState", in_state, confidence=0.86, source="derived", status="derived", source_ref="F1 domestic - out-of-state")

    if aid_counts:
        first_year_total = None
        aid_awarded = None
        for row in aid_counts.get("rows", [])[1:]:
            if not row:
                continue
            letter = row[0]
            if letter == "A":
                first_year_total = parse_number(row[2]) if len(row) > 2 else None
            elif letter == "D":
                aid_awarded = parse_number(row[2]) if len(row) > 2 else None
        if first_year_total and aid_awarded is not None:
            _set_field(data, field_meta, "financialAid.percentReceivingAid", round(aid_awarded / first_year_total, 4), confidence=0.9, source="table", source_ref="H2 D/A first-year")
    if aid_averages:
        for row in aid_averages.get("rows", []):
            if not row:
                continue
            label = row[0]
            if label == "I":
                value = parse_percent(row[2]) if len(row) > 2 else None
                if value is not None:
                    _set_field(data, field_meta, "financialAid.percentNeedFullyMet", round(value, 4), confidence=0.93, source="table", source_ref="H2 I first-year")
            if label == "J":
                value = parse_number(row[2]) if len(row) > 2 else None
                if value is not None:
                    _set_field(data, field_meta, "financialAid.averageAidPackage", value, confidence=0.93, source="table", source_ref="H2 J first-year")
            elif label == "K":
                value = parse_number(row[2]) if len(row) > 2 else None
                if value is not None:
                    _set_field(data, field_meta, "financialAid.averageNeedBasedGrant", value, confidence=0.93, source="table", source_ref="H2 K first-year")


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
    sat_match = SAT_SECTION_PATTERN.search(text) if "testScores.sat" not in field_meta and not data["testScores"].get("sat") else None
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

    act_match = ACT_SECTION_PATTERN.search(text) if "testScores.act" not in field_meta and not data["testScores"].get("act") else None
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
        if not all(key in sat for key in ["composite", "readingWriting", "math"]):
            data["testScores"].pop("sat", None)
            field_meta["testScores.sat"] = FieldMeta(
                value={},
                confidence=0.3,
                status="low_confidence",
                source="heuristic_guardrail",
                source_ref=field_meta.get("testScores.sat", {}).get("source_ref"),
                notes=["SAT block was incomplete, so it was suppressed."],
            ).to_dict()
            sat = None
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
        if "composite" not in act:
            data["testScores"].pop("act", None)
            field_meta["testScores.act"] = FieldMeta(
                value={},
                confidence=0.3,
                status="low_confidence",
                source="heuristic_guardrail",
                source_ref=field_meta.get("testScores.act", {}).get("source_ref"),
                notes=["ACT block was incomplete, so it was suppressed."],
            ).to_dict()
            act = None
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


def _vision_field_parser(path: str) -> Any:
    percent_fields = {
        "financialAid.percentReceivingAid",
        "financialAid.percentNeedFullyMet",
        "testScores.sat.submissionRate",
        "testScores.act.submissionRate",
        "computed.demographics.outOfStatePercent",
    }
    return parse_percent if path in percent_fields else parse_number


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
        _set_field(
            data,
            field_meta,
            path,
            round(float(parsed), 4) if parser is parse_percent else parsed,
            confidence=min(0.99, max(0.0, float(candidate.get("confidence", 0.0)))),
            source="vision_llm",
            source_ref=source_ref,
            notes=[],
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


def _cleanup_internal_fields(data: dict[str, Any], field_meta: dict[str, dict[str, Any]]) -> None:
    data.pop("computed", None)
    for path in [key for key in field_meta if key.startswith("computed.")]:
        field_meta.pop(path, None)


def normalize_document(raw_payload: dict[str, Any], config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    data = _empty_year_data()
    field_meta: dict[str, dict[str, Any]] = {}
    form_fields = raw_payload.get("form_fields", {})
    text = _collect_text(raw_payload)

    if config.get("school_slug") == "georgetown":
        _extract_georgetown_from_tables(raw_payload, data, field_meta)

    _apply_vision_candidates(raw_payload, data, field_meta)

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
        existing = field_meta.get(path)
        if existing and float(existing.get("confidence", 0)) >= 0.9:
            continue
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
        existing = field_meta.get(path)
        if existing and float(existing.get("confidence", 0)) >= 0.9:
            continue
        text_match = _find_text_value(text, _percent_patterns(config, path), parse_percent)
        if text_match:
            _set_field(data, field_meta, path, round(float(text_match[0]), 4), confidence=0.7, source="text_regex", source_ref=text_match[1])

    _derive_test_scores(data, text, field_meta)
    _derive_admissions(data, field_meta)
    _derive_costs(data, field_meta)
    _derive_enrollment(data, field_meta)
    _derive_residency_from_vision_percent(data, field_meta)
    _sanitize_document(data, field_meta)
    _derive_costs(data, field_meta)
    _derive_enrollment(data, field_meta)
    _cleanup_internal_fields(data, field_meta)

    return data, field_meta
