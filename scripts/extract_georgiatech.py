#!/usr/bin/env python3
"""
Georgia Tech CDS extractor.

Builds a Georgia Tech dataset from the local Common Data Set PDFs in
College-Data/GeorgiaTech. The PDF layout differs enough from the generic CDS
extractor that we use targeted text parsing for the sections that power the
site.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "College-Data" / "GeorgiaTech"
OUTPUT_PATH = ROOT / "src" / "data" / "schools" / "georgiatech.json"

MANUAL_FINANCIAL_AID = {
    "2016-2017": {
        "percentReceivingAid": 0.4023,
        "averageAidPackage": 13171,
        "averageNeedBasedGrant": 11070,
        "percentNeedFullyMet": 0.1601,
    },
    "2017-2018": {
        "percentReceivingAid": 0.3760,
        "averageAidPackage": 13016,
        "averageNeedBasedGrant": 7194,
        "percentNeedFullyMet": 0.3951,
    },
    "2018-2019": {
        "percentReceivingAid": 0.4013,
        "averageAidPackage": 14422,
        "averageNeedBasedGrant": 12581,
        "percentNeedFullyMet": 0.2503,
    },
    "2019-2020": {
        "percentReceivingAid": 0.3062,
        "averageAidPackage": 14292,
        "averageNeedBasedGrant": 12474,
        "percentNeedFullyMet": 0.2640,
    },
    "2020-2021": {
        "percentReceivingAid": 0.3715,
        "averageAidPackage": 15631,
        "averageNeedBasedGrant": 13700,
        "percentNeedFullyMet": 0.1776,
    },
    "2021-2022": {
        "percentReceivingAid": 0.3633,
        "averageAidPackage": 15587,
        "averageNeedBasedGrant": 9507,
        "percentNeedFullyMet": 0.2432,
    },
    "2022-2023": {
        "percentReceivingAid": 0.3543,
        "averageAidPackage": 14479,
        "averageNeedBasedGrant": 13687,
        "percentNeedFullyMet": 0.2084,
    },
    "2023-2024": {
        "percentReceivingAid": 0.3374,
        "averageAidPackage": 16764,
        "averageNeedBasedGrant": 15171,
        "percentNeedFullyMet": 0.2178,
    },
    "2024-2025": {
        "percentReceivingAid": 0.3493,
        "averageAidPackage": 17219,
        "averageNeedBasedGrant": 15204,
        "percentNeedFullyMet": 0.2107,
    },
    "2025-2026": {
        "percentReceivingAid": 0.3158,
        "averageAidPackage": 19224,
        "averageNeedBasedGrant": 16851,
        "percentNeedFullyMet": 0.2048,
    },
}

MANUAL_TEST_SCORES = {
    "2024-2025": {
        "sat": {
            "composite": {"p25": 1370, "p50": 1460, "p75": 1530},
            "readingWriting": {"p25": 680, "p50": 720, "p75": 750},
            "math": {"p25": 690, "p50": 760, "p75": 790},
            "submissionRate": 0.77,
        },
        "act": {
            "composite": {"p25": 30, "p50": 33, "p75": 34},
            "submissionRate": 0.35,
        },
    },
    "2025-2026": {
        "sat": {
            "composite": {"p25": 1370, "p50": 1460, "p75": 1530},
            "readingWriting": {"p25": 680, "p50": 730, "p75": 760},
            "math": {"p25": 700, "p50": 750, "p75": 790},
            "submissionRate": 0.78,
        },
        "act": {
            "composite": {"p25": 31, "p50": 33, "p75": 35},
            "submissionRate": 0.33,
        },
    },
}


def parse_int(value: str) -> int:
    cleaned = value.replace(",", "").replace("$", "").replace(" ", "").strip()
    if cleaned.endswith(".00"):
        cleaned = cleaned[:-3]
    return int(float(cleaned))


def parse_float(value: str) -> float:
    cleaned = value.replace(",", "").replace("%", "").replace("$", "").replace(" ", "").strip()
    return float(cleaned)


def year_from_name(name: str) -> str:
    match = re.search(r"(\d{4})-(\d{4})", name)
    if not match:
        raise ValueError(f"Could not determine year from {name}")
    return f"{match.group(1)}-{match.group(2)}"


def maybe_match(patterns: list[str], text: str, flags: int = re.IGNORECASE | re.DOTALL):
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return match
    return None


def numbers_in_text(text: str) -> list[int]:
    return [int(round(float(num.replace(",", "")))) for num in re.findall(r"\d[\d,]*(?:\.\d+)?", text)]


def dollar_amounts(text: str) -> list[int]:
    return [int(round(float(amount.replace("$", "").replace(",", "")))) for amount in re.findall(r"\$\s*[\d,]+(?:\.\d+)?", text)]


def extract_admissions(text: str) -> dict:
    applied = admitted = enrolled = 0

    old_gender_patterns = {
        "applied": [
            r"Total first-time, first-year.*?males? who applied\s+([\d,\.]+)",
            r"Total first-time, first-year.*?men who applied\s+([\d,\.]+)",
        ],
        "female_applied": [
            r"Total first-time, first-year.*?females? who applied\s+([\d,\.]+)",
            r"Total first-time, first-year.*?women who applied\s+([\d,\.]+)",
        ],
        "unknown_applied": [
            r"students of unknown sex who applied\s+([\d,\.]+)",
        ],
        "admitted": [
            r"Total first-time, first-year.*?males? who were admitted\s+([\d,\.]+)",
            r"Total first-time, first-year.*?men who were admitted\s+([\d,\.]+)",
        ],
        "female_admitted": [
            r"Total first-time, first-year.*?females? who were admitted\s+([\d,\.]+)",
            r"Total first-time, first-year.*?women who were admitted\s+([\d,\.]+)",
        ],
        "unknown_admitted": [
            r"students of unknown sex who were admitted\s+([\d,\.]+)",
        ],
    }

    male_applied = maybe_match(old_gender_patterns["applied"], text)
    female_applied = maybe_match(old_gender_patterns["female_applied"], text)
    if male_applied and female_applied:
        applied = parse_int(male_applied.group(1)) + parse_int(female_applied.group(1))
        unknown = maybe_match(old_gender_patterns["unknown_applied"], text)
        if unknown:
            applied += parse_int(unknown.group(1))

    male_admitted = maybe_match(old_gender_patterns["admitted"], text)
    female_admitted = maybe_match(old_gender_patterns["female_admitted"], text)
    if male_admitted and female_admitted:
        admitted = parse_int(male_admitted.group(1)) + parse_int(female_admitted.group(1))
        unknown = maybe_match(old_gender_patterns["unknown_admitted"], text)
        if unknown:
            admitted += parse_int(unknown.group(1))

    enroll_matches = re.findall(
        r"Total (?:full-time|part-time), first-time, first-year .*? enrolled\s+([\d,\.]+)",
        text,
        re.IGNORECASE,
    )
    if enroll_matches:
        enrolled = sum(parse_int(value) for value in enroll_matches)

    if not applied:
        match = re.search(
            r"Total first-time, first-year students who applied in Fall \d{4}\s+[\d,\.]+\s+[\d,\.]+(?:\s+[\d,\.]+)?\s+([\d,\.]+)",
            text,
            re.IGNORECASE,
        )
        if match:
            applied = parse_int(match.group(1))

    if not admitted:
        match = re.search(
            r"Total first-time, first-year students admitted in Fall \d{4}\s+[\d,\.]+\s+[\d,\.]+(?:\s+[\d,\.]+)?\s+([\d,\.]+)",
            text,
            re.IGNORECASE,
        )
        if match:
            admitted = parse_int(match.group(1))

    if not enrolled:
        match = re.search(
            r"Total first-time, first-year students enrolled in Fall \d{4}\s+[\d,\.]+\s+[\d,\.]+(?:\s+[\d,\.]+)?\s+([\d,\.]+)",
            text,
            re.IGNORECASE,
        )
        if match:
            enrolled = parse_int(match.group(1))

    acceptance_rate = round(admitted / applied, 4) if applied else 0
    yield_rate = round(enrolled / admitted, 4) if admitted else 0

    return {
        "applied": applied,
        "admitted": admitted,
        "enrolled": enrolled,
        "acceptanceRate": acceptance_rate,
        "yield": yield_rate,
    }


def extract_test_scores(text: str, year: str) -> dict:
    if year in MANUAL_TEST_SCORES:
        return MANUAL_TEST_SCORES[year]

    data: dict = {}
    normalized = re.sub(r"\s+", " ", text)

    sat_submit = re.search(r"Submitting SAT Scores\s+(\d+(?:\.\d+)?)%", normalized, re.IGNORECASE)
    act_submit = re.search(r"Submitting ACT Scores\s+(\d+(?:\.\d+)?)%", normalized, re.IGNORECASE)

    sat_rw = re.search(
        r"SAT (?:Critical Reading|Evidence-Based Reading and Writing(?: \(200 - 800\))?)\s+(\d{3})\s+(\d{3})(?:\s+(\d{3}))?",
        normalized,
        re.IGNORECASE,
    )
    sat_math = re.search(
        r"SAT Math(?: \(200 - 800\))?\s+(\d{3})\s+(\d{3})(?:\s+(\d{3}))?",
        normalized,
        re.IGNORECASE,
    )
    sat_comp = re.search(
        r"SAT Composite(?: \(400 - 1600\))?\s+(\d{3,4})\s+(\d{3,4})(?:\s+(\d{3,4}))?",
        normalized,
        re.IGNORECASE,
    )
    act_comp = re.search(
        r"ACT Composite(?: \(0 - 36\))?\s+(\d{2})\s+(\d{2})(?:\s+(\d{2}))?",
        normalized,
        re.IGNORECASE,
    )

    if not sat_rw and sat_comp and sat_math:
        comp25 = parse_int(sat_comp.group(1))
        comp_mid = parse_int(sat_comp.group(2))
        comp75 = parse_int(sat_comp.group(3)) if sat_comp.group(3) else comp_mid
        if not sat_comp.group(3):
            comp_mid = (comp25 + comp75) // 2

        math25 = parse_int(sat_math.group(1))
        math_mid = parse_int(sat_math.group(2))
        math75 = parse_int(sat_math.group(3)) if sat_math.group(3) else math_mid
        if not sat_math.group(3):
            math_mid = (math25 + math75) // 2

        sat_rw = (
            str(comp25 - math25),
            str(comp_mid - math_mid),
            str(comp75 - math75),
        )

    if sat_rw and sat_math:
        if isinstance(sat_rw, tuple):
            rw25 = parse_int(sat_rw[0])
            rw_mid = parse_int(sat_rw[1])
            rw75 = parse_int(sat_rw[2])
        else:
            rw25 = parse_int(sat_rw.group(1))
            rw_mid = parse_int(sat_rw.group(2))
            rw75 = parse_int(sat_rw.group(3)) if sat_rw.group(3) else rw_mid
        if not isinstance(sat_rw, tuple) and not sat_rw.group(3):
            rw_mid = (rw25 + rw75) // 2

        math25 = parse_int(sat_math.group(1))
        math_mid = parse_int(sat_math.group(2))
        math75 = parse_int(sat_math.group(3)) if sat_math.group(3) else math_mid
        if not sat_math.group(3):
            math_mid = (math25 + math75) // 2

        data["sat"] = {
            "composite": {
                "p25": rw25 + math25,
                "p50": rw_mid + math_mid,
                "p75": rw75 + math75,
            },
            "readingWriting": {"p25": rw25, "p50": rw_mid, "p75": rw75},
            "math": {"p25": math25, "p50": math_mid, "p75": math75},
            "submissionRate": round(parse_float(sat_submit.group(1)) / 100, 4) if sat_submit else 0,
        }

    if act_comp:
        act25 = parse_int(act_comp.group(1))
        act_mid = parse_int(act_comp.group(2))
        act75 = parse_int(act_comp.group(3)) if act_comp.group(3) else act_mid
        if not act_comp.group(3):
            act_mid = (act25 + act75) // 2

        data["act"] = {
            "composite": {"p25": act25, "p50": act_mid, "p75": act75},
            "submissionRate": round(parse_float(act_submit.group(1)) / 100, 4) if act_submit else 0,
        }

    return data


def extract_demographics(text: str) -> dict:
    undergraduate_match = maybe_match(
        [
            r"Total of all undergraduate students enrolled\s+([\d,\.]+)",
            r"Total all undergraduates\s+([\d,\.\s]+)",
            r"TOTAL\s+[\d,\.\s]+\s+[\d,\.\s]+\s+([\d,\.\s]+)",
        ],
        text,
    )
    graduate_match = maybe_match(
        [
            r"Total of all graduate students enrolled\s+([\d,\.]+)",
            r"Total all graduate\s+([\d,\.\s]+)",
        ],
        text,
    )

    undergraduate = parse_int(undergraduate_match.group(1)) if undergraduate_match else 0
    graduate = parse_int(graduate_match.group(1)) if graduate_match else 0

    race_patterns = {
        "international": [
            r"(?:Nonresident aliens|International \(nonresidents\)|Nonresidents)\s+[\d,\.]+\s+[\d,\.]+\s+([\d,\.]+)"
        ],
        "hispanicLatino": [r"Hispanic/Latino\s+[\d,\.]+\s+[\d,\.]+\s+([\d,\.]+)"],
        "blackAfricanAmerican": [r"Black or African American, non-Hispanic\s+[\d,\.]+\s+[\d,\.]+\s+([\d,\.]+)"],
        "white": [r"White, non-Hispanic\s+[\d,\.]+\s+[\d,\.]+\s+([\d,\.]+)"],
        "asian": [r"Asian, non-Hispanic\s+[\d,\.]+\s+[\d,\.]+\s+([\d,\.]+)"],
        "americanIndianAlaskaNative": [
            r"American Indian or Alaska Native, non-Hispanic\s+[\d,\.]+\s+[\d,\.]+\s+([\d,\.]+)"
        ],
        "nativeHawaiianPacificIslander": [
            r"Native Hawaiian or other Pacific Islander, non-?\s*Hispanic\s+[\d,\.]+\s+[\d,\.]+\s+([\d,\.]+)"
        ],
        "twoOrMoreRaces": [r"Two or more races, non-Hispanic\s+[\d,\.]+\s+[\d,\.]+\s+([\d,\.]+)"],
        "unknown": [r"Race and/or ethnicity unknown\s+[\d,\.]+\s+[\d,\.]+\s+([\d,\.]+)"],
    }

    by_race = {}
    for key, patterns in race_patterns.items():
        match = maybe_match(patterns, text)
        by_race[key] = parse_int(match.group(1)) if match else 0

    out_state_match = re.search(
        r"Percent who are from out of state.*?(\d+(?:\.\d+)?)%?\s+(\d+(?:\.\d+)?)%",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    out_state_pct = parse_float(out_state_match.group(2)) if out_state_match else 0

    international = by_race["international"]
    domestic = max(undergraduate - international, 0)
    out_of_state = round(domestic * out_state_pct / 100)
    in_state = domestic - out_of_state

    return {
        "enrollment": {
            "total": undergraduate + graduate,
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


def extract_costs(text: str) -> dict:
    tuition_match = maybe_match(
        [
            r"In-state \(out-of-district\):\s*\$([\d,]+)",
            r"Tuition:\s*In-state \(out-of-district\):\s*\$([\d,]+)",
        ],
        text,
    )
    fees_match = maybe_match([r"(?:Required Fees|REQUIRED FEES):?\s*\$([\d,\s]+)"], text)
    room_match = maybe_match(
        [
            r"Food and housing \(on-campus\):\s*\$([\d,\s]+)",
            r"Room and Board \(on-campus\):\s*\$([\d,\s]+)",
            r"ROOM AND BOARD:\s*\(on-campus\)\s*\$([\d,\s]+)",
        ],
        text,
    )

    tuition = parse_int(tuition_match.group(1)) if tuition_match else 0
    fees = parse_int(fees_match.group(1)) if fees_match else 0
    room_and_board = parse_int(room_match.group(1)) if room_match else 0

    return {
        "tuition": tuition,
        "fees": fees,
        "roomAndBoard": room_and_board,
        "totalCOA": tuition + fees + room_and_board,
    }


def extract_financial_aid(year: str) -> dict:
    return MANUAL_FINANCIAL_AID[year]


def extract_pdf(pdf_path: Path, year: str) -> dict:
    with pdfplumber.open(str(pdf_path)) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    return {
        "admissions": extract_admissions(text),
        "testScores": extract_test_scores(text, year),
        "demographics": extract_demographics(text),
        "costs": extract_costs(text),
        "financialAid": extract_financial_aid(year),
    }


def main() -> None:
    school_data = {
        "name": "Georgia Institute of Technology",
        "slug": "georgiatech",
        "years": {},
    }

    for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
        year = year_from_name(pdf_path.name)
        school_data["years"][year] = extract_pdf(pdf_path, year)

    OUTPUT_PATH.write_text(json.dumps(school_data, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {OUTPUT_PATH}")
    for year, data in school_data["years"].items():
        print(
            f"{year}: {data['admissions']['applied']:,} applied, "
            f"{data['admissions']['admitted']:,} admitted, "
            f"{data['demographics']['enrollment']['undergraduate']:,} undergrads"
        )


if __name__ == "__main__":
    main()
