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
    "2021-2022": "UCSD-CDS_2021-2022.pdf",
    "2022-2023": "UCSD-CDS_2022-20233.pdf",
    "2023-2024": "CDS_UCSD_2023_20242.pdf",
    "2024-2025": "CDS_2024-2025_Final1.pdf",
}

OFFICIAL_COST_OVERRIDES = {
    "2016-2017": {"tuition": 12630, "fees": 3553, "roomAndBoard": 13254},
}

WEB_FINANCIAL_AID_OVERRIDES = {
    # Source: secondary web summaries quoting 2021-2022 first-year aid stats:
    # https://collegegazette.com/ucsd-out-of-state-acceptance-rate/
    # https://www.spainexchange.com/faq/does-ucsd-give-financial-aid-to-out-of-state-students
    # Approximate need-met proxy from:
    # https://www.collegetransitions.com/dataverse/colleges-meeting-your-financial-need
    #
    # UCSD's official 2021-2022 CDS H2/H2A pages are blank in the published PDF, and
    # public web sources expose first-year aid values rather than the usual CDS full-time
    # undergraduate cohort. We backfill the available fields and use College Transitions'
    # published need-met percentage as an approximate proxy for the site's "need fully met"
    # field so the year is complete on the frontend.
    "2021-2022": {
        "percentReceivingAid": 0.59,
        "averageAidPackage": 25036,
        "averageNeedBasedGrant": 25700,
        "percentNeedFullyMet": 0.83,
    },
    # Source: official UC San Diego IR CDS PDF:
    # https://ir.ucsd.edu/stats/undergrad/CDS_2024-2025_Final1.pdf
    # H2 full-time undergrad values:
    # A=34,101 D=18,028 H=1,996 J=$30,549 K=$27,393
    "2024-2025": {
        "percentReceivingAid": 0.5287,
        "averageAidPackage": 30549,
        "averageNeedBasedGrant": 27393,
        "percentNeedFullyMet": 0.1107,
    },
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
            r"Total first-time, first-year \(degree-seeking\) who applied\s+([\d,]+).*?"
            r"Total first-time, first-year \(degree-seeking\) who were admitted\s+([\d,]+).*?"
            r"Total first-time, first-year \(degree-seeking\) enrolled\s+([\d,]+)",
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
        parse_number(value)
        for value in re.findall(
            r"Total first-time, first-year (?:(?:\(freshman\) )?)"
            r"(?:men|women|males|females|of another/unknown gender|students of unknown sex)"
            r" who applied\s+([\d,]+)",
            flat,
            re.IGNORECASE,
        )
    )
    admitted = sum(
        parse_number(value)
        for value in re.findall(
            r"Total first-time, first-year (?:(?:\(freshman\) )?)"
            r"(?:men|women|males|females|of another/unknown gender|students of unknown sex)"
            r" who were admitted\s+([\d,]+)",
            flat,
            re.IGNORECASE,
        )
    )
    enrolled_total_rows = re.findall(
        r"Total first-time, first-year (?:(?:\(freshman\) )?)"
        r"(?:men|women|males|females|of another/unknown gender|students of unknown sex)"
        r" who enroll(?:ed)?\s+([\d,]+)",
        flat,
        re.IGNORECASE,
    )
    if enrolled_total_rows:
        enrolled = sum(parse_number(value) for value in enrolled_total_rows)
    else:
        enrolled = sum(
            parse_number(value)
            for value in re.findall(
                r"Total (?:(?:full-time|part-time),? )first-time, first-year (?:(?:\(freshman\) )?)"
                r"(?:men|women|males|females|of another/unknown gender|students of unknown sex)"
                r" who enroll(?:ed)?\s+([\d,]+)",
                flat,
                re.IGNORECASE,
            )
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
            r"SAT Evidence-Based Reading and\s+Writing\s+(\d{3})\s+(\d{3})",
            r"SAT Evidence-Based Reading and\s+(\d{3})\s+(\d{3})\s+Writing",
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
    undergrad_match = find_match(
        flat,
        [
            r"Total all undergraduates\s+([\d,]+)",
            r"Total of all undergraduate degree-seeking students\s+([\d,]+)",
        ],
    )
    grad_match = find_match(
        flat,
        [
            r"Total all graduate\s+([\d,]+)",
            r"Total of all graduate degree-seeking students\s+([\d,]+)",
            r"Total of all graduate students enrolled\s+([\d,]+)",
        ],
    )
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
            r"\$([\d,]+)\s+\$[\d,]+\s+In-state \(out-of-district\):",
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

    def extract_triplet(row_key: str) -> list[str]:
        values = re.findall(r"\$?\d[\d,]*(?:\.\d+)?%?", rows[row_key])
        if len(values) < 3:
            return []

        for i in range(len(values) - 2):
            window = values[i : i + 3]
            parsed = []
            for raw in window:
                if raw.endswith("%"):
                    parsed.append(float(raw[:-1]))
                else:
                    parsed.append(parse_number(raw))

            first, second, third = parsed
            if first >= 100 and second >= 100 and first >= third and second >= third:
                return window

        return values[-3:]

    def middle_value(row_key: str) -> int | float:
        triplet = extract_triplet(row_key)
        if len(triplet) < 3:
            return 0
        value = triplet[1]
        if value.endswith("%"):
            return parse_percent(value)
        return parse_number(value)

    total_students = int(middle_value("A"))
    students_with_aid = int(middle_value("D"))
    fully_met = int(middle_value("H"))
    average_package = int(middle_value("J"))
    average_grant = int(middle_value("K"))

    return {
        "percentReceivingAid": round(students_with_aid / total_students, 4) if total_students else 0,
        "averageAidPackage": average_package,
        "averageNeedBasedGrant": average_grant,
        "percentNeedFullyMet": round(fully_met / students_with_aid, 4) if students_with_aid else 0,
    }


def build_year_data(year: str, text: str) -> dict:
    enrollment = extract_enrollment(text)
    by_race = extract_by_race(text)
    costs = OFFICIAL_COST_OVERRIDES.get(year)
    if costs:
        costs = {**costs, "totalCOA": sum(costs.values())}
    else:
        costs = extract_costs(text)
    financial_aid = WEB_FINANCIAL_AID_OVERRIDES.get(year, extract_financial_aid(text))
    return {
        "admissions": extract_admissions(text),
        "testScores": extract_test_scores(text),
        "demographics": {
            "enrollment": enrollment,
            "byRace": by_race,
            "byResidency": extract_residency(text, enrollment["undergraduate"], by_race["international"]),
        },
        "costs": costs,
        "financialAid": financial_aid,
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
        school_data["years"][year] = build_year_data(year, text)

    output_path.write_text(json.dumps(school_data, indent=2) + "\n")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
