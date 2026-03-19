#!/usr/bin/env python3
"""
UCI CDS extractor.

Builds a clean UCI dataset from official CDS PDFs. Most years come directly
from UCI's CDS archive; for 2018-2019 through 2020-2021, UCI's G-section cost
cells are blank in the PDFs, so those cost fields are backfilled from UCI's
registrar fee archives plus IPEDS-derived living-cost data.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber


YEAR_FILES = {
    "2016-2017": "2016-17.pdf",
    "2017-2018": "2017-18.pdf",
    "2018-2019": "2018-19.pdf",
    "2019-2020": "2019-20.pdf",
    "2020-2021": "2020-21.pdf",
    "2021-2022": "2021-22.pdf",
    "2022-2023": "2022-23.pdf",
    "2023-2024": "2023-24.pdf",
    "2024-2025": "2024-25.pdf",
}


COST_OVERRIDES = {
    # 2016-2017 and 2017-2018 come directly from UCI's G1 text rows in the
    # official CDS PDFs.
    "2016-2017": {"tuition": 11502, "fees": 4014, "roomAndBoard": 14829},
    "2017-2018": {"tuition": 11442, "fees": 2258, "roomAndBoard": 15263},
    # 2018-2019 through 2020-2021 use official UCI registrar tuition/fee
    # archives for tuition + required fees (excluding health insurance), and
    # CollegeTuitionCompare's IPEDS-based on-campus living-cost history for
    # room and board.
    "2018-2019": {"tuition": 11442, "fees": 2258, "roomAndBoard": 18763},
    "2019-2020": {"tuition": 11442, "fees": 2285, "roomAndBoard": 19198},
    "2020-2021": {"tuition": 11442, "fees": 2311, "roomAndBoard": 20246},
    # All values below come from official UCI CDS PDFs:
    # - 2022-2023 and 2023-2024 are from the 2022-23 CDS current/previous columns
    # - 2024-2025 and 2025-2026 are from the 2024-25 CDS previous/current columns
    "2021-2022": {"tuition": 11834, "fees": 2433, "roomAndBoard": 18639},
    "2022-2023": {"tuition": 12522, "fees": 2663, "roomAndBoard": 18639},
    "2023-2024": {"tuition": 12800, "fees": 2558, "roomAndBoard": 19653},
    "2024-2025": {"tuition": 13602, "fees": 2852, "roomAndBoard": 19653},
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


def find_line_value(text: str, pattern: str) -> int:
    match = re.search(pattern, text, re.IGNORECASE)
    return parse_number(match.group(1)) if match else 0


def extract_admissions(text: str) -> dict:
    legacy_men_applied = find_line_value(
        text, r"Total first-time, first-year (?:\(freshman\) )?men who applied\s+([\d,\.]+)"
    )
    legacy_women_applied = find_line_value(
        text, r"Total first-time, first-year (?:\(freshman\) )?women who applied\s+([\d,\.]+)"
    )
    legacy_another_applied = find_line_value(
        text, r"Total first-time, first-year another gender who applied\s+([\d,\.]+)"
    )
    legacy_men_admitted = find_line_value(
        text, r"Total first-time, first-year (?:\(freshman\) )?men who were admitted\s+([\d,\.]+)"
    )
    legacy_women_admitted = find_line_value(
        text, r"Total first-time, first-year (?:\(freshman\) )?women who were admitted\s+([\d,\.]+)"
    )
    legacy_another_admitted = find_line_value(
        text, r"Total first-time, first-year another gender who were admitted\s+([\d,\.]+)"
    )
    legacy_men_enrolled = find_line_value(
        text, r"Total full-time, first-time, first-year (?:\(freshman\) )?men who enrolled\s+([\d,\.]+)"
    ) + find_line_value(
        text, r"Total part-time, first-time, first-year (?:\(freshman\) )?men who enrolled\s+([\d,\.]+)"
    )
    legacy_women_enrolled = find_line_value(
        text, r"Total full-time, first-time, first-year (?:\(freshman\) )?women who enrolled\s+([\d,\.]+)"
    ) + find_line_value(
        text, r"Total part-time, first-time, first-year (?:\(freshman\) )?women who enrolled\s+([\d,\.]+)"
    )
    legacy_another_enrolled = find_line_value(
        text, r"Total full-time, first-time, first-year another gender who enrolled\s+([\d,\.]+)"
    ) + find_line_value(
        text, r"Total part-time, first-time, first-year another gender who enrolled\s+([\d,\.]+)"
    )

    if legacy_men_applied or legacy_women_applied:
        applied = legacy_men_applied + legacy_women_applied + legacy_another_applied
        admitted = legacy_men_admitted + legacy_women_admitted + legacy_another_admitted
        enrolled = legacy_men_enrolled + legacy_women_enrolled + legacy_another_enrolled
    else:
        applied_match = re.search(
            r"Total first-time, first-year students who applied in Fall 2023\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
            text,
            re.IGNORECASE,
        )
        admitted_match = re.search(
            r"Total first-time, first-year students admitted in Fall 2023\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
            text,
            re.IGNORECASE,
        )
        enrolled_match = re.search(
            r"Total first-time, first-year students enrolled in Fall 2023\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
            text,
            re.IGNORECASE,
        )
        applied = sum(parse_number(group) for group in applied_match.groups())
        admitted = sum(parse_number(group) for group in admitted_match.groups())
        enrolled = sum(parse_number(group) for group in enrolled_match.groups())

    return {
        "applied": applied,
        "admitted": admitted,
        "enrolled": enrolled,
        "acceptanceRate": round(admitted / applied, 4) if applied else 0,
        "yield": round(enrolled / admitted, 4) if admitted else 0,
    }


def extract_test_scores(text: str) -> dict:
    flat = squish(text)

    def first_match(patterns: list[str]) -> re.Match[str] | None:
        for pattern in patterns:
            match = re.search(pattern, flat, re.IGNORECASE)
            if match:
                return match
        return None

    sat_composite = first_match(
        [
            r"SAT Composite(?: \(400 - 1600\))?\s+(\d{3,4})\s+(?:\d{3,4}\s+)?(\d{3,4})",
        ]
    )
    sat_rw = first_match(
        [
            r"SAT Evidence-Based Reading and(?: Writing)?\s+(\d{3})\s+(?:\d{3}\s+)?(\d{3})",
            r"SAT Evidence-\s*Based Reading and Writing\s+(\d{3})\s+(\d{3})",
            r"SAT Critical Reading\s+(\d{3})\s+(\d{3})",
        ]
    )
    sat_math = first_match(
        [
            r"SAT Math(?: \(200 - 800\))?\s+(\d{3})\s+(?:\d{3}\s+)?(\d{3})",
        ]
    )
    sat_submit = first_match(
        [
            r"Submitting SAT Scores\s+(\d+(?:\.\d+)?)%",
            r"Percent submitting SAT scores\s+(\d+(?:\.\d+)?)%",
        ]
    )
    act_composite = first_match(
        [
            r"ACT Composite(?: \(0 - 36\))?\s+(\d{2})\s+(?:\d{2}\s+)?(\d{2})",
        ]
    )
    act_submit = first_match(
        [
            r"Submitting ACT Scores\s+(\d+(?:\.\d+)?)%",
            r"Percent submitting ACT scores\s+(\d+(?:\.\d+)?)%",
        ]
    )

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
    undergrad_match = re.search(
        r"(?:Total all undergraduate[s]?|Total of all undergraduate students enrolled)\.?\s+([\d,\.]+)",
        text,
        re.IGNORECASE,
    )
    grad_match = re.search(
        r"(?:Total all graduate|Total of all graduate students enrolled)\.?\s+([\d,\.]+)",
        text,
        re.IGNORECASE,
    )

    undergrad = parse_number(undergrad_match.group(1)) if undergrad_match else 0
    graduate = parse_number(grad_match.group(1)) if grad_match else 0

    if not graduate:
        graduate_line = re.search(
            r"Total Graduate Students\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
            text,
            re.IGNORECASE,
        )
        if graduate_line:
            graduate = sum(parse_number(group) for group in graduate_line.groups())

    return {
        "total": undergrad + graduate,
        "undergraduate": undergrad,
        "graduate": graduate,
    }


def extract_by_race(text: str) -> dict:
    flat = squish(text)
    patterns = {
        "international": [
            r"International \(nonresidents\)\s+[\d,\.]+\s+([\d,\.]+)\s+[\d,\.]+",
            r"Nonresident aliens\s+[\d,\.]+\s+([\d,\.]+)\s+[\d,\.]+",
            r"Nonresidents\s+[\d,\.]+\s+([\d,\.]+)\s+[\d,\.]+",
        ],
        "hispanicLatino": [r"Hispanic/Latino\s+[\d,\.]+\s+([\d,\.]+)\s+[\d,\.]+"],
        "blackAfricanAmerican": [r"Black or African American, non-Hispanic\s+[\d,\.]+\s+([\d,\.]+)\s+[\d,\.]+"],
        "white": [r"White, non-Hispanic\s+[\d,\.]+\s+([\d,\.]+)\s+[\d,\.]+"],
        "americanIndianAlaskaNative": [
            r"American Indian or Alaska Native,?\s*non-?\s*Hispanic\s+[\d,\.]+\s+([\d,\.]+)\s+[\d,\.]+",
            r"American Indian or Alaska Native,?\s*non-\s*[\d,\.]+\s+([\d,\.]+)\s+[\d,\.]+\s*Hispanic",
        ],
        "asian": [r"Asian, non-Hispanic\s+[\d,\.]+\s+([\d,\.]+)\s+[\d,\.]+"],
        "nativeHawaiianPacificIslander": [
            r"Native Hawaiian or other Pacific Islander,?\s*non-?\s*Hispanic\s+[\d,\.]+\s+([\d,\.]+)\s+[\d,\.]+",
            r"Native Hawaiian or other Pacific Islander,?\s*[\d,\.]+\s+([\d,\.]+)\s+[\d,\.]+\s*non-\s*Hispanic",
        ],
        "twoOrMoreRaces": [r"Two or more races, non-Hispanic\s+[\d,\.]+\s+([\d,\.]+)\s+[\d,\.]+"],
        "unknown": [r"Race and/or ethnicity unknown\s+[\d,\.]+\s+([\d,\.]+)\s+[\d,\.]+"],
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
    match = re.search(
        r"Percent who are from out of state.*?(\d+(?:\.\d+)?)%\s+(\d+(?:\.\d+)?)%",
        squish(text),
        re.IGNORECASE,
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


def extract_h2_rows(text: str) -> dict[str, str]:
    match = re.search(
        r"H2(?:\.|\s).*?Awarded Aid(.*?)(?:H2A|H4)",
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
        row_match = re.match(r"^([A-M])(?:[.)])?\s", line)
        if row_match:
            if current_key:
                rows[current_key] = squish(" ".join(current_parts))
            current_key = row_match.group(1)
            current_parts = [line]
        elif current_key:
            current_parts.append(line)

    if current_key:
        rows[current_key] = squish(" ".join(current_parts))

    return rows


def extract_financial_aid_legacy(text: str) -> dict | None:
    flat = squish(text)
    patterns = {
        "total_students": r"H2 a\).*?(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)",
        "students_with_aid": r"H2 d\).*?(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)",
        "fully_met": r"H2 h\).*?(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)",
        "average_package": r"H2 j\).*?\$?\s*(\d[\d,]*)\s+\$?\s*(\d[\d,]*)\s+\$?\s*(\d[\d,]*)",
        "average_grant": r"k\)\s+\$?\s*(\d[\d,]*)\s+\$?\s*(\d[\d,]*)\s+\$?\s*(\d[\d,]*)",
    }

    values: dict[str, int] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, flat, re.IGNORECASE)
        if not match:
            return None
        values[key] = parse_number(match.group(2))

    total_students = values["total_students"]
    students_with_aid = values["students_with_aid"]
    fully_met = values["fully_met"]

    return {
        "percentReceivingAid": round(students_with_aid / total_students, 4) if total_students else 0,
        "averageAidPackage": values["average_package"],
        "averageNeedBasedGrant": values["average_grant"],
        "percentNeedFullyMet": round(fully_met / students_with_aid, 4) if students_with_aid else 0,
    }


def extract_financial_aid(text: str) -> dict:
    rows = extract_h2_rows(text)
    required_keys = {"A", "D", "H", "J", "K"}
    if not rows or not required_keys.issubset(rows):
        legacy = extract_financial_aid_legacy(text)
        if legacy:
            return legacy

    def second_integer(row_key: str) -> int:
        raw_numbers = [parse_number(value) for value in re.findall(r"\d[\d,]*(?:\.\d+)?", rows[row_key])]
        numbers = [value for value in raw_numbers if value < 1900 or value > 2100]
        if len(numbers) > 3:
            numbers = [value for value in numbers if value >= 10]
        return numbers[1]

    total_students = second_integer("A")
    students_with_aid = second_integer("D")
    fully_met = second_integer("H")
    average_package = second_integer("J")
    average_grant = second_integer("K")

    return {
        "percentReceivingAid": round(students_with_aid / total_students, 4) if total_students else 0,
        "averageAidPackage": average_package,
        "averageNeedBasedGrant": average_grant,
        "percentNeedFullyMet": round(fully_met / students_with_aid, 4) if students_with_aid else 0,
    }


def build_year_data(text: str, year: str) -> dict:
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
        "costs": {
            **COST_OVERRIDES[year],
            "totalCOA": sum(COST_OVERRIDES[year].values()),
        },
        "financialAid": extract_financial_aid(text),
    }


def main() -> None:
    base_dir = Path("College-Data/UCI")
    output_path = Path("src/data/schools/uci.json")

    school_data = {
        "name": "University of California, Irvine",
        "slug": "uci",
        "years": {},
    }

    for year, filename in YEAR_FILES.items():
        text = load_text(base_dir / filename)
        school_data["years"][year] = build_year_data(text, year)

    output_path.write_text(json.dumps(school_data, indent=2) + "\n")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
