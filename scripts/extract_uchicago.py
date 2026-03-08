#!/usr/bin/env python3
"""
Extract UChicago CDS data from the local PDF archive.

UChicago's CDS formatting differs enough from the generic extractor that a
school-specific parser is more reliable. The official archive currently starts
with 2021-2022, so this script only emits those official CDS years.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

import pdfplumber


PDF_DIR = Path("College-Data/UChicago")
OUTPUT_PATH = Path("src/data/schools/uchicago.json")

PDF_FILES = {
    "2021-2022": PDF_DIR / "UChicago_CDS_2021-22.pdf",
    "2022-2023": PDF_DIR / "UChicago_CDS_2022-23.pdf",
    "2023-2024": PDF_DIR / "UChicago_CDS_2023-24.pdf",
    "2024-2025": PDF_DIR / "CDS_2024-2025_to_publish.pdf",
}


def parse_int(value: str) -> int:
    match = re.search(r"\d[\d,]*", value or "")
    return int(match.group(0).replace(",", "")) if match else 0


def parse_percent(value: str) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)", value or "")
    return float(match.group(1)) / 100 if match else 0.0


def load_lines(pdf_path: Path) -> list[str]:
    with pdfplumber.open(str(pdf_path)) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return [line.strip() for line in text.splitlines() if line.strip()]


def find_line(lines: list[str], needle: str) -> tuple[int, str]:
    needle = needle.lower()
    for index, line in enumerate(lines):
        if needle in line.lower():
            return index, line
    raise ValueError(f"Missing line containing: {needle}")


def find_first_line(lines: list[str], needles: Iterable[str]) -> tuple[int, str]:
    for needle in needles:
        try:
            return find_line(lines, needle)
        except ValueError:
            continue
    raise ValueError(f"Missing line containing any of: {', '.join(needles)}")


def numbers_in_line(line: str) -> list[int]:
    return [int(num.replace(",", "")) for num in re.findall(r"\d[\d,]*", line)]


def slice_section(lines: list[str], start_needle: str, end_needles: Iterable[str]) -> list[str]:
    start_index, _ = find_line(lines, start_needle)
    end_index = len(lines)
    lowered_end_needles = [needle.lower() for needle in end_needles]
    for index, line in enumerate(lines[start_index + 1 :], start=start_index + 1):
        if any(needle in line.lower() for needle in lowered_end_needles):
            end_index = index
            break
    return lines[start_index:end_index]


def extract_b2_value(lines: list[str], label: str) -> int:
    lowered = label.lower()
    for index, line in enumerate(lines):
        if lowered in line.lower():
            nums = numbers_in_line(line)
            if len(nums) >= 3:
                return nums[-1]
            if index + 1 < len(lines):
                candidate = f"{line} {lines[index + 1]}"
                nums = numbers_in_line(candidate)
                if len(nums) >= 3:
                    return nums[-1]
    raise ValueError(f"Missing B2 values for {label}")


def extract_out_of_state_percent(lines: list[str]) -> float:
    index, line = find_line(lines, "Percent who are from out of state")
    nums = numbers_in_line(line)
    if len(nums) >= 2:
        return nums[-1] / 100
    if index + 1 < len(lines):
        nums = numbers_in_line(lines[index + 1])
        if nums:
            return nums[-1] / 100
    raise ValueError("Missing out-of-state percentage")


def sum_matching(lines: list[str], patterns: Iterable[str]) -> int:
    total = 0
    matched = False
    for pattern in patterns:
        for line in lines:
            if re.search(pattern, line, re.IGNORECASE):
                nums = numbers_in_line(line)
                if nums:
                    total += nums[-1]
                    matched = True
    if not matched:
        return 0
    return total


def first_matching_value(lines: list[str], patterns: Iterable[str], use: str = "last") -> int:
    for pattern in patterns:
        for line in lines:
            if re.search(pattern, line, re.IGNORECASE):
                nums = numbers_in_line(line)
                if nums:
                    return nums[0] if use == "first" else nums[-1]
    return 0


def extract_admissions(lines: list[str]) -> dict:
    applied = first_matching_value(
        lines,
        [
            r"Total first-time, first-year \(degree-seeking\) who applied",
        ],
    )
    admitted = first_matching_value(
        lines,
        [
            r"Total first-time, first-year \(degree-seeking\) who were admitted",
        ],
    )
    enrolled = first_matching_value(
        lines,
        [
            r"Total first-time, first-year \(degree-seeking\) who enrolled",
        ],
    )

    if not applied:
        applied = sum_matching(
            lines,
            [
                r"Total first-time, first-year men who applied",
                r"Total first-time, first-year women who applied",
                r"Total first-time, first-year another gender who applied",
                r"Total first-time, first-year unknown gender who applied",
                r"Non-binary",
            ],
        )
    if not admitted:
        admitted = sum_matching(
            lines,
            [
                r"Total first-time, first-year men who were admitted",
                r"Total first-time, first-year women who were admitted",
                r"Total first-time, first-year another gender who were admitted",
                r"Total first-time, first-year unknown gender who were admitted",
            ],
        )
    if not enrolled:
        enrolled = sum_matching(
            lines,
            [
                r"Total full-time, first-time, first-year.* men who enrolled",
                r"Total part-time, first-time, first-year.* men who enrolled",
                r"Total full-time, first-time, first-year.* women who enrolled",
                r"Total part-time, first-time, first-year.* women who enrolled",
                r"Total full-time, first-time, first-year.* another gender who enrolled",
                r"Total part-time, first-time, first-year.* another gender who enrolled",
                r"Total full-time, first-time, first-year.* unknown gender who enrolled",
                r"Total part-time, first-time, first-year.* unknown gender who enrolled",
            ],
        )

    men_applied = first_matching_value(lines, [r"Total first-time, first-year men who applied"])
    women_applied = first_matching_value(lines, [r"Total first-time, first-year women who applied"])
    men_admitted = first_matching_value(lines, [r"Total first-time, first-year men who were admitted"])
    women_admitted = first_matching_value(lines, [r"Total first-time, first-year women who were admitted"])
    men_enrolled = sum_matching(
        lines,
        [
            r"Total full-time, first-time, first-year.* men who enrolled",
            r"Total part-time, first-time, first-year.* men who enrolled",
        ],
    )
    women_enrolled = sum_matching(
        lines,
        [
            r"Total full-time, first-time, first-year.* women who enrolled",
            r"Total part-time, first-time, first-year.* women who enrolled",
        ],
    )

    data = {
        "applied": applied,
        "admitted": admitted,
        "enrolled": enrolled,
        "acceptanceRate": round(admitted / applied, 4) if applied else 0,
        "yield": round(enrolled / admitted, 4) if admitted else 0,
    }

    if men_applied and women_applied:
        data["byGender"] = {
            "men": {
                "applied": men_applied,
                "admitted": men_admitted,
                "enrolled": men_enrolled,
            },
            "women": {
                "applied": women_applied,
                "admitted": women_admitted,
                "enrolled": women_enrolled,
            },
        }

    return data


def extract_test_scores(lines: list[str], year: str) -> dict:
    _, sat_submission_line = find_line(lines, "Submitting SAT Scores")
    _, act_submission_line = find_line(lines, "Submitting ACT Scores")
    sat_submission_rate = parse_percent(sat_submission_line)
    act_submission_rate = parse_percent(act_submission_line)

    _, sat_line = find_line(lines, "SAT Composite")
    sat_composite = numbers_in_line(sat_line)

    erw_idx, erw_line = find_first_line(
        lines,
        [
            "SAT Evidence-Based Reading and Writing",
            "SAT Evidence-Based Reading",
            "Writing",
        ],
    )
    sat_erw = numbers_in_line(erw_line)
    if not sat_erw and erw_idx + 1 < len(lines):
        sat_erw = numbers_in_line(lines[erw_idx + 1])

    _, math_line = find_line(lines, "SAT Math")
    sat_math = numbers_in_line(math_line)

    _, act_line = find_line(lines, "ACT Composite")
    act = numbers_in_line(act_line)

    data: dict = {}

    # 2021-2022 only reports 25th/75th percentiles in the official CDS. Avoid
    # inventing medians just to satisfy the chart schema.
    if year != "2021-2022" and len(sat_composite) >= 3 and len(sat_erw) >= 3 and len(sat_math) >= 3:
        data["sat"] = {
            "composite": {"p25": sat_composite[0], "p50": sat_composite[1], "p75": sat_composite[2]},
            "readingWriting": {"p25": sat_erw[0], "p50": sat_erw[1], "p75": sat_erw[2]},
            "math": {"p25": sat_math[0], "p50": sat_math[1], "p75": sat_math[2]},
            "submissionRate": sat_submission_rate,
        }

    if year != "2021-2022" and len(act) >= 3:
        data["act"] = {
            "composite": {"p25": act[0], "p50": act[1], "p75": act[2]},
            "submissionRate": act_submission_rate,
        }

    return data


def extract_demographics(lines: list[str]) -> dict:
    undergraduate = first_matching_value(lines, [r"Total all undergraduates"])
    graduate = first_matching_value(lines, [r"Total all graduate"])
    total = first_matching_value(lines, [r"GRAND TOTAL ALL STUDENTS"])
    b2_lines = slice_section(lines, "B2 Enrollment by Racial/Ethnic Category", ["Persistence", "B3 Number of degrees awarded"])

    by_race = {
        "international": extract_b2_value(b2_lines, "Nonresident"),
        "hispanicLatino": extract_b2_value(b2_lines, "Hispanic/Latino"),
        "blackAfricanAmerican": extract_b2_value(b2_lines, "Black or African American"),
        "white": extract_b2_value(b2_lines, "White, non-Hispanic"),
        "asian": extract_b2_value(b2_lines, "Asian, non-Hispanic"),
        "americanIndianAlaskaNative": extract_b2_value(b2_lines, "American Indian or Alaska Native"),
        "nativeHawaiianPacificIslander": extract_b2_value(b2_lines, "Native Hawaiian or other Pacific Islander"),
        "twoOrMoreRaces": extract_b2_value(b2_lines, "Two or more races"),
        "unknown": extract_b2_value(b2_lines, "Race and/or ethnicity unknown"),
    }

    out_pct = extract_out_of_state_percent(lines)
    domestic = undergraduate - by_race["international"]
    out_of_state = round(domestic * out_pct)
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


def extract_costs(lines: list[str]) -> dict:
    g1_start, _ = find_first_line(
        lines,
        [
            "G1 Undergraduate full-time tuition, required fees, food and housing",
            "G1 Undergraduate full-time tuition, required fees, room and board",
            "G1 Undergraduate full-time tuition, fees, room and board",
        ],
    )
    g1_lines = slice_section(lines[g1_start:], lines[g1_start], ["G2", "CDS-H Page", "H. FINANCIAL AID"])
    tuition = first_matching_value(g1_lines, [r"^Tuition:"], use="first")
    fees = first_matching_value(g1_lines, [r"^Required Fees"], use="first")
    room_and_board = first_matching_value(g1_lines, [r"^Room and Board", r"^Food and housing"], use="first")
    return {
        "tuition": tuition,
        "fees": fees,
        "roomAndBoard": room_and_board,
        "totalCOA": tuition + fees + room_and_board,
    }


def extract_h2_values(lines: list[str]) -> dict[str, int | float]:
    start_index, _ = find_line(lines, "Number of Enrolled Students Awarded Aid")
    line_map: dict[str, int] = {}
    for index, line in enumerate(lines[start_index:], start=start_index):
        if re.match(r"^[A-Z]\s", line) and line[0] not in line_map:
            line_map[line[0]] = index

    def values_for(letter: str) -> list[int]:
        index = line_map[letter]
        nums = numbers_in_line(lines[index])
        filtered = [num for num in nums if num >= 10]
        if len(filtered) >= 2:
            return filtered[-2:]
        for offset in range(1, 4):
            if index + offset < len(lines):
                nums = numbers_in_line(lines[index + offset])
                filtered = [num for num in nums if num >= 10]
                if len(filtered) >= 2:
                    return filtered[-2:]
        raise ValueError(f"Missing H2 values for line {letter}")

    a = values_for("A")[-1]
    d = values_for("D")[-1]
    h = values_for("H")[-1]
    j = values_for("J")[-1]
    k = values_for("K")[-1]

    return {
        "percentReceivingAid": round(d / a, 4) if a else 0,
        "averageAidPackage": j,
        "averageNeedBasedGrant": k,
        "percentNeedFullyMet": round(h / d, 4) if d else 0,
    }


def extract_year(year: str, pdf_path: Path) -> dict:
    lines = load_lines(pdf_path)
    year_data = {
        "admissions": extract_admissions(lines),
        "testScores": extract_test_scores(lines, year),
        "demographics": extract_demographics(lines),
        "costs": extract_costs(lines),
        "financialAid": extract_h2_values(lines),
    }
    return year_data


def main() -> None:
    school_data = {
        "name": "University of Chicago",
        "slug": "uchicago",
        "years": {year: extract_year(year, pdf_path) for year, pdf_path in PDF_FILES.items()},
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(school_data, indent=2) + "\n")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
