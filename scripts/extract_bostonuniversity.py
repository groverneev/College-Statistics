#!/usr/bin/env python3
"""
Boston University CDS extractor.

Uses the local Boston University CDS PDFs and targeted parsing for BU's
recurring PDF layout.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber is required. Install with: pip install pdfplumber")
    sys.exit(1)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "College-Data" / "BostonUniversity"
OUTPUT_PATH = ROOT / "src" / "data" / "schools" / "bostonuniversity.json"


def extract_number(value: str) -> int:
    cleaned = re.sub(r"[^\d]", "", value or "")
    return int(cleaned) if cleaned else 0


def extract_percent(value: str) -> float:
    return round(extract_number(value) / 100, 4)


def normalize_text(text: str) -> str:
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    text = re.sub(r"(\d)\s+,", r"\1,", text)
    return text


def squish(text: str) -> str:
    return re.sub(r"\s+", " ", normalize_text(text)).strip()


def extract_pdf_text(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return normalize_text("\n".join(page.extract_text() or "" for page in pdf.pages))


def get_section(text: str, start: str, end: str) -> str:
    start_idx = text.find(start)
    if start_idx == -1:
        return ""
    end_idx = text.find(end, start_idx + len(start))
    if end_idx == -1:
        return text[start_idx:]
    return text[start_idx:end_idx]


def extract_score_triplet(flat_text: str, patterns: list[str]) -> tuple[int, int, int]:
    for pattern in patterns:
        match = re.search(pattern, flat_text, re.IGNORECASE)
        if not match:
            continue
        groups = tuple(int(value) for value in match.groups())
        if len(groups) == 3:
            return groups
        if len(groups) == 2:
            p25, p75 = groups
            return p25, (p25 + p75) // 2, p75
    return 0, 0, 0


def parse_admissions(text: str) -> dict:
    c1 = get_section(text, "C1.", "C2.")
    c21 = get_section(text, "C21.", "C22.")
    lines = [line.strip() for line in c1.splitlines() if line.strip()]

    def parse_total_row(prefixes: tuple[str, ...]) -> int:
        for line in lines:
            lowered = line.lower()
            if not any(lowered.startswith(prefix) for prefix in prefixes):
                continue
            values = [extract_number(value) for value in re.findall(r"[\d,]+", line)]
            if not values:
                continue
            if len(values) >= 2 and values[-1] == sum(values[:-1]):
                return values[-1]
            return sum(values)
        return 0

    applied = parse_total_row(("applicants", "applied"))
    admitted = parse_total_row(("offered admission", "admitted"))
    enrolled = parse_total_row(("full-time enrolled",))

    early_decision_applied = 0
    early_decision_admitted = 0
    c21_flat = squish(c21)
    match = re.search(
        r"Number of early decision applications received(?: by your institution)?\s+([\d,]+)",
        c21_flat,
        re.IGNORECASE,
    )
    if match:
        early_decision_applied = extract_number(match.group(1))
    match = re.search(
        r"Number of applicants admitted under early decision plan\s+([\d,]+)",
        c21_flat,
        re.IGNORECASE,
    )
    if match:
        early_decision_admitted = extract_number(match.group(1))

    data = {
        "applied": applied,
        "admitted": admitted,
        "enrolled": enrolled,
        "acceptanceRate": round(admitted / applied, 4) if applied else 0,
        "yield": round(enrolled / admitted, 4) if admitted else 0,
    }
    if early_decision_applied and early_decision_admitted:
        data["earlyDecision"] = {
            "applied": early_decision_applied,
            "admitted": early_decision_admitted,
        }
    return data


def parse_test_scores(text: str) -> dict:
    c9_flat = squish(get_section(text, "C9.", "C10."))

    sat_submission = 0.0
    act_submission = 0.0

    match = re.search(r"SAT I\s+(\d{1,3})%", c9_flat, re.IGNORECASE)
    if match:
        sat_submission = extract_percent(match.group(1))

    match = re.search(r"\bACT\s+(\d{1,3})%\s+[\d,]+", c9_flat, re.IGNORECASE)
    if match:
        act_submission = extract_percent(match.group(1))

    rw = extract_score_triplet(
        c9_flat,
        [
            r"(?:SAT\s+)?(?:Evidence-Based\s+)?Reading and Writing\s+(\d{3})\s+(\d{3})\s+(\d{3})",
            r"(?:SAT\s+)?(?:Evidence-Based\s+)?Reading and Writing\s+(\d{3})-(\d{3})",
            r"SAT Critical Reading\s+(\d{3})-(\d{3})",
        ],
    )
    math = extract_score_triplet(
        c9_flat,
        [
            r"SAT Math\s+(\d{3})\s+(\d{3})\s+(\d{3})",
            r"SAT Math\s+(\d{3})-(\d{3})",
        ],
    )
    sat_composite = extract_score_triplet(
        c9_flat,
        [
            r"SAT Composite\s+(\d{4})\s+(\d{4})\s+(\d{4})",
            r"SAT Composite\s+(\d{4})-(\d{4})",
        ],
    )
    act_composite = extract_score_triplet(
        c9_flat,
        [
            r"ACT Composite\s+(\d{2})\s+(\d{2})\s+(\d{2})",
            r"ACT Composite\s+(\d{2})-(\d{2})",
        ],
    )

    data: dict = {}

    if any(rw) and any(math):
        if not any(sat_composite):
            sat_composite = (
                rw[0] + math[0],
                rw[1] + math[1],
                rw[2] + math[2],
            )
        data["sat"] = {
            "composite": {"p25": sat_composite[0], "p50": sat_composite[1], "p75": sat_composite[2]},
            "readingWriting": {"p25": rw[0], "p50": rw[1], "p75": rw[2]},
            "math": {"p25": math[0], "p50": math[1], "p75": math[2]},
            "submissionRate": sat_submission,
        }

    if any(act_composite):
        data["act"] = {
            "composite": {"p25": act_composite[0], "p50": act_composite[1], "p75": act_composite[2]},
            "submissionRate": act_submission,
        }

    return data


def parse_demographics(text: str) -> dict:
    b1_flat = squish(get_section(text, "B1.", "B2."))
    b2_flat = squish(get_section(text, "B2.", "B3."))
    f1_flat = squish(get_section(text, "F1.", "F2."))

    undergraduate = 0
    graduate = 0

    match = re.search(r"Total undergraduate enrollment\s+([\d,]+)", b1_flat, re.IGNORECASE)
    if match:
        undergraduate = extract_number(match.group(1))
    match = re.search(
        r"Total graduate and professional enrollment\s+([\d,]+)",
        b1_flat,
        re.IGNORECASE,
    )
    if match:
        graduate = extract_number(match.group(1))

    row_patterns = {
        "international": [r"Non-resident aliens\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"],
        "hispanicLatino": [r"Hispanic(?:/Latino)?\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"],
        "blackAfricanAmerican": [r"Black, non-Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"],
        "white": [r"White, non-Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"],
        "asian": [r"Asian, non-Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"],
        "americanIndianAlaskaNative": [r"American Indian/Alaskan Native\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"],
        "nativeHawaiianPacificIslander": [r"Hawaiian/Pacific Islander\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"],
        "twoOrMoreRaces": [r"Two or More Races, non-Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"],
        "unknown": [r"Race/ethnicity unknown\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"],
    }

    by_race = {key: 0 for key in row_patterns}
    for key, patterns in row_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, b2_flat, re.IGNORECASE)
            if match:
                by_race[key] = extract_number(match.group(3))
                break

    out_pct = 0
    match = re.search(r"From out-of-state\s+(\d{1,3})%\s+(\d{1,3})%", f1_flat, re.IGNORECASE)
    if match:
        out_pct = extract_number(match.group(2))

    domestic = max(undergraduate - by_race["international"], 0)
    out_of_state = int(round(domestic * out_pct / 100))
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
            "international": by_race["international"],
        },
    }


def parse_costs(text: str) -> dict:
    g1_flat = squish(get_section(text, "G1.", "G2."))

    tuition = 0
    fees = 0
    room_and_board = 0

    match = re.search(r"Full-time tuition\s+\$([\d,]+)", g1_flat, re.IGNORECASE)
    if match:
        tuition = extract_number(match.group(1))

    match = re.search(r"Full-time mandatory fees\s+\$([\d,]+)", g1_flat, re.IGNORECASE)
    if match:
        fees = extract_number(match.group(1))

    match = re.search(r"Room\s*&\s*board.*?\$([\d,]+)", g1_flat, re.IGNORECASE)
    if match:
        room_and_board = extract_number(match.group(1))

    return {
        "tuition": tuition,
        "fees": fees,
        "roomAndBoard": room_and_board,
        "totalCOA": tuition + fees + room_and_board,
    }


def parse_financial_aid(text: str) -> dict:
    h2_flat = squish(get_section(text, "H2.", "H2A."))

    def parse_row(pattern: str) -> tuple[int, int, int]:
        match = re.search(pattern, h2_flat, re.IGNORECASE)
        if not match:
            return 0, 0, 0
        return tuple(extract_number(value) for value in match.groups())

    row_a = parse_row(r"\(a\)\s+Number of degree seeking students\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)")
    row_d = parse_row(r"\(d\)\s+Number in \"c\" who received any aid\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)")
    row_h = parse_row(r"\(h\)\s+Number in \"d\" whose need was fully met\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)")
    row_j = parse_row(r"\(j\)\s+Average package \(up to need\) for those in \"d\"\s+\$?([\d,]+)\s+\$?([\d,]+)\s+\$?([\d,]+)")
    row_k = parse_row(r"\(k\)\s+Average need-based gift for those in \"e\"\s+\$?([\d,]+)\s+\$?([\d,]+)\s+\$?([\d,]+)")

    total_students = row_a[1]
    students_with_aid = row_d[1]
    fully_met = row_h[1]

    return {
        "percentReceivingAid": round(students_with_aid / total_students, 4) if total_students else 0,
        "averageAidPackage": row_j[1],
        "averageNeedBasedGrant": row_k[1],
        "percentNeedFullyMet": round(fully_met / students_with_aid, 4) if students_with_aid else 0,
    }


def filename_to_year(filename: str) -> str:
    match = re.search(r"(\d{4})", filename)
    if not match:
        raise ValueError(f"Could not extract year from {filename}")
    end_year = int(match.group(1))
    return f"{end_year - 1}-{end_year}"


def extract_year_data(pdf_path: Path) -> dict:
    text = extract_pdf_text(pdf_path)
    return {
        "admissions": parse_admissions(text),
        "testScores": parse_test_scores(text),
        "demographics": parse_demographics(text),
        "costs": parse_costs(text),
        "financialAid": parse_financial_aid(text),
    }


def validate_year(year: str, data: dict) -> None:
    enrollment = data["demographics"]["enrollment"]
    by_race = data["demographics"]["byRace"]
    by_residency = data["demographics"]["byResidency"]

    assert enrollment["total"] == enrollment["undergraduate"] + enrollment["graduate"], year
    assert sum(by_race.values()) == enrollment["undergraduate"], year
    assert sum(by_residency.values()) == enrollment["undergraduate"], year
    assert data["admissions"]["acceptanceRate"] == round(
        data["admissions"]["admitted"] / data["admissions"]["applied"], 4
    ), year


def main() -> None:
    school_data = {
        "name": "Boston University",
        "slug": "bostonuniversity",
        "years": {},
    }

    for pdf_path in sorted(SOURCE_DIR.glob("*.pdf")):
        year = filename_to_year(pdf_path.name)
        year_data = extract_year_data(pdf_path)
        validate_year(year, year_data)
        school_data["years"][year] = year_data

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(school_data, file, indent=2)

    for year in sorted(school_data["years"]):
        admissions = school_data["years"][year]["admissions"]
        sat = school_data["years"][year]["testScores"].get("sat")
        sat_range = (
            f"{sat['composite']['p25']}-{sat['composite']['p75']}"
            if sat
            else "n/a"
        )
        print(
            f"{year}: applied={admissions['applied']:,}, admitted={admissions['admitted']:,}, "
            f"enrolled={admissions['enrolled']:,}, rate={admissions['acceptanceRate']:.1%}, "
            f"sat={sat_range}"
        )


if __name__ == "__main__":
    main()
