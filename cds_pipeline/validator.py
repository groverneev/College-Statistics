from __future__ import annotations

from typing import Any

from .models import SectionExtraction


def _get_nested(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for key in path.split("."):
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _issue(kind: str, message: str, severity: str = "error") -> dict[str, str]:
    return {"kind": kind, "severity": severity, "message": message}


def validate_year_data(data: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    applied = _get_nested(data, "admissions.applied")
    admitted = _get_nested(data, "admissions.admitted")
    enrolled = _get_nested(data, "admissions.enrolled")
    if all(isinstance(value, (int, float)) for value in (applied, admitted, enrolled)):
        if not applied >= admitted >= enrolled >= 0:
            issues.append(_issue("admissions_order", "Expected applied >= admitted >= enrolled >= 0."))
        acceptance_rate = _get_nested(data, "admissions.acceptanceRate")
        if acceptance_rate is not None and applied:
            expected = round(admitted / applied, 4)
            if abs(expected - float(acceptance_rate)) > 0.002:
                issues.append(
                    _issue(
                        "admissions_acceptance_rate_mismatch",
                        f"Expected acceptanceRate {expected}, found {acceptance_rate}.",
                    )
                )
        yield_rate = _get_nested(data, "admissions.yield")
        if yield_rate is not None and admitted:
            expected = round(enrolled / admitted, 4)
            if abs(expected - float(yield_rate)) > 0.002:
                issues.append(
                    _issue("admissions_yield_mismatch", f"Expected yield {expected}, found {yield_rate}.")
                )

    for path in (
        "admissions.acceptanceRate",
        "admissions.yield",
        "testScores.sat.submissionRate",
        "testScores.act.submissionRate",
        "financialAid.percentReceivingAid",
        "financialAid.percentNeedFullyMet",
    ):
        value = _get_nested(data, path)
        if isinstance(value, (int, float)) and not 0 <= value <= 1:
            issues.append(_issue("rate_out_of_range", f"{path} must be between 0 and 1, found {value}."))

    undergraduate = _get_nested(data, "demographics.enrollment.undergraduate")
    graduate = _get_nested(data, "demographics.enrollment.graduate")
    total = _get_nested(data, "demographics.enrollment.total")
    if isinstance(total, (int, float)) and isinstance(undergraduate, (int, float)) and isinstance(graduate, (int, float)):
        if int(total) != int(undergraduate + graduate):
            issues.append(
                _issue(
                    "enrollment_total_mismatch",
                    f"Expected enrollment total {undergraduate + graduate}, found {total}.",
                    "warning",
                )
            )

    for test in ("sat", "act"):
        percentiles = _get_nested(data, f"testScores.{test}.composite")
        if isinstance(percentiles, dict) and all(key in percentiles for key in ("p25", "p75")):
            p25 = percentiles["p25"]
            p75 = percentiles["p75"]
            if not isinstance(p25, (int, float)) or isinstance(p25, bool) or not isinstance(
                p75, (int, float)
            ) or isinstance(p75, bool):
                issues.append(_issue(f"{test}_percentile_type", f"{test.upper()} percentiles must be numeric."))
                continue
            p50 = percentiles.get("p50")
            if p25 > p75 or (
                isinstance(p50, (int, float))
                and not isinstance(p50, bool)
                and not p25 <= p50 <= p75
            ):
                issues.append(_issue(f"{test}_percentile_order", f"{test.upper()} percentiles are not ordered."))
            lower, upper = (400, 1600) if test == "sat" else (1, 36)
            if not lower <= p25 <= upper or not lower <= p75 <= upper:
                issues.append(_issue(f"{test}_score_range", f"{test.upper()} composite scores are out of range."))

    race = _get_nested(data, "demographics.byRace")
    if isinstance(race, dict) and isinstance(undergraduate, (int, float)) and undergraduate > 0:
        race_values = [value for value in race.values() if isinstance(value, (int, float))]
        if any(value < 0 for value in race_values):
            issues.append(_issue("negative_race_count", "Race/ethnicity counts cannot be negative."))
        race_total = sum(race_values)
        if race_total > undergraduate * 1.02:
            issues.append(
                _issue(
                    "race_total_exceeds_undergraduate",
                    f"Race/ethnicity total {race_total} exceeds undergraduate enrollment {undergraduate}.",
                )
            )
        elif race_values and race_total < undergraduate * 0.5:
            issues.append(
                _issue(
                    "race_total_unusually_low",
                    f"Race/ethnicity total {race_total} is unusually low versus undergraduate enrollment {undergraduate}.",
                    "warning",
                )
            )

    residency = _get_nested(data, "demographics.byResidency")
    if isinstance(residency, dict) and isinstance(undergraduate, (int, float)) and undergraduate > 0:
        residency_values = [value for value in residency.values() if isinstance(value, (int, float))]
        if any(value < 0 for value in residency_values):
            issues.append(_issue("negative_residency_count", "Residency counts cannot be negative."))
        residency_total = sum(residency_values)
        if residency_total > undergraduate * 1.02:
            issues.append(
                _issue(
                    "residency_total_exceeds_undergraduate",
                    f"Residency total {residency_total} exceeds undergraduate enrollment {undergraduate}.",
                )
            )

    tuition = _get_nested(data, "costs.tuition")
    fees = _get_nested(data, "costs.fees")
    room_and_board = _get_nested(data, "costs.roomAndBoard")
    total_coa = _get_nested(data, "costs.totalCOA")
    if all(isinstance(value, (int, float)) for value in (tuition, fees, room_and_board, total_coa)):
        if any(value < 0 for value in (tuition, fees, room_and_board, total_coa)):
            issues.append(_issue("negative_cost", "Cost values cannot be negative."))
        expected = tuition + fees + room_and_board
        if abs(total_coa - expected) > 1:
            issues.append(
                _issue("cost_total_mismatch", f"Expected totalCOA {expected}, found {total_coa}.")
            )

    return _summarize(issues)


def validate_section_extraction(payload: dict[str, Any]) -> dict[str, Any]:
    extraction = SectionExtraction.model_validate(payload)
    issues: list[dict[str, str]] = []
    seen: set[str] = set()
    for observation in extraction.observations:
        if observation.path in seen:
            issues.append(_issue("duplicate_metric", f"Metric {observation.path} appears more than once."))
        seen.add(observation.path)
        if observation.value is not None and not observation.evidence:
            issues.append(_issue("missing_evidence", f"Metric {observation.path} has a value but no evidence."))
        if observation.value is not None:
            if observation.path.startswith("profile.admissionsFactors."):
                allowed = {"very_important", "important", "considered", "not_considered"}
                if not isinstance(observation.value, str) or observation.value not in allowed:
                    issues.append(_issue("invalid_factor_value", f"Metric {observation.path} has an invalid C7 value."))
            elif isinstance(observation.value, bool) or not isinstance(observation.value, (int, float)):
                issues.append(_issue("invalid_metric_type", f"Metric {observation.path} must be numeric."))
            elif observation.value < 0:
                issues.append(_issue("negative_metric", f"Metric {observation.path} cannot be negative."))
        if observation.value is not None and observation.confidence < 0.8:
            issues.append(_issue("low_confidence", f"Metric {observation.path} has confidence below 0.8."))
        if observation.review_required:
            issues.append(_issue("review_required", f"Metric {observation.path} requires review.", "warning"))
    return _summarize(issues)


def validate_school_data(payload: dict[str, Any]) -> dict[str, Any]:
    years = payload.get("years", {})
    if not isinstance(years, dict):
        raise ValueError("School payload must contain a years object.")
    per_year = []
    issues: list[dict[str, str]] = []
    for year in sorted(years):
        result = validate_year_data(years[year] if isinstance(years[year], dict) else {})
        per_year.append({"year": year, **result})
        issues.extend({**issue, "year": year} for issue in result["issues"])
    return {
        "school_name": payload.get("name"),
        "school_slug": payload.get("slug"),
        **_summarize(issues),
        "years": per_year,
    }


def validate_year_submission(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_year_data(payload.get("data", {}) if isinstance(payload.get("data"), dict) else {})
    return {"year": payload.get("year"), **result, "notes": payload.get("notes", [])}


def _summarize(issues: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "issue_count": len(issues),
        "error_count": sum(issue.get("severity") == "error" for issue in issues),
        "warning_count": sum(issue.get("severity") == "warning" for issue in issues),
        "issues": issues,
    }
