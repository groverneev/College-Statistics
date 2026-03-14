#!/usr/bin/env python3
"""
Extract Johns Hopkins University CDS data from local PDF files.

This parser targets the recent JHU CDS layouts available in
College-Data/JohnHopkinsUniversity/.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "College-Data" / "JohnHopkinsUniversity"
OUTPUT_PATH = ROOT / "src" / "data" / "schools" / "johnshopkins.json"

PDF_FILES = {
    "2021-2022": "CDS_2021-2022.pdf",
    "2022-2023": "CDS_2022-2023-3.19.24.pdf",
    "2023-2024": "CDS_2023-2024_JHU_20250401.pdf",
    "2024-2025": "CDS_2024-2025_JHU.pdf",
}


def clean_number(value: str) -> int:
    digits = re.sub(r"[^\d]", "", value or "")
    return int(digits) if digits else 0


def extract_text(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join((page.extract_text() or "") for page in pdf.pages)


def first_int(pattern: str, text: str) -> int:
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return clean_number(match.group(1)) if match else 0


def first_float(pattern: str, text: str) -> float:
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    if not match:
        return 0.0
    raw = match.group(1).replace("%", "").replace(",", "").strip()
    return float(raw) if raw else 0.0


def parse_percentile_row(text: str, label: str, digits: int) -> tuple[int, int, int]:
    three_value = re.search(
        rf"{label}\s+([0-9]{{{digits}}})\s+([0-9]{{{digits}}})\s+([0-9]{{{digits}}})",
        text,
        re.IGNORECASE | re.MULTILINE,
    )
    if three_value:
        return tuple(int(three_value.group(i)) for i in range(1, 4))

    two_value = re.search(
        rf"{label}\s+([0-9]{{{digits}}})\s+([0-9]{{{digits}}})",
        text,
        re.IGNORECASE | re.MULTILINE,
    )
    if two_value:
        p25 = int(two_value.group(1))
        p75 = int(two_value.group(2))
        return p25, (p25 + p75) // 2, p75

    return 0, 0, 0


def parse_admissions(text: str) -> dict[str, Any]:
    gender_variants = [
        ("men", "men"),
        ("women", "women"),
        ("another gender", "anotherGender"),
        ("unknown gender", "unknownGender"),
        ("unknown", "unknownGender"),
        ("other/not reported", "unknownGender"),
    ]

    by_gender = {
        "men": {"applied": 0, "admitted": 0, "enrolled": 0},
        "women": {"applied": 0, "admitted": 0, "enrolled": 0},
    }
    extra_totals = {"applied": 0, "admitted": 0, "enrolled": 0}

    for label, bucket in gender_variants:
        applied = first_int(
            rf"Total first-time, first-year(?: \([^)]+\))? {re.escape(label)} who applied\s+([0-9,]+)",
            text,
        )
        admitted = first_int(
            rf"Total first-time, first-year(?: \([^)]+\))? {re.escape(label)} who were admitted\s+([0-9,]+)",
            text,
        )
        full_time = first_int(
            rf"Total full-time, first-time, first-year(?: \([^)]+\))? {re.escape(label)} who enrolled\s+([0-9,]+)",
            text,
        )
        part_time = first_int(
            rf"Total part-time, first-time, first-year(?: \([^)]+\))? {re.escape(label)} who enrolled\s+([0-9,]+)",
            text,
        )
        enrolled = full_time + part_time

        if bucket in by_gender:
            by_gender[bucket]["applied"] = applied
            by_gender[bucket]["admitted"] = admitted
            by_gender[bucket]["enrolled"] = enrolled
        else:
            extra_totals["applied"] += applied
            extra_totals["admitted"] += admitted
            extra_totals["enrolled"] += enrolled

    applied = sum(group["applied"] for group in by_gender.values()) + extra_totals["applied"]
    admitted = sum(group["admitted"] for group in by_gender.values()) + extra_totals["admitted"]
    enrolled = sum(group["enrolled"] for group in by_gender.values()) + extra_totals["enrolled"]

    early_applied = first_int(
        r"Number of early decision applications received by your institution\s+([0-9,\s]+)",
        text,
    )
    early_admitted = first_int(
        r"Number of applicants admitted under early decision plan\s+([0-9,\s]+)",
        text,
    )

    admissions: dict[str, Any] = {
        "applied": applied,
        "admitted": admitted,
        "enrolled": enrolled,
        "acceptanceRate": round(admitted / applied, 4) if applied else 0,
        "yield": round(enrolled / admitted, 4) if admitted else 0,
        "byGender": by_gender,
    }

    if early_applied and early_admitted:
        admissions["earlyDecision"] = {
            "applied": early_applied,
            "admitted": early_admitted,
        }

    return admissions


def parse_test_scores(text: str) -> dict[str, Any]:
    sat_submission = first_float(r"Submitting SAT Scores\s+([0-9.]+)%", text) / 100
    act_submission = first_float(r"Submitting ACT Scores\s+([0-9.]+)%", text) / 100

    sat_composite = parse_percentile_row(text, r"SAT Composite", 4)
    sat_reading = parse_percentile_row(
        text, r"SAT Evidence-Based Reading(?: and(?:\s+Writing)?)?", 3
    )
    sat_math = parse_percentile_row(text, r"SAT Math", 3)
    act_composite = parse_percentile_row(text, r"ACT Composite", 2)

    data: dict[str, Any] = {}

    if sat_composite[0] and sat_reading[0] and sat_math[0]:
        data["sat"] = {
            "composite": {
                "p25": sat_composite[0],
                "p50": sat_composite[1],
                "p75": sat_composite[2],
            },
            "readingWriting": {
                "p25": sat_reading[0],
                "p50": sat_reading[1],
                "p75": sat_reading[2],
            },
            "math": {
                "p25": sat_math[0],
                "p50": sat_math[1],
                "p75": sat_math[2],
            },
            "submissionRate": round(sat_submission, 4),
        }

    if act_composite[0]:
        data["act"] = {
            "composite": {
                "p25": act_composite[0],
                "p50": act_composite[1],
                "p75": act_composite[2],
            },
            "submissionRate": round(act_submission, 4),
        }

    return data


def parse_demographics(text: str) -> dict[str, Any]:
    undergraduate = first_int(r"Total all undergraduates\s+([0-9,\s]+)", text)
    total = first_int(r"GRAND TOTAL ALL STUDENTS\s+([0-9,\s]+)", text)
    graduate = max(total - undergraduate, 0) if total and undergraduate else 0

    race_patterns = {
        "international": r"Nonresident(?: aliens|s)?\s+([0-9,\s]+)\s+([0-9,\s]+)",
        "hispanicLatino": r"Hispanic/Latino\s+([0-9,\s]+)\s+([0-9,\s]+)",
        "blackAfricanAmerican": r"Black or African American, non-Hispanic\s+([0-9,\s]+)\s+([0-9,\s]+)",
        "white": r"White, non-Hispanic\s+([0-9,\s]+)\s+([0-9,\s]+)",
        "americanIndianAlaskaNative": r"American Indian or Alaska Native, non-Hispanic\s+([0-9,\s]+)\s+([0-9,\s]+)",
        "asian": r"Asian, non-Hispanic\s+([0-9,\s]+)\s+([0-9,\s]+)",
        "nativeHawaiianPacificIslander": r"Native Hawaiian or other Pacific Islander, non-[\s-]*Hisp(?:anic)?\s+([0-9,\s]+)\s+([0-9,\s]+)",
        "twoOrMoreRaces": r"Two or more races, non-Hispanic\s+([0-9,\s]+)\s+([0-9,\s]+)",
        "unknown": r"Race and/or ethnicity unknown\s+([0-9,\s]+)\s+([0-9,\s]+)",
    }

    by_race: dict[str, int] = {}
    for field, pattern in race_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        by_race[field] = clean_number(match.group(2)) if match else 0

    race_sum = sum(by_race.values())
    if undergraduate and race_sum < undergraduate:
        by_race["unknown"] += undergraduate - race_sum

    out_of_state_match = re.search(
        r"Percent who are from out of state .*?([0-9.]+)%\s+([0-9.]+)%",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    out_of_state_pct = float(out_of_state_match.group(2)) if out_of_state_match else 0.0
    if not out_of_state_pct:
        single_pct = re.search(
            r"Percent who are from out of state .*?([0-9.]+)%",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        out_of_state_pct = float(single_pct.group(1)) if single_pct else 0.0

    international = by_race["international"]
    domestic = max(undergraduate - international, 0)
    out_of_state = round(domestic * (out_of_state_pct / 100)) if domestic else 0
    in_state = max(domestic - out_of_state, 0)

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
            "international": international,
        },
    }


def parse_costs(text: str) -> dict[str, int]:
    tuition = first_int(r"Tuition:\s*\$([0-9,\s]+)", text)
    fees = first_int(r"Required Fees:?\s*\$([0-9,\s]+)", text)
    room_and_board = (
        first_int(r"Room and Board \(on-campus\):\s*\$([0-9,\s]+)", text)
        or first_int(r"Food and housing \(on-campus\):\s*\$([0-9,\s]+)", text)
    )

    return {
        "tuition": tuition,
        "fees": fees,
        "roomAndBoard": room_and_board,
        "totalCOA": tuition + fees + room_and_board,
    }


def parse_financial_aid(text: str) -> dict[str, Any]:
    def first_match(pattern: str) -> int:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return clean_number(match.group(1)) if match else 0

    aid_population = first_match(
        r"A Number of degree-seeking undergraduate students[\s\S]{0,160}?([0-9,]+)\s+[0-9,]+\s+[0-9,]+"
    )
    awarded_any = first_match(
        r"D Number of students[\s\S]{0,160}?awarded any[\s\S]{0,80}?financial aid[\s\S]{0,60}?([0-9,]+)\s+[0-9,]+\s+[0-9,]+"
    )
    fully_met = first_match(
        r"H Number of students[\s\S]{0,200}?whose need was fully met[\s\S]{0,80}?([0-9,]+)\s+[0-9,]+\s+(?:[0-9,]+|n/a)"
    )
    average_package = first_match(
        r"\nJ The average financial aid package of those in line d\.[\s\S]{0,200}?\$\s*([0-9,]+)\s+\$\s*[0-9,]+\s+\$?\s*(?:-|0|n/a)"
    )
    average_grant = first_match(
        r"\nK[\s\S]{0,120}?\$\s*([0-9,]+)\s+\$\s*[0-9,]+\s+\$?\s*(?:-|0|n/a)"
    )

    return {
        "percentReceivingAid": round(awarded_any / aid_population, 4) if aid_population else 0,
        "averageAidPackage": average_package,
        "averageNeedBasedGrant": average_grant,
        "percentNeedFullyMet": round(fully_met / awarded_any, 4) if awarded_any else 0,
    }


def parse_pdf(pdf_path: Path) -> dict[str, Any]:
    text = extract_text(pdf_path)
    return {
        "admissions": parse_admissions(text),
        "testScores": parse_test_scores(text),
        "demographics": parse_demographics(text),
        "costs": parse_costs(text),
        "financialAid": parse_financial_aid(text),
    }


def main() -> None:
    data = {
        "name": "Johns Hopkins University",
        "slug": "johnshopkins",
        "years": {},
    }

    for year, filename in PDF_FILES.items():
        data["years"][year] = parse_pdf(PDF_DIR / filename)

    OUTPUT_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
