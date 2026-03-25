#!/usr/bin/env python3
"""
Build the UC San Diego dataset from official CDS PDFs.

UC San Diego's archive mixes older CDS layouts (2016-2021) with newer
2022+ templates. This extractor normalizes the fields displayed on the site
and writes `src/data/schools/ucsandiego.json`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber


YEAR_FILES = {
    "2016-2017": "ucsd20162017.pdf",
    "2017-2018": "UCSD_CDS_2017-2018.pdf",
    "2018-2019": "UCSD-CDS_2018-2019.pdf",
    "2019-2020": "UCSD_CDS_2019-2020.pdf",
    "2020-2021": "UCSD-2020-2021.pdf",
    "2022-2023": "UCSD-CDS_2022-20233.pdf",
    "2023-2024": "CDS_UCSD_2023_20242.pdf",
    "2024-2025": "CDS_2024-2025_Final1.pdf",
}


def squish(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_number(value: str) -> int:
    cleaned = value.replace("$", "").replace(",", "").strip()
    return int(round(float(cleaned)))


def parse_percent(value: str) -> float:
    return float(value.replace("%", "").strip()) / 100


def load_text(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def find_match(text: str, patterns: list[str], flags: int = re.IGNORECASE) -> re.Match[str] | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return match
    return None


def extract_admissions(text: str) -> dict:
    flat = squish(text)

    total_match = find_match(
        flat,
        [
            r"Total first-time, first-year \(degree seeking\) who applied\s+[\d,]+\s+[\d,]+\s+[\d,]+\s+([\d,]+).*?"
            r"Total first-time, first-year \(degree seeking\) who were admitted\s+[\d,]+\s+[\d,]+\s+[\d,]+\s+([\d,]+).*?"
            r"Total first-time, first-year \(degree seeking\) enrolled\s+[\d,]+\s+[\d,]+\s+[\d,]+\s+([\d,]+)",
            r"Total first-time, first-year students who applied in Fall \d{4}\s+[\d,]+\s+[\d,]+\s+[\d,]+\s+([\d,]+).*?"
            r"Total first-time, first-year students admitted in Fall \d{4}\s+[\d,]+\s+[\d,]+\s+[\d,]+\s+([\d,]+).*?"
            r"Total first-time, first-year students enrolled in Fall \d{4}\s+[\d,]+\s+[\d,]+\s+[\d,]+\s+([\d,]+)",
        ],
    )
    if total_match:
        applied, admitted, enrolled = (parse_number(group) for group in total_match.groups())
        return {
            "applied": applied,
            "admitted": admitted,
            "enrolled": enrolled,
            "acceptanceRate": round(admitted / applied, 4) if applied else 0,
            "yield": round(enrolled / admitted, 4) if admitted else 0,
        }

    applied = sum(
        parse_number(group)
        for group in find_match(
            flat,
            [
                r"Total first-time, first-year \(freshman\) men who applied\s+([\d,]+).*?"
                r"Total first-time, first-year \(freshman\) women who applied\s+([\d,]+)(?:.*?another gender who applied\s+([\d,]+))?",
                r"Total first-time, first-year men who applied\s+([\d,]+).*?"
                r"Total first-time, first-year women who applied\s+([\d,]+)(?:.*?another gender who applied\s+([\d,]+))?",
            ],
        ).groups(default="0")
    )
    admitted = sum(
        parse_number(group)
        for group in find_match(
            flat,
            [
                r"Total first-time, first-year \(freshman\) men who were admitted\s+([\d,]+).*?"
                r"Total first-time, first-year \(freshman\) women who were admitted\s+([\d,]+)(?:.*?another gender who were admitted\s+([\d,]+))?",
                r"Total first-time, first-year men who were admitted\s+([\d,]+).*?"
                r"Total first-time, first-year women who were admitted\s+([\d,]+)(?:.*?another gender who were admitted\s+([\d,]+))?",
            ],
        ).groups(default="0")
    )
    enrolled = sum(
        parse_number(group)
        for group in find_match(
            flat,
            [
                r"Total full-time, first-time, first-year \(freshman\) men who enrolled\s+([\d,]+).*?"
                r"Total part-time, first-time, first-year \(freshman\) men who enrolled\s+([\d,]+).*?"
                r"Total full-time, first-time, first-year \(freshman\) women who enrolled\s+([\d,]+).*?"
                r"Total part-time, first-time, first-year \(freshman\) women who enrolled\s+([\d,]+)",
                r"Total full-time, first-time, first-year men who enrolled\s+([\d,]+).*?"
                r"Total part-time, first-time, first-year men who enrolled\s+([\d,]+).*?"
                r"Total full-time, first-time, first-year women who enrolled\s+([\d,]+).*?"
                r"Total part-time, first-time, first-year women who enrolled\s+([\d,]+).*?"
                r"Total full-time, first-time, first-year another gender who enrolled\s+([\d,]+).*?"
                r"Total part-time, first-time, first-year another gender who enrolled\s+([\d,]+)",
            ],
        ).groups(default="0")
    )

    return {
        "applied": applied,
        "admitted": admitted,
        "enrolled": enrolled,
        "acceptanceRate": round(admitted / applied, 4) if applied else 0,
        "yield": round(enrolled / admitted, 4) if admitted else 0,
    }


def extract_test_scores(text: str) -> dict:
    flat = squish(text)

    sat_submit = find_match(flat, [r"(?:Percent )?submitting SAT scores\s+(\d+(?:\.\d+)?)%"])
    act_submit = find_match(flat, [r"(?:Percent )?submitting ACT scores\s+(\d+(?:\.\d+)?)%"])

    sat_rw = find_match(
        flat,
        [
            r"SAT Evidence-Based Reading and Writing\s+(\d{3})\s+(\d{3})",
            r"SAT Critical Reading\s+(\d{3})\s+(\d{3})",
        ],
    )
    sat_math = find_match(flat, [r"SAT Math\s+(\d{3})\s+(\d{3})"])
    sat_composite = find_match(flat, [r"SAT Composite(?: \(400 - 1600\))?\s+(\d{3,4})\s+(\d{3,4})"])
    act_composite = find_match(flat, [r"ACT Composite(?: \(0 - 36\))?\s+(\d{2})\s+(\d{2})"])

    data: dict = {}

    if sat_rw and sat_math:
        rw25, rw75 = map(int, sat_rw.groups())
        math25, math75 = map(int, sat_math.groups())
        if sat_composite:
            comp25, comp75 = map(int, sat_composite.groups())
        else:
            comp25 = rw25 + math25
            comp75 = rw75 + math75
        data["sat"] = {
            "composite": {"p25": comp25, "p50": (comp25 + comp75) // 2, "p75": comp75},
            "readingWriting": {"p25": rw25, "p50": (rw25 + rw75) // 2, "p75": rw75},
            "math": {"p25": math25, "p50": (math25 + math75) // 2, "p75": math75},
            "submissionRate": round(parse_percent(sat_submit.group(1)) if sat_submit else 0, 4),
        }

    if act_composite:
        act25, act75 = map(int, act_composite.groups())
        data["act"] = {
            "composite": {"p25": act25, "p50": (act25 + act75) // 2, "p75": act75},
            "submissionRate": round(parse_percent(act_submit.group(1)) if act_submit else 0, 4),
        }

    return data


def extract_enrollment(text: str) -> dict:
    flat = squish(text)
    undergrad_match = find_match(flat, [r"Total all undergraduates\s+([\d,]+)"])
    grad_match = find_match(flat, [r"Total all graduate\s+([\d,]+)"])
    if not undergrad_match or not grad_match:
        raise ValueError("Could not extract enrollment totals")

    undergraduate = parse_number(undergrad_match.group(1))
    graduate = parse_number(grad_match.group(1))

    return {
        "total": undergraduate + graduate,
        "undergraduate": undergraduate,
        "graduate": graduate,
    }


def extract_by_race(text: str) -> dict:
    flat = squish(text)
    patterns = {
        "international": [
            r"International \(nonresidents\)\s+[\d,]+\s+([\d,]+)\s+[\d,]+",
            r"Nonresidents\s+[\d,]+\s+([\d,]+)\s+[\d,]+",
            r"Nonresident aliens\s+[\d,]+\s+([\d,]+)\s+[\d,]+",
        ],
        "hispanicLatino": [r"Hispanic/Latino\s+[\d,]+\s+([\d,]+)\s+[\d,]+"],
        "blackAfricanAmerican": [r"Black or African American, non-Hispanic\s+[\d,]+\s+([\d,]+)\s+[\d,]+"],
        "white": [r"White, non-Hispanic\s+[\d,]+\s+([\d,]+)\s+[\d,]+"],
        "americanIndianAlaskaNative": [
            r"American Indian or Alaska Native, non-Hispanic\s+[\d,]+\s+([\d,]+)\s+[\d,]+",
            r"American Indian or Alaska Native, non-\s*Hispanic\s+[\d,]+\s+([\d,]+)\s+[\d,]+",
        ],
        "asian": [r"Asian, non-Hispanic\s+[\d,]+\s+([\d,]+)\s+[\d,]+"],
        "nativeHawaiianPacificIslander": [
            r"Native Hawaiian or other Pacific Islander, non-Hispanic\s+[\d,]+\s+([\d,]+)\s+[\d,]+",
            r"Native Hawaiian or other Pacific Islander, non-\s*Hispanic\s+[\d,]+\s+([\d,]+)\s+[\d,]+",
            r"Native Hawaiian or other Pacific Islander,\s+[\d,]+\s+([\d,]+)\s+[\d,]+\s+non-Hispanic",
            r"Native Hawaiian or other Pacific Islander, non-Hispa\s+[\d,]+\s+([\d,]+)\s+[\d,]+",
        ],
        "twoOrMoreRaces": [r"Two or more races, non-Hispanic\s+[\d,]+\s+([\d,]+)\s+[\d,]+"],
        "unknown": [r"Race and/or ethnicity unknown\s+[\d,]+\s+([\d,]+)\s+[\d,]+"],
    }

    result = {}
    for field, options in patterns.items():
        value = 0
        for pattern in options:
            match = re.search(pattern, flat, re.IGNORECASE)
            if match:
                value = parse_number(match.group(1))
                break
        result[field] = value
    return result


def extract_residency(text: str, undergraduate: int, international: int) -> dict:
    match = find_match(
        squish(text),
        [
            r"Percent who are from out of state .*?(\d+(?:\.\d+)?)%\s+(\d+(?:\.\d+)?)%",
        ],
    )
    out_pct = float(match.group(2)) if match else 0
    domestic = undergraduate - international
    out_of_state = round(domestic * out_pct / 100)
    in_state = domestic - out_of_state
    return {
        "inState": in_state,
        "outOfState": out_of_state,
        "international": international,
    }


def extract_costs(text: str) -> dict:
    flat = squish(text)
    tuition_match = find_match(
        flat,
        [
            r"Tuition: In-state \(out-of-district\): \$([\d,]+)",
            r"In-state \(out-of-district\): \$([\d,]+)",
            r"PUBLIC INSTITUTIONS \$([\d,]+) \$[\d,]+ In-state \(out-of-district\):",
        ],
    )
    fees_match = find_match(flat, [r"Required Fees:?\s+\$([\d,]+)", r"REQUIRED FEES:\s+\$([\d,]+)"])
    room_match = find_match(
        flat,
        [r"Food and [Hh]ousing \(on-campus\): \$([\d,]+)", r"Room and Board \(on-campus\): \$([\d,]+)", r"ROOM AND BOARD: \(on-campus\) \$([\d,]+)"],
    )
    if not tuition_match or not fees_match or not room_match:
        raise ValueError("Could not extract cost data")

    tuition = parse_number(tuition_match.group(1))
    fees = parse_number(fees_match.group(1))
    room_and_board = parse_number(room_match.group(1))
    return {
        "tuition": tuition,
        "fees": fees,
        "roomAndBoard": room_and_board,
        "totalCOA": tuition + fees + room_and_board,
    }


def extract_h2_rows(text: str) -> dict[str, str]:
    match = re.search(
        r"(?:H2 Number of Enrolled Students Awarded Aid|Number of Enrolled Students Awarded Aid:)(.*?)(?:H2A|Number of Enrolled Students Awarded Non-need-based Scholarships and Grants:)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return {}

    rows: dict[str, str] = {}
    current_key = ""
    current_parts: list[str] = []

    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        row_match = re.match(r"^(?:H2\s*)?([A-Ma-m])(?:[.)]|\s)", line)
        if row_match:
            if current_key:
                rows[current_key] = squish(" ".join(current_parts))
            current_key = row_match.group(1).upper()
            current_parts = [line]
        elif current_key:
            current_parts.append(line)

    if current_key:
        rows[current_key] = squish(" ".join(current_parts))

    return rows


def extract_financial_aid(text: str) -> dict:
    rows = extract_h2_rows(text)
    required = {"A", "D", "H", "J", "K"}
    if not required.issubset(rows):
        return {}

    def second_value(row_key: str) -> int | float:
        values = re.findall(r"\$?\d[\d,]*(?:\.\d+)?%?", rows[row_key])
        if len(values) < 2:
            return 0
        value = values[1]
        if value.endswith("%"):
            return parse_percent(value)
        return parse_number(value)

    total_students = int(second_value("A"))
    students_with_aid = int(second_value("D"))
    fully_met = int(second_value("H"))
    average_package = int(second_value("J"))
    average_grant = int(second_value("K"))

    return {
        "percentReceivingAid": round(students_with_aid / total_students, 4) if total_students else 0,
        "averageAidPackage": average_package,
        "averageNeedBasedGrant": average_grant,
        "percentNeedFullyMet": round(fully_met / students_with_aid, 4) if students_with_aid else 0,
    }


def build_year_data(text: str) -> dict:
    enrollment = extract_enrollment(text)
    by_race = extract_by_race(text)
    return {
        "admissions": extract_admissions(text),
        "testScores": extract_test_scores(text),
        "demographics": {
            "enrollment": enrollment,
            "byRace": by_race,
            "byResidency": extract_residency(text, enrollment["undergraduate"], by_race["international"]),
        },
        "costs": extract_costs(text),
        "financialAid": extract_financial_aid(text),
    }


def main() -> None:
    base_dir = Path("College-Data/UCSanDiego")
    output_path = Path("src/data/schools/ucsandiego.json")

    school_data = {
        "name": "University of California, San Diego",
        "slug": "ucsandiego",
        "years": {},
    }

    for year, filename in YEAR_FILES.items():
        text = load_text(base_dir / filename)
        school_data["years"][year] = build_year_data(text)

    output_path.write_text(json.dumps(school_data, indent=2) + "\n")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
