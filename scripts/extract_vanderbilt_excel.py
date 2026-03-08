#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

import openpyxl
import xlrd


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value)).strip().lower()


def parse_number(value: Any) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return value

    text = str(value).strip()
    if not text:
        return None

    lowered = text.lower()
    if lowered in {"n/a", "na", "not applicable", "varies"}:
        return None

    cleaned = (
        text.replace("$", "")
        .replace(",", "")
        .replace("%", "")
        .replace("\u2212", "-")
        .strip()
    )
    if not cleaned:
        return None

    try:
        if re.fullmatch(r"-?\d+", cleaned):
            return int(cleaned)
        return float(cleaned)
    except ValueError:
        return None


def parse_rate(value: Any) -> float:
    number = parse_number(value)
    if number is None:
        return 0.0
    rate = float(number)
    return rate / 100 if rate > 1 else rate


def row_numbers(row: list[Any]) -> list[float | int]:
    numbers: list[float | int] = []
    for cell in row:
        number = parse_number(cell)
        if number is not None:
            numbers.append(number)
    return numbers


def midpoint(p25: int, p75: int) -> int:
    return int(round((p25 + p75) / 2))


def compact_row(values: list[Any]) -> list[Any]:
    compacted: list[Any] = []
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                continue
            compacted.append(stripped)
        else:
            compacted.append(value)
    return compacted


def read_xlsx_rows(path: Path, sheet_name: str) -> list[list[Any]]:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = workbook[sheet_name]
    finally:
        pass

    rows = [compact_row(list(row)) for row in sheet.iter_rows(values_only=True)]
    workbook.close()
    return rows


def read_xls_rows(path: Path, sheet_name: str) -> list[list[Any]]:
    workbook = xlrd.open_workbook(path)
    sheet_map = {normalize_text(name): name for name in workbook.sheet_names()}
    actual_name = sheet_map.get(normalize_text(sheet_name))
    if actual_name is None:
        raise ValueError(f"Sheet {sheet_name!r} not found in {path.name}")
    sheet = workbook.sheet_by_name(actual_name)

    rows: list[list[Any]] = []
    for row_idx in range(sheet.nrows):
        rows.append(compact_row(sheet.row_values(row_idx)))
    return rows


def read_rows(path: Path, sheet_name: str) -> list[list[Any]]:
    if path.suffix.lower() == ".xlsx":
        return read_xlsx_rows(path, sheet_name)
    if path.suffix.lower() == ".xls":
        return read_xls_rows(path, sheet_name)
    raise ValueError(f"Unsupported workbook type: {path.suffix}")


def find_row(rows: list[list[Any]], *needles: str) -> list[Any]:
    normalized_needles = [normalize_text(needle) for needle in needles]
    for row in rows:
        haystack = normalize_text(" | ".join(str(cell) for cell in row))
        if all(needle in haystack for needle in normalized_needles):
            return row
    raise ValueError(f"Could not find row containing: {needles}")


def find_optional_row(rows: list[list[Any]], *needles: str) -> list[Any] | None:
    try:
        return find_row(rows, *needles)
    except ValueError:
        return None


def find_numeric_row(rows: list[list[Any]], *needles: str) -> list[Any]:
    normalized_needles = [normalize_text(needle) for needle in needles]
    for row in rows:
        haystack = normalize_text(" | ".join(str(cell) for cell in row))
        if all(needle in haystack for needle in normalized_needles) and row_numbers(row):
            return row
    raise ValueError(f"Could not find numeric row containing: {needles}")


def find_optional_numeric_row(rows: list[list[Any]], *needles: str) -> list[Any] | None:
    try:
        return find_numeric_row(rows, *needles)
    except ValueError:
        return None


def extract_last_int(row: list[Any]) -> int:
    numbers = row_numbers(row)
    if not numbers:
        raise ValueError(f"No numeric values found in row: {row}")
    return int(round(float(numbers[-1])))


def extract_admissions(rows: list[list[Any]]) -> dict[str, Any]:
    aggregate_applied = find_optional_numeric_row(rows, "total first-time, first-year students", "applied")
    aggregate_admitted = find_optional_numeric_row(rows, "total first-time, first-year students", "admitted")
    aggregate_enrolled = find_optional_numeric_row(rows, "total first-time, first-year students", "enrolled")

    if aggregate_applied and aggregate_admitted and aggregate_enrolled:
        applied = sum(int(round(float(value))) for value in row_numbers(aggregate_applied))
        admitted = sum(int(round(float(value))) for value in row_numbers(aggregate_admitted))
        enrolled = sum(int(round(float(value))) for value in row_numbers(aggregate_enrolled))
    else:
        applied = sum(
            extract_last_int(find_numeric_row(rows, "total", label, "applied"))
            for label in ("men", "women")
        )
        admitted = sum(
            extract_last_int(find_numeric_row(rows, "total", label, "admitted"))
            for label in ("men", "women")
        )

        unknown_applied = find_optional_numeric_row(rows, "total", "unknown gender", "applied")
        if unknown_applied is not None:
            applied += extract_last_int(unknown_applied)

        unknown_admitted = find_optional_numeric_row(rows, "total", "unknown gender", "admitted")
        if unknown_admitted is not None:
            admitted += extract_last_int(unknown_admitted)

        enrolled = 0
        for labels in [
            ("total", "enrolled", "full-time", "men"),
            ("total", "enrolled", "part-time", "men"),
            ("total", "enrolled", "full-time", "women"),
            ("total", "enrolled", "part-time", "women"),
            ("total", "enrolled", "full-time", "unknown gender"),
            ("total", "enrolled", "part-time", "unknown gender"),
            ("total", "enrolled", "full-time", "another gender"),
            ("total", "enrolled", "part-time", "another gender"),
        ]:
            row = find_optional_numeric_row(rows, *labels)
            if row is not None and row_numbers(row):
                enrolled += extract_last_int(row)

    data: dict[str, Any] = {
        "applied": applied,
        "admitted": admitted,
        "enrolled": enrolled,
        "acceptanceRate": round(admitted / applied, 4),
        "yield": round(enrolled / admitted, 4),
    }

    early_applied = find_optional_numeric_row(rows, "number of early decision applications received")
    early_admitted = find_optional_numeric_row(rows, "admitted under early decision")
    if early_applied is not None and early_admitted is not None:
        data["earlyDecision"] = {
            "applied": extract_last_int(early_applied),
            "admitted": extract_last_int(early_admitted),
        }

    return data


def extract_test_scores(rows: list[list[Any]]) -> dict[str, Any]:
    sat_submission_row = find_optional_row(rows, "submitting sat scores") or find_optional_row(rows, "percent submitting sat scores")
    act_submission_row = find_optional_row(rows, "submitting act scores") or find_optional_row(rows, "percent submitting act scores")

    sat_rw_row = find_optional_row(rows, "sat evidence-based reading and writing") or find_optional_row(rows, "sat critical reading")
    sat_math_row = find_row(rows, "sat math")
    sat_composite_row = find_optional_row(rows, "sat composite")
    act_composite_row = find_row(rows, "act composite")

    if sat_rw_row is None:
        raise ValueError("Missing SAT reading/writing row")

    sat_rw_numbers = [int(round(float(value))) for value in row_numbers(sat_rw_row)]
    sat_math_numbers = [int(round(float(value))) for value in row_numbers(sat_math_row)]
    act_numbers = [int(round(float(value))) for value in row_numbers(act_composite_row)]
    sat_composite_numbers = [int(round(float(value))) for value in row_numbers(sat_composite_row or [])]

    if len(sat_composite_numbers) >= 3:
        sat_comp_p25, sat_comp_p50, sat_comp_p75 = sat_composite_numbers[-3:]
    else:
        sat_comp_p25 = sat_rw_numbers[-2] + sat_math_numbers[-2]
        sat_comp_p75 = sat_rw_numbers[-1] + sat_math_numbers[-1]
        sat_comp_p50 = midpoint(sat_comp_p25, sat_comp_p75)

    if len(sat_rw_numbers) >= 3:
        sat_rw_p25, sat_rw_p50, sat_rw_p75 = sat_rw_numbers[-3:]
    else:
        sat_rw_p25, sat_rw_p75 = sat_rw_numbers[-2:]
        sat_rw_p50 = midpoint(sat_rw_p25, sat_rw_p75)

    if len(sat_math_numbers) >= 3:
        sat_math_p25, sat_math_p50, sat_math_p75 = sat_math_numbers[-3:]
    else:
        sat_math_p25, sat_math_p75 = sat_math_numbers[-2:]
        sat_math_p50 = midpoint(sat_math_p25, sat_math_p75)

    if len(act_numbers) >= 3:
        act_p25, act_p50, act_p75 = act_numbers[-3:]
    else:
        act_p25, act_p75 = act_numbers[-2:]
        act_p50 = midpoint(act_p25, act_p75)

    sat_submission_rate = parse_rate(row_numbers(sat_submission_row)[0]) if sat_submission_row else 0.0
    act_submission_rate = parse_rate(row_numbers(act_submission_row)[0]) if act_submission_row else 0.0

    return {
        "sat": {
            "composite": {"p25": sat_comp_p25, "p50": sat_comp_p50, "p75": sat_comp_p75},
            "readingWriting": {"p25": sat_rw_p25, "p50": sat_rw_p50, "p75": sat_rw_p75},
            "math": {"p25": sat_math_p25, "p50": sat_math_p50, "p75": sat_math_p75},
            "submissionRate": round(sat_submission_rate, 4),
        },
        "act": {
            "composite": {"p25": act_p25, "p50": act_p50, "p75": act_p75},
            "submissionRate": round(act_submission_rate, 4),
        },
    }


def extract_demographics(b_rows: list[list[Any]], f_rows: list[list[Any]]) -> dict[str, Any]:
    undergraduate_row = find_optional_numeric_row(b_rows, "total all undergraduates") or find_optional_numeric_row(b_rows, "total of all undergraduate students enrolled") or find_numeric_row(b_rows, "total undergraduate students")
    graduate_row = find_optional_numeric_row(b_rows, "total all graduate") or find_optional_numeric_row(b_rows, "total of all graduate students enrolled") or find_numeric_row(b_rows, "total graduate students")
    total_row = find_optional_numeric_row(b_rows, "grand total all students")

    undergraduate = extract_last_int(undergraduate_row)
    graduate = extract_last_int(graduate_row)
    total = extract_last_int(total_row) if total_row is not None else undergraduate + graduate

    by_race = {
        "international": extract_last_int(find_optional_numeric_row(b_rows, "nonresident aliens") or find_numeric_row(b_rows, "nonresidents")),
        "hispanicLatino": extract_last_int(find_numeric_row(b_rows, "hispanic/latino")),
        "blackAfricanAmerican": extract_last_int(find_numeric_row(b_rows, "black or african american, non-hispanic")),
        "white": extract_last_int(find_numeric_row(b_rows, "white, non-hispanic")),
        "asian": extract_last_int(find_numeric_row(b_rows, "asian, non-hispanic")),
        "americanIndianAlaskaNative": extract_last_int(find_numeric_row(b_rows, "american indian or alaska native, non-hispanic")),
        "nativeHawaiianPacificIslander": extract_last_int(find_numeric_row(b_rows, "native hawaiian or other pacific islander, non-hispanic")),
        "twoOrMoreRaces": extract_last_int(find_numeric_row(b_rows, "two or more races, non-hispanic")),
        "unknown": extract_last_int(find_numeric_row(b_rows, "race and/or ethnicity unknown")),
    }

    out_of_state_pct = parse_rate(row_numbers(find_row(f_rows, "percent who are from out of state"))[-1])
    domestic = undergraduate - by_race["international"]
    out_of_state = int(math.floor(domestic * out_of_state_pct + 0.5))
    in_state = domestic - out_of_state

    return {
        "enrollment": {
            "total": total,
            "undergraduate": undergraduate,
            "graduate": graduate,
        },
        "byRace": by_race,
        "byResidency": {
            "inState": in_state,
            "outOfState": out_of_state,
            "international": by_race["international"],
        },
    }


def extract_costs(rows: list[list[Any]]) -> dict[str, int]:
    tuition = extract_last_int(find_numeric_row(rows, "tuition:"))
    fees = extract_last_int(find_numeric_row(rows, "required fees"))
    room_board_row = find_optional_numeric_row(rows, "food and housing") or find_optional_numeric_row(rows, "room and board")
    if room_board_row is None:
        raise ValueError("Missing room and board row")
    room_and_board = extract_last_int(room_board_row)

    return {
        "tuition": tuition,
        "fees": fees,
        "roomAndBoard": room_and_board,
        "totalCOA": tuition + fees + room_and_board,
    }


def extract_financial_aid(rows: list[list[Any]]) -> dict[str, Any]:
    total_students = extract_last_int(find_numeric_row(rows, "number of degree-seeking undergraduate students"))
    awarded_aid = extract_last_int(find_numeric_row(rows, "awarded any financial aid"))
    fully_met_rate = parse_rate(find_numeric_row(rows, "percentage of need that was met")[-1])
    avg_package = extract_last_int(find_numeric_row(rows, "average financial aid package"))
    avg_grant = extract_last_int(find_optional_numeric_row(rows, "average need-based scholarship and grant award") or find_numeric_row(rows, "average need-based scholarship or grant award"))

    return {
        "percentReceivingAid": round(awarded_aid / total_students, 4),
        "averageAidPackage": avg_package,
        "averageNeedBasedGrant": avg_grant,
        "percentNeedFullyMet": round(fully_met_rate, 4),
    }


def extract_year_data(workbook_path: Path) -> dict[str, Any]:
    admissions_rows = read_rows(workbook_path, "CDS-C")
    demographics_rows = read_rows(workbook_path, "CDS-B")
    student_life_rows = read_rows(workbook_path, "CDS-F")
    costs_rows = read_rows(workbook_path, "CDS-G")
    aid_rows = read_rows(workbook_path, "CDS-H")

    year_data = {
        "admissions": extract_admissions(admissions_rows),
        "testScores": extract_test_scores(admissions_rows),
        "demographics": extract_demographics(demographics_rows, student_life_rows),
        "costs": extract_costs(costs_rows),
        "financialAid": extract_financial_aid(aid_rows),
    }

    undergrad = year_data["demographics"]["enrollment"]["undergraduate"]
    race_total = sum(year_data["demographics"]["byRace"].values())
    residency_total = sum(year_data["demographics"]["byResidency"].values())
    if race_total != undergrad:
        raise ValueError(f"{workbook_path.name}: race total {race_total} does not match undergrad {undergrad}")
    if residency_total != undergrad:
        raise ValueError(f"{workbook_path.name}: residency total {residency_total} does not match undergrad {undergrad}")

    return year_data


def workbook_year_label(path: Path) -> str:
    match = re.search(r"(20\d{2})[-_](20\d{2})", path.stem)
    if not match:
        raise ValueError(f"Could not determine year from filename: {path.name}")
    return f"{match.group(1)}-{match.group(2)}"


def build_dataset(input_dir: Path) -> dict[str, Any]:
    years: dict[str, Any] = {}
    for workbook_path in sorted(input_dir.iterdir()):
        if workbook_path.suffix.lower() not in {".xls", ".xlsx"}:
            continue
        years[workbook_year_label(workbook_path)] = extract_year_data(workbook_path)

    return {
        "name": "Vanderbilt University",
        "slug": "vanderbilt",
        "years": years,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Vanderbilt CDS data from Excel workbooks.")
    parser.add_argument("--input-dir", type=Path, default=Path("College-Data/Vanderbilt"))
    parser.add_argument("--output", type=Path, default=Path("src/data/schools/vanderbilt.json"))
    args = parser.parse_args()

    dataset = build_dataset(args.input_dir)
    args.output.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
