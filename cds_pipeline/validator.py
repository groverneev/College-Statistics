from __future__ import annotations

from typing import Any


CORE_FIELDS = [
    "admissions.applied",
    "admissions.admitted",
    "admissions.enrolled",
    "costs.tuition",
    "costs.fees",
    "costs.roomAndBoard",
]


def _get_nested(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for key in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def validate_document(data: dict[str, Any], field_meta: dict[str, dict[str, Any]]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    low_confidence_fields: list[dict[str, Any]] = []

    present = 0
    for path in CORE_FIELDS:
        value = _get_nested(data, path)
        if isinstance(value, (int, float)) and value:
            present += 1

    for path, meta in field_meta.items():
        if meta.get("confidence", 1) < 0.6 or meta.get("status") == "low_confidence":
            low_confidence_fields.append(
                {
                    "field": path,
                    "confidence": meta.get("confidence"),
                    "status": meta.get("status"),
                    "source": meta.get("source"),
                }
            )

    applied = _get_nested(data, "admissions.applied") or 0
    admitted = _get_nested(data, "admissions.admitted") or 0
    enrolled = _get_nested(data, "admissions.enrolled") or 0
    acceptance_rate = _get_nested(data, "admissions.acceptanceRate") or 0
    yield_rate = _get_nested(data, "admissions.yield") or 0

    if applied and admitted:
        expected = round(admitted / applied, 4)
        if abs(expected - acceptance_rate) > 0.002:
            issues.append(
                {
                    "kind": "admissions_acceptance_rate_mismatch",
                    "message": f"Expected acceptanceRate {expected}, found {acceptance_rate}.",
                }
            )
    if admitted and enrolled:
        expected = round(enrolled / admitted, 4)
        if abs(expected - yield_rate) > 0.002:
            issues.append(
                {
                    "kind": "admissions_yield_mismatch",
                    "message": f"Expected yield {expected}, found {yield_rate}.",
                }
            )

    undergraduate = _get_nested(data, "demographics.enrollment.undergraduate") or 0
    graduate = _get_nested(data, "demographics.enrollment.graduate") or 0
    total = _get_nested(data, "demographics.enrollment.total") or 0
    if undergraduate or graduate:
        expected = undergraduate + graduate
        if total != expected:
            issues.append(
                {
                    "kind": "enrollment_total_mismatch",
                    "message": f"Expected enrollment total {expected}, found {total}.",
                }
            )

    race_total = sum(
        [
            _get_nested(data, "demographics.byRace.international") or 0,
            _get_nested(data, "demographics.byRace.hispanicLatino") or 0,
            _get_nested(data, "demographics.byRace.blackAfricanAmerican") or 0,
            _get_nested(data, "demographics.byRace.white") or 0,
            _get_nested(data, "demographics.byRace.asian") or 0,
            _get_nested(data, "demographics.byRace.americanIndianAlaskaNative") or 0,
            _get_nested(data, "demographics.byRace.nativeHawaiianPacificIslander") or 0,
            _get_nested(data, "demographics.byRace.twoOrMoreRaces") or 0,
            _get_nested(data, "demographics.byRace.unknown") or 0,
        ]
    )
    if undergraduate and race_total and abs(race_total - undergraduate) > max(10, int(undergraduate * 0.02)):
        issues.append(
            {
                "kind": "race_total_mismatch",
                "message": f"Race total {race_total} does not reconcile to undergraduate enrollment {undergraduate}.",
            }
        )

    residency_total = sum(
        [
            _get_nested(data, "demographics.byResidency.inState") or 0,
            _get_nested(data, "demographics.byResidency.outOfState") or 0,
            _get_nested(data, "demographics.byResidency.international") or 0,
        ]
    )
    if undergraduate and residency_total and abs(residency_total - undergraduate) > max(10, int(undergraduate * 0.02)):
        issues.append(
            {
                "kind": "residency_total_mismatch",
                "message": f"Residency total {residency_total} does not reconcile to undergraduate enrollment {undergraduate}.",
            }
        )

    tuition = _get_nested(data, "costs.tuition") or 0
    fees = _get_nested(data, "costs.fees") or 0
    room_and_board = _get_nested(data, "costs.roomAndBoard") or 0
    total_coa = _get_nested(data, "costs.totalCOA") or 0
    if tuition or fees or room_and_board:
        expected = tuition + fees + room_and_board
        if total_coa != expected:
            issues.append(
                {
                    "kind": "cost_total_mismatch",
                    "message": f"Expected totalCOA {expected}, found {total_coa}.",
                }
            )

    return {
        "core_coverage": round(present / len(CORE_FIELDS), 3),
        "issue_count": len(issues),
        "issues": issues,
        "low_confidence_fields": low_confidence_fields,
    }
