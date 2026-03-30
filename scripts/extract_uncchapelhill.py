#!/usr/bin/env python3
"""
UNC Chapel Hill CDS extractor.

Parses the PDFs in College-Data/UNC-Chapel-Hill and writes
src/data/schools/uncchapelhill.json.
"""

import json
import re
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber is required. Install with: pip install pdfplumber")
    sys.exit(1)


PDF_DIR = Path("College-Data/UNC-Chapel-Hill")
OUTPUT_PATH = Path("src/data/schools/uncchapelhill.json")
OVERRIDES = {
    "2016-2017": {
        "costs": {"tuition": 6881, "fees": 1953, "roomAndBoard": 11218, "totalCOA": 20052},
        "financialAid": {
            "percentReceivingAid": 0.4620,
            "averageAidPackage": 19310,
            "averageNeedBasedGrant": 17260,
            "percentNeedFullyMet": 0.7969,
        },
    },
    "2017-2018": {
        "demographics": {
            "byRace": {
                "nativeHawaiianPacificIslander": 12,
            },
        },
        "costs": {"tuition": 7019, "fees": 1967, "roomAndBoard": 11190, "totalCOA": 20176},
        "financialAid": {
            "percentReceivingAid": 0.4527,
            "averageAidPackage": 19626,
            "averageNeedBasedGrant": 17607,
            "percentNeedFullyMet": 0.8046,
        },
    },
    "2018-2019": {
        "costs": {"tuition": 7019, "fees": 2027, "roomAndBoard": 11526, "totalCOA": 20572},
        "financialAid": {
            "percentReceivingAid": 0.4639,
            "averageAidPackage": 20312,
            "averageNeedBasedGrant": 18410,
            "percentNeedFullyMet": 0.7572,
        },
    },
    "2023-2024": {
        "admissions": {
            "enrolled": 4699,
            "yield": 0.4330,
            "byGender": {
                "men": {"applied": 23947, "admitted": 4334, "enrolled": 1764},
                "women": {"applied": 33955, "admitted": 6518, "enrolled": 2935},
            },
        },
        "demographics": {
            "enrollment": {"total": 32496, "undergraduate": 20880, "graduate": 11616},
            "byRace": {
                "americanIndianAlaskaNative": 67,
                "nativeHawaiianPacificIslander": 8,
            },
        },
        "costs": {"tuition": 7020, "fees": 1990, "roomAndBoard": 13804, "totalCOA": 22814},
        "financialAid": {
            "percentReceivingAid": 0.3818,
            "averageAidPackage": 19660,
            "averageNeedBasedGrant": 17853,
            "percentNeedFullyMet": 0.6967,
        },
    },
    "2024-2025": {
        "demographics": {
            "byRace": {
                "nativeHawaiianPacificIslander": 9,
            },
        },
    },
}


def normalize_text(text: str) -> str:
    replacements = {
        "\r": "",
        "\u00a0": " ",
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\ufb01": "fi",
        "\ufb02": "fl",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def load_pdf_pages(pdf_path: Path) -> list[str]:
    with pdfplumber.open(pdf_path) as pdf:
        return [normalize_text(page.extract_text(layout=True) or "") for page in pdf.pages]


def extract_number(value: str) -> int:
    return int(value.replace(",", "").replace("$", "").replace(".00", "").strip())


def extract_year_from_filename(filename: str) -> str:
    match = re.search(r"(\d{4})[-_](\d{2,4})", filename)
    if not match:
        raise ValueError(f"Could not extract year from {filename}")

    start = int(match.group(1))
    end_raw = match.group(2)
    end = int(end_raw) if len(end_raw) == 4 else 2000 + int(end_raw)
    return f"{start}-{end}"


def first_page_with(pages: list[str], needles: list[str]) -> int:
    for idx, page in enumerate(pages):
        if all(needle.lower() in page.lower() for needle in needles):
            return idx
    return -1


def first_match(text: str, patterns: list[str]) -> int:
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return extract_number(match.group(1))
    return 0


def score_block(text: str, patterns: list[str]) -> dict:
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            nums = [int(group) for group in match.groups() if group]
            if len(nums) == 3:
                return {"p25": nums[0], "p50": nums[1], "p75": nums[2]}
            return {"p25": nums[0], "p50": (nums[0] + nums[1]) // 2, "p75": nums[1]}
    return {"p25": 0, "p50": 0, "p75": 0}


def extract_admissions(pages: list[str]) -> dict:
    idx = first_page_with(pages, ["first-time", "who applied"])
    text = pages[idx] if idx >= 0 else ""

    men_applied = first_match(text, [r"men who applied\s+([\d,]+)"])
    women_applied = first_match(text, [r"women who applied\s+([\d,]+)"])
    total_applied = first_match(
        text,
        [r"who applied\s+[\d,]+\s+[\d,]+(?:\s+[\d,]+)?\s+([\d,]+)"],
    )

    men_admitted = first_match(text, [r"men who were admitted\s+([\d,]+)"])
    women_admitted = first_match(text, [r"women who were admitted\s+([\d,]+)"])
    total_admitted = first_match(
        text,
        [r"who were admitted\s+[\d,]+\s+[\d,]+(?:\s+[\d,]+)?\s+([\d,]+)"],
    )

    men_enrolled = (
        first_match(text, [r"full-time, first-time, first-year(?: \(freshman\))? men who enrolled\s+([\d,]+)"])
        + first_match(text, [r"part-time, first-time, first-year(?: \(freshman\))? men who enrolled\s+([\d,]+)"])
    )
    women_enrolled = (
        first_match(text, [r"full-time, first-time, first-year(?: \(freshman\))? women who enrolled\s+([\d,]+)"])
        + first_match(text, [r"part-time, first-time, first-year(?: \(freshman\))? women who enrolled\s+([\d,]+)"])
    )

    if men_enrolled == 0:
        men_enrolled = (
            first_match(text, [r"Total full-time, first-time, first-year who enrolled\s+([\d,]+)\s+[\d,]+(?:\s+[\d,]+)?\s+[\d,]+"])
            + first_match(text, [r"Total part-time, first-time, first-year who enrolled\s+([\d,]+)\s+[\d,]+(?:\s+[\d,]+)?\s+[\d,]+"])
        )
    if women_enrolled == 0:
        women_enrolled = (
            first_match(text, [r"Total full-time, first-time, first-year who enrolled\s+[\d,]+\s+([\d,]+)(?:\s+[\d,]+)?\s+[\d,]+"])
            + first_match(text, [r"Total part-time, first-time, first-year who enrolled\s+[\d,]+\s+([\d,]+)(?:\s+[\d,]+)?\s+[\d,]+"])
        )

    total_enrolled = first_match(text, [r"Total Enrolled first-time, first-years\s+([\d,]+)"])
    if total_enrolled == 0:
        total_enrolled = first_match(
            text,
            [
                r"Total full-time, first-time, first-year(?: \(freshman\))? who enrolled\s+[\d,]+\s+[\d,]+(?:\s+[\d,]+)?\s+([\d,]+)",
                r"Total first-time, first-year \(degree seeking\) enrolled.*?([\d,]+)",
            ],
        ) + first_match(
            text,
            [r"Total part-time, first-time, first-year(?: \(freshman\))? who enrolled\s+[\d,]+\s+[\d,]+(?:\s+[\d,]+)?\s+([\d,]+)"],
        )
    if total_enrolled == 0:
        total_enrolled = men_enrolled + women_enrolled

    applied = total_applied or (men_applied + women_applied)
    admitted = total_admitted or (men_admitted + women_admitted)
    enrolled = total_enrolled

    return {
        "applied": applied,
        "admitted": admitted,
        "enrolled": enrolled,
        "acceptanceRate": round(admitted / applied, 4) if applied else 0,
        "yield": round(enrolled / admitted, 4) if admitted else 0,
        "byGender": {
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
        },
    }


def extract_test_scores(pages: list[str]) -> dict:
    idx = first_page_with(pages, ["Percent submitting SAT scores"])
    text = ""
    if idx >= 0:
        text = pages[idx]
        if idx + 1 < len(pages):
            text += "\n" + pages[idx + 1]

    sat_submission_match = re.search(r"Percent submitting SAT scores\s+(\d+(?:\.\d+)?)%", text, re.I)
    act_submission_match = re.search(r"Percent submitting ACT scores\s+(\d+(?:\.\d+)?)%", text, re.I)
    sat_submission = float(sat_submission_match.group(1)) / 100 if sat_submission_match else 0
    act_submission = float(act_submission_match.group(1)) / 100 if act_submission_match else 0

    sat = {
        "composite": score_block(
            text,
            [
                r"SAT Composite(?: \(.*?\))?\s+(\d{3,4})\s+(\d{3,4})\s+(\d{3,4})",
                r"SAT Composite(?: \(.*?\))?\s+(\d{3,4})\s+(\d{3,4})",
            ],
        ),
        "readingWriting": score_block(
            text,
            [
                r"SAT EBRW(?: \(.*?\))?\s+(\d{3})\s+(\d{3})\s+(\d{3})",
                r"SAT EBRW(?: \(.*?\))?\s+(\d{3})\s+(\d{3})",
                r"SAT Evidence-Based Reading and Writing\s+(\d{3})\s+(\d{3})\s+(\d{3})",
                r"SAT Evidence-Based Reading and Writing\s+(\d{3})\s+(\d{3})",
                r"SAT Critical Reading\s+(\d{3})\s+(\d{3})",
            ],
        ),
        "math": score_block(
            text,
            [
                r"SAT Math(?: \(.*?\))?\s+(\d{3})\s+(\d{3})\s+(\d{3})",
                r"SAT Math(?: \(.*?\))?\s+(\d{3})\s+(\d{3})",
            ],
        ),
        "submissionRate": sat_submission,
    }

    if sat["composite"]["p25"] == 0 and sat["readingWriting"]["p25"] and sat["math"]["p25"]:
        sat["composite"] = {
            "p25": sat["readingWriting"]["p25"] + sat["math"]["p25"],
            "p50": sat["readingWriting"]["p50"] + sat["math"]["p50"],
            "p75": sat["readingWriting"]["p75"] + sat["math"]["p75"],
        }

    act = {
        "composite": score_block(
            text,
            [
                r"ACT Composite(?: \(.*?\))?\s+(\d{2})\s+(\d{2})\s+(\d{2})",
                r"ACT Composite(?: \(.*?\))?\s+(\d{2})\s+(\d{2})",
            ],
        ),
        "submissionRate": act_submission,
    }

    data = {}
    if sat["readingWriting"]["p25"] and sat["math"]["p25"]:
        data["sat"] = sat
    if act["composite"]["p25"]:
        data["act"] = act
    return data


def extract_demographics(pages: list[str]) -> dict:
    b1_idx = first_page_with(pages, ["Total all undergraduates"])
    if b1_idx == -1:
        b1_idx = first_page_with(pages, ["Total of all undergraduate students enrolled"])
    b1_text = pages[b1_idx] if b1_idx >= 0 else ""

    b2_idx = first_page_with(pages, ["Hispanic/Latino", "White"])
    b2_text = pages[b2_idx] if b2_idx >= 0 else b1_text

    undergraduate = first_match(
        b1_text,
        [
            r"Total all undergraduates\s+([\d,]+)",
            r"Total of all undergraduate students enrolled\s+([\d,]+)",
        ],
    )
    graduate = first_match(
        b1_text,
        [
            r"Total all graduate\s+([\d,]+)",
            r"Total of all graduate students enrolled\s+([\d,]+)",
        ],
    )

    def row(patterns: list[str]) -> int:
        for pattern in patterns:
            match = re.search(pattern, b2_text, re.I | re.S)
            if match:
                return extract_number(match.group(3))
        return 0

    by_race = {
        "international": row(
            [
                r"Nonresident aliens\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)",
                r"Nonresidents\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)",
                r"International \(nonresidents\)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)",
            ]
        ),
        "hispanicLatino": row([r"Hispanic/Latino\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"]),
        "blackAfricanAmerican": row([r"Black or African American, non-Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"]),
        "white": row([r"White, non-Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"]),
        "asian": row([r"Asian, non-Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"]),
        "americanIndianAlaskaNative": row(
            [
                r"American Indian or Alaska Native, non-Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)",
                r"American Indian or Alaska Native, non-\s+Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)",
            ]
        ),
        "nativeHawaiianPacificIslander": row(
            [
                r"Native Hawaiian or other Pacific Islander, non-Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)",
                r"Native Hawaiian or other Pacific Islander,\s+non-Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)",
                r"Native Hawaiian or other Pacific Islander, non-\s+Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)",
            ]
        ),
        "twoOrMoreRaces": row([r"Two or more races, non-Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"]),
        "unknown": row([r"Race and/or ethnicity unknown\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"]),
    }

    f1_idx = first_page_with(pages, ["Percent who are from out of state"])
    f1_text = pages[f1_idx] if f1_idx >= 0 else ""
    out_pct_match = re.search(
        r"Percent who are from out of state.*?(\d+(?:\.\d+)?)%\s+(\d+(?:\.\d+)?)%",
        f1_text,
        re.I | re.S,
    )
    international = by_race["international"]
    domestic = undergraduate - international
    out_of_state = round(domestic * float(out_pct_match.group(2)) / 100) if out_pct_match else 0

    return {
        "enrollment": {
            "total": undergraduate + graduate,
            "undergraduate": undergraduate,
            "graduate": graduate,
        },
        "byRace": by_race,
        "byResidency": {
            "inState": domestic - out_of_state,
            "outOfState": out_of_state,
            "international": international,
        },
    }


def extract_costs(pages: list[str]) -> dict:
    idx = first_page_with(pages, ["out-of-district"])
    text = pages[idx] if idx >= 0 else ""

    tuition = first_match(
        text,
        [
            r"Tuition: \(In-state, out-of-district\)\s+\$([\d,]+(?:\.00)?)",
            r"In-state \(out-of-district\):\s+\$([\d,]+(?:\.00)?)",
        ],
    )
    fees = first_match(
        text,
        [
            r"Required Fees:?\s+\$([\d,]+(?:\.00)?)",
            r"REQUIRED FEES:\s+\$([\d,]+(?:\.00)?)",
        ],
    )
    room_and_board = first_match(
        text,
        [
            r"Food and Housing \(on-campus\):\s+\$([\d,]+(?:\.00)?)",
            r"Room & Board \(on-campus\)\s+\$([\d,]+(?:\.00)?)",
            r"ROOM AND BOARD:\s*\(on-campus\)\s+\$([\d,]+(?:\.00)?)",
        ],
    )

    return {
        "tuition": tuition,
        "fees": fees,
        "roomAndBoard": room_and_board,
        "totalCOA": tuition + fees + room_and_board,
    }


def extract_financial_aid(pages: list[str]) -> dict:
    idx = first_page_with(pages, ["Number of Enrolled Students Awarded Aid"])
    if idx == -1:
        idx = first_page_with(pages, ["Number of degree-seeking undergraduate students"])

    text = ""
    if idx >= 0:
        text = pages[idx]
        if idx + 1 < len(pages):
            text += "\n" + pages[idx + 1]

    def row(patterns: list[str]) -> list[int]:
        for pattern in patterns:
            match = re.search(pattern, text, re.I | re.S)
            if match:
                return [extract_number(group) for group in match.groups()]
        return []

    row_a = row(
        [
            r"[Aa][\)\.]?\s+Number of degree-seeking undergraduate students.*?([\d,]+)\s+([\d,]+)\s+([\d,]+)",
            r"H2 a\).*?([\d,]+)\s+([\d,]+)\s+([\d,]+)",
            r"Number of degree-seeking undergraduate students.*?([\d,]+)\s+([\d,]+)\s+([\d,]+)",
        ]
    )
    row_d = row(
        [
            r"[Dd][\)\.]?\s+Number of students in line c who were awarded any financial aid.*?([\d,]+)\s+([\d,]+)\s+([\d,]+)",
            r"H2 d\).*?([\d,]+)\s+([\d,]+)\s+([\d,]+)",
            r"Number of students in line c who were awarded any financial aid.*?([\d,]+)\s+([\d,]+)\s+([\d,]+)",
        ]
    )
    row_h = row(
        [
            r"[Hh][\)\.]?\s+Number of students in line d whose need was fully met.*?([\d,]+)\s+([\d,]+)\s+([\d,]+)",
            r"H2 h\).*?([\d,]+)\s+([\d,]+)\s+([\d,]+)",
            r"Number of students in line d whose need was fully met.*?([\d,]+)\s+([\d,]+)\s+([\d,]+)",
        ]
    )
    row_j = row(
        [
            r"[Jj][\)\.]?\s+The average financial aid package of those in line d.*?\$([\d,]+)\s+\$([\d,]+)\s+\$([\d,]+)",
            r"H2 j\).*?\$([\d,]+)\s+\$([\d,]+)\s+\$([\d,]+)",
            r"The average financial aid package of those in line d.*?\$([\d,]+)\s+\$([\d,]+)\s+\$([\d,]+)",
        ]
    )
    row_k = row(
        [
            r"[Kk][\)\.]?\s+Average need-based scholarship and grant award of those in line e.*?\$([\d,]+)\s+\$([\d,]+)\s+\$([\d,]+)",
            r"H2 k\).*?\$([\d,]+)\s+\$([\d,]+)\s+\$([\d,]+)",
            r"Average need-based scholarship and grant award of those in line e.*?\$([\d,]+)\s+\$([\d,]+)\s+\$([\d,]+)",
        ]
    )

    students = row_a[1] if len(row_a) >= 2 else 0
    awarded = row_d[1] if len(row_d) >= 2 else 0
    fully_met = row_h[1] if len(row_h) >= 2 else 0

    return {
        "percentReceivingAid": round(awarded / students, 4) if students else 0,
        "averageAidPackage": row_j[1] if len(row_j) >= 2 else 0,
        "averageNeedBasedGrant": row_k[1] if len(row_k) >= 2 else 0,
        "percentNeedFullyMet": round(fully_met / awarded, 4) if awarded else 0,
    }


def extract_year_data(pages: list[str]) -> dict:
    return {
        "admissions": extract_admissions(pages),
        "testScores": extract_test_scores(pages),
        "demographics": extract_demographics(pages),
        "costs": extract_costs(pages),
        "financialAid": extract_financial_aid(pages),
    }


def deep_update(target: dict, patch: dict) -> None:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_update(target[key], value)
        else:
            target[key] = value


def main() -> None:
    school_data = {
        "name": "University of North Carolina at Chapel Hill",
        "slug": "uncchapelhill",
        "years": {},
    }

    for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
        year = extract_year_from_filename(pdf_path.name)
        pages = load_pdf_pages(pdf_path)
        school_data["years"][year] = extract_year_data(pages)
        if year in OVERRIDES:
            deep_update(school_data["years"][year], OVERRIDES[year])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(school_data, f, indent=2)
        f.write("\n")

    for year, year_data in school_data["years"].items():
        admissions = year_data["admissions"]
        print(
            f"{year}: {admissions['applied']:,} applied, {admissions['admitted']:,} admitted, "
            f"{admissions['enrolled']:,} enrolled"
        )

    print(f"\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
