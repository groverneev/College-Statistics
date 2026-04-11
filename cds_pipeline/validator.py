from __future__ import annotations

from typing import Any


def _get_nested(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for key in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def validate_year_data(data: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []

    applied = _get_nested(data, "admissions.applied") or 0
    admitted = _get_nested(data, "admissions.admitted") or 0
    enrolled = _get_nested(data, "admissions.enrolled") or 0
    acceptance_rate = _get_nested(data, "admissions.acceptanceRate")
    yield_rate = _get_nested(data, "admissions.yield")

    if applied and admitted and acceptance_rate is not None:
        expected = round(admitted / applied, 4)
        if abs(expected - float(acceptance_rate)) > 0.002:
            issues.append(
                {
                    "kind": "admissions_acceptance_rate_mismatch",
                    "message": f"Expected acceptanceRate {expected}, found {acceptance_rate}.",
                }
            )

    if admitted and enrolled and yield_rate is not None:
        expected = round(enrolled / admitted, 4)
        if abs(expected - float(yield_rate)) > 0.002:
            issues.append(
                {
                    "kind": "admissions_yield_mismatch",
                    "message": f"Expected yield {expected}, found {yield_rate}.",
                }
            )

    undergraduate = _get_nested(data, "demographics.enrollment.undergraduate") or 0
    graduate = _get_nested(data, "demographics.enrollment.graduate") or 0
    total = _get_nested(data, "demographics.enrollment.total")
    if total is not None and (undergraduate or graduate):
        expected = undergraduate + graduate
        if int(total) != expected:
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
    total_coa = _get_nested(data, "costs.totalCOA")
    if total_coa is not None and (tuition or fees or room_and_board):
        expected = tuition + fees + room_and_board
        if int(total_coa) != expected:
            issues.append(
                {
                    "kind": "cost_total_mismatch",
                    "message": f"Expected totalCOA {expected}, found {total_coa}.",
                }
            )

    return {
        "issue_count": len(issues),
        "issues": issues,
    }


def validate_year_submission(payload: dict[str, Any]) -> dict[str, Any]:
    notes = payload.get("notes", [])
    data = payload.get("data", {})
    validation = validate_year_data(data if isinstance(data, dict) else {})
    return {
        "year": payload.get("year"),
        "issue_count": validation["issue_count"],
        "issues": validation["issues"],
        "notes": notes if isinstance(notes, list) else [],
    }


def validate_school_data(payload: dict[str, Any]) -> dict[str, Any]:
    years = payload.get("years", {})
    if not isinstance(years, dict):
        raise ValueError("School payload must contain a years object.")

    per_year = []
    total_issues = 0
    for year in sorted(years):
        validation = validate_year_data(years[year] if isinstance(years[year], dict) else {})
        total_issues += validation["issue_count"]
        per_year.append(
            {
                "year": year,
                "issue_count": validation["issue_count"],
                "issues": validation["issues"],
            }
        )

    return {
        "school_name": payload.get("name"),
        "school_slug": payload.get("slug"),
        "issue_count": total_issues,
        "years": per_year,
    }
