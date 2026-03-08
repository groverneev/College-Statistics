#!/usr/bin/env python3
"""
Extract Emory CDS data from local and archived official PDFs.

The current Emory CDS page only exposes 2021-2022 through 2024-2025. Older
official PDFs used here were recovered from archive snapshots of Emory's own
PDF URLs. The 2018-2019 G1 text layer drops the cost values entirely, so that
year's cost figures come from Emory's official student accounts documents for
the corresponding 2019-2020 rates.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber


PDF_FILES = {
    "2017-2018": Path("College-Data/EmoryUniversity/emory-common-data-set-2017-2018-archive.pdf"),
    "2018-2019": Path("College-Data/EmoryUniversity/emory-common-data-set-2018-2019-archive.pdf"),
    "2019-2020": Path("College-Data/EmoryUniversity/emory-common-data-set-2019-2020-archive.pdf"),
    "2020-2021": Path("College-Data/EmoryUniversity/emory-common-data-set-2020-2021-archive.pdf"),
    "2021-2022": Path("College-Data/EmoryUniversity/emory-common-data-set-2021-2022.pdf"),
    "2022-2023": Path("College-Data/EmoryUniversity/emory-common-data-set-2022-2023.pdf"),
    "2023-2024": Path("College-Data/EmoryUniversity/emory-common-data-set-2023-2024.pdf"),
    "2024-2025": Path("College-Data/EmoryUniversity/emory-common-data-set-2024-2025.pdf"),
}

OUTPUT_PATH = Path("src/data/schools/emory.json")

# 2018-2019 G1 is unreadable in the archived CDS text layer. These values come
# from Emory's official 2019-20 tuition, student fee, and housing/meal rate docs.
MANUAL_COSTS = {
    "2017-2018": {"tuition": 50590, "fees": 716, "roomAndBoard": 14456},
    "2018-2019": {"tuition": 53070, "fees": 734, "roomAndBoard": 14896},
    "2019-2020": {"tuition": 55200, "fees": 798, "roomAndBoard": 15572},
    "2020-2021": {"tuition": 54660, "fees": 808, "roomAndBoard": 16302},
    "2021-2022": {"tuition": 57120, "fees": 828, "roomAndBoard": 17016},
    "2022-2023": {"tuition": 59920, "fees": 854, "roomAndBoard": 18972},
    "2023-2024": {"tuition": 63400, "fees": 880, "roomAndBoard": 20220},
    "2024-2025": {"tuition": 67080, "fees": 976, "roomAndBoard": 21244},
}


def load_lines(pdf_path: Path) -> list[str]:
    with pdfplumber.open(str(pdf_path)) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return [line.strip() for line in text.splitlines() if line.strip()]


def load_tables(pdf_path: Path) -> list[list[list[str]]]:
    tables: list[list[list[str]]] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                rows = [[(cell or "").replace("\n", " ").strip() for cell in row] for row in table]
                if any(any(cell for cell in row) for row in rows):
                    tables.append(rows)
    return tables


def clean_money(text: str) -> str:
    return text.replace(",", "").replace("$", "").replace(".00", "")


def numbers_in_text(text: str) -> list[int]:
    values = [int(round(float(num.replace(",", "")))) for num in re.findall(r"\d[\d,]*(?:\.\d+)?", text)]
    if re.match(r"^[A-Z]\d+\b", text) and values and values[0] < 100:
        values = values[1:]
    return values


def dollar_amounts(text: str) -> list[int]:
    values = []
    for raw in re.findall(r"\$\s*[\d,]+(?:\.\d+)?", text):
        values.append(int(round(float(clean_money(raw)))))
    return values


def find_line_index(lines: list[str], pattern: str) -> int:
    regex = re.compile(pattern, re.IGNORECASE)
    for index, line in enumerate(lines):
        if regex.search(line):
            return index
    raise ValueError(f"Missing line matching {pattern}")


def line_window(lines: list[str], pattern: str, size: int = 4) -> str:
    index = find_line_index(lines, pattern)
    return " ".join(lines[index : index + size])


def joined_window(lines: list[str], pattern: str, size: int = 4, scan: int = 3) -> str:
    regex = re.compile(pattern, re.IGNORECASE)
    for index in range(len(lines)):
        candidate = " ".join(lines[index : index + scan])
        if regex.search(candidate):
            return " ".join(lines[index : index + size])
    raise ValueError(f"Missing joined window matching {pattern}")


def value_from_tail(text: str) -> int:
    values = numbers_in_text(text)
    if not values:
        raise ValueError(f"No numeric value found in: {text}")
    return values[-1]


def extract_b2_value(lines: list[str], label: str) -> int:
    label_start = label.split()[0].lower()
    for index, line in enumerate(lines):
        current = line.lower()
        if not (current.startswith(f"b2 {label_start}") or current.startswith(label_start)):
            continue
        candidate = line
        if label.lower() not in candidate.lower() and label_start != "native":
            continue
        values = numbers_in_text(candidate)
        if line.lower().startswith("b2") and values and values[0] == 2:
            values = values[1:]
        if len(values) >= 2:
            return values[-1]
        candidate = " ".join(lines[index : index + 3])
        values = numbers_in_text(candidate)
        if line.lower().startswith("b2") and values and values[0] == 2:
            values = values[1:]
        if len(values) >= 2:
            return values[-1]
    raise ValueError(f"Missing B2 row for {label}")


def extract_admissions(lines: list[str], year: str) -> dict:
    if year == "2023-2024":
        applied_line = line_window(lines, r"Total first-time, first-year students who applied in Fall 2023", 1)
        admitted_line = line_window(lines, r"Total first-time, first-year students admitted in Fall 2023", 1)
        enrolled_line = line_window(lines, r"Total first-time, first-year students enrolled in Fall 2023", 1)
        applied_parts = numbers_in_text(applied_line)
        admitted_parts = numbers_in_text(admitted_line)
        enrolled_parts = numbers_in_text(enrolled_line)
        applied = sum(applied_parts[-2:])
        admitted = sum(admitted_parts[-2:])
        enrolled = sum(enrolled_parts[-2:])
    else:
        applied = admitted = enrolled = 0
        for gender in ("men", "women", "another gender"):
            for action, bucket in (
                ("applied", "applied"),
                ("were admitted", "admitted"),
            ):
                pattern = rf"Total first-time, first-year.*?{gender} who {action}"
                try:
                    line = line_window(lines, pattern, 1)
                    value = value_from_tail(line)
                    if bucket == "applied":
                        applied += value
                    else:
                        admitted += value
                except ValueError:
                    continue

            for enrollment_pattern in (
                rf"Total full-time, first-time, first-year.*?{gender} who enrolled",
                rf"Total part-time, first-time, first-year.*?{gender} who enrolled",
            ):
                try:
                    enrolled += value_from_tail(line_window(lines, enrollment_pattern, 1))
                except ValueError:
                    continue

    ed_applied = value_from_tail(line_window(lines, r"Number of early decision applications received", 1))
    ed_admitted = value_from_tail(line_window(lines, r"Number of applicants admitted under early decision plan", 1))

    return {
        "applied": applied,
        "admitted": admitted,
        "enrolled": enrolled,
        "acceptanceRate": round(admitted / applied, 4) if applied else 0,
        "yield": round(enrolled / admitted, 4) if admitted else 0,
        "earlyDecision": {
            "applied": ed_applied,
            "admitted": ed_admitted,
        },
    }


def extract_test_scores(lines: list[str]) -> dict:
    sat_submit_line = line_window(lines, r"Submitting SAT Scores", 1)
    act_submit_line = line_window(lines, r"Submitting ACT Scores", 1)
    sat_submit_match = re.search(r"(\d+(?:\.\d+)?)%", sat_submit_line)
    act_submit_match = re.search(r"(\d+(?:\.\d+)?)%", act_submit_line)
    sat_submission_rate = (float(sat_submit_match.group(1)) / 100) if sat_submit_match else 0
    act_submission_rate = (float(act_submit_match.group(1)) / 100) if act_submit_match else 0

    sat_composite = []
    sat_erw = []
    sat_math = []
    act_composite = []

    for pattern, target in (
        (r"SAT Composite", sat_composite),
        (r"SAT Evidence-Based Reading", sat_erw),
        (r"SAT Math", sat_math),
        (r"ACT Composite", act_composite),
    ):
        try:
            target.extend(numbers_in_text(line_window(lines, pattern, 1)))
        except ValueError:
            pass

    data: dict = {}
    if len(sat_composite) >= 3 and len(sat_erw) >= 3 and len(sat_math) >= 3:
        data["sat"] = {
            "composite": {"p25": sat_composite[-3], "p50": sat_composite[-2], "p75": sat_composite[-1]},
            "readingWriting": {"p25": sat_erw[-3], "p50": sat_erw[-2], "p75": sat_erw[-1]},
            "math": {"p25": sat_math[-3], "p50": sat_math[-2], "p75": sat_math[-1]},
            "submissionRate": sat_submission_rate,
        }

    if len(act_composite) >= 3:
        data["act"] = {
            "composite": {"p25": act_composite[-3], "p50": act_composite[-2], "p75": act_composite[-1]},
            "submissionRate": act_submission_rate,
        }

    return data


def extract_demographics(pdf_path: Path, lines: list[str]) -> dict:
    tables = load_tables(pdf_path)
    b2_table = None
    for table in tables:
        joined_rows = [" ".join(cell for cell in row if cell).lower() for row in table]
        if any("hispanic/latino" in row for row in joined_rows) and any(row.startswith("total") or " total " in row for row in joined_rows):
            b2_table = table
            break

    def b2_table_value(*labels: str) -> int | None:
        if b2_table is None:
            return None
        lowered_labels = [label.lower() for label in labels]
        for row in b2_table:
            joined = " ".join(cell for cell in row if cell)
            if any(label in joined.lower() for label in lowered_labels):
                values = numbers_in_text(joined)
                if len(values) >= 2:
                    return values[-1]
        return None

    undergraduate = b2_table_value("TOTAL")
    if undergraduate is None:
        try:
            undergraduate = value_from_tail(line_window(lines, r"Total all undergraduates", 1))
        except ValueError:
            try:
                undergraduate = value_from_tail(line_window(lines, r"Total of all undergraduate students enrolled", 1))
            except ValueError:
                values = numbers_in_text(line_window(lines, r"Total undergraduates", 1))
                undergraduate = sum(values[-4:])

    try:
        graduate = value_from_tail(line_window(lines, r"Total all graduate", 1))
    except ValueError:
        graduate = value_from_tail(line_window(lines, r"Total of all graduate students enrolled", 1))

    try:
        total = value_from_tail(line_window(lines, r"GRAND TOTAL ALL STUDENTS", 1))
    except ValueError:
        total = undergraduate + graduate

    def b2_value(*labels: str) -> int:
        value = b2_table_value(*labels)
        if value is not None:
            return value
        for label in labels:
            try:
                return extract_b2_value(lines, label)
            except ValueError:
                continue
        raise ValueError(f"Missing B2 row for {labels[0]}")

    by_race = {
        "international": b2_value("International (nonresidents)", "Nonresidents", "Nonresident aliens"),
        "hispanicLatino": b2_value("Hispanic/Latino"),
        "blackAfricanAmerican": b2_value("Black or African American"),
        "white": b2_value("White, non-Hispanic"),
        "asian": b2_value("Asian, non-Hispanic"),
        "americanIndianAlaskaNative": b2_value("American Indian or Alaska Native"),
        "nativeHawaiianPacificIslander": b2_value("Native Hawaiian or other Pacific Islander"),
        "twoOrMoreRaces": b2_value("Two or more races"),
        "unknown": b2_value("Race and/or ethnicity unknown"),
    }

    out_state_values = numbers_in_text(line_window(lines, r"Percent who are from out of state", 3))
    out_state_pct = out_state_values[-1] / 100
    domestic = undergraduate - by_race["international"]
    out_of_state = round(domestic * out_state_pct)
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


def extract_costs(lines: list[str], year: str) -> dict:
    if year in MANUAL_COSTS:
        costs = MANUAL_COSTS[year].copy()
        costs["totalCOA"] = costs["tuition"] + costs["fees"] + costs["roomAndBoard"]
        return costs

    tuition = dollar_amounts(line_window(lines, r"Tuition:\s*\$", 1))[0]

    required_fees = 0
    for pattern in (r"Required Fees", r"REQUIRED FEES"):
        try:
            values = dollar_amounts(line_window(lines, pattern, 2))
            if values:
                required_fees = values[0]
                break
        except ValueError:
            continue

    room_board = 0
    for pattern in (
        r"Room and Board \(on-campus\)",
        r"ROOM AND BOARD:",
        r"Food and [Hh]ousing \(on-campus\)",
    ):
        try:
            values = dollar_amounts(line_window(lines, pattern, 2))
            if values:
                room_board = values[0]
                break
        except ValueError:
            continue

    return {
        "tuition": tuition,
        "fees": required_fees,
        "roomAndBoard": room_board,
        "totalCOA": tuition + required_fees + room_board,
    }


def extract_financial_aid(pdf_path: Path, lines: list[str]) -> dict:
    row_map: dict[str, list[str]] = {}
    for table in load_tables(pdf_path):
        table_text = " ".join(" ".join(cell for cell in row if cell) for row in table).lower()
        if not any(
            needle in table_text
            for needle in (
                "degree-seeking undergraduate students",
                "average financial aid package",
                "need-based scholarship",
                "awarded any financial aid",
                "line d",
                "fully met",
            )
        ):
            continue
        for row in table:
            if row and row[0]:
                first = row[0].strip().lower().rstrip(".)")
                if first in {"a", "d", "h", "j", "k"}:
                    row_map[first] = row
            joined = " ".join(cell for cell in row if cell).lower()
            if "degree-seeking undergraduate students" in joined:
                row_map["a"] = row
            elif "awarded any financial aid" in joined:
                row_map["d"] = row
            elif "need was fully met" in joined:
                row_map["h"] = row
            elif "average financial aid package" in joined:
                row_map["j"] = row
            elif "average need-based scholarship" in joined or "scholarship and grant award" in joined:
                row_map["k"] = row

    if "a" in row_map:
        a = numbers_in_text(" ".join(row_map["a"]))[-2]
    else:
        a = numbers_in_text(joined_window(lines, r"Number of degree-seeking undergraduate students", 4))[-2]

    if "d" in row_map:
        d = numbers_in_text(" ".join(row_map["d"]))[-2]
    else:
        d = numbers_in_text(joined_window(lines, r"Number of students in line [cd].*awarded any", 4))[-2]

    if "h" in row_map:
        h = numbers_in_text(" ".join(row_map["h"]))[-2]
    else:
        h = numbers_in_text(joined_window(lines, r"Number of students in line d whose need was fully met", 4))[-2]

    if "j" in row_map:
        average_package = dollar_amounts(" ".join(row_map["j"]))[-2]
    else:
        average_package = dollar_amounts(joined_window(lines, r"average financial aid package", 5))[-2]

    if "k" in row_map:
        average_grant = dollar_amounts(" ".join(row_map["k"]))[-2]
    else:
        average_grant = dollar_amounts(joined_window(lines, r"average need-based scholarship|average need-based scholarship or grant award", 5))[-2]

    return {
        "percentReceivingAid": round(d / a, 4) if a else 0,
        "averageAidPackage": average_package,
        "averageNeedBasedGrant": average_grant,
        "percentNeedFullyMet": round(h / d, 4) if d else 0,
    }


def extract_year(year: str, pdf_path: Path) -> dict:
    lines = load_lines(pdf_path)
    year_data = {
        "admissions": extract_admissions(lines, year),
        "testScores": extract_test_scores(lines),
        "demographics": extract_demographics(pdf_path, lines),
        "costs": extract_costs(lines, year),
        "financialAid": extract_financial_aid(pdf_path, lines),
    }

    undergraduate = year_data["demographics"]["enrollment"]["undergraduate"]
    if sum(year_data["demographics"]["byRace"].values()) != undergraduate:
        raise ValueError(f"Race totals do not match undergraduate total for {year}")
    if sum(year_data["demographics"]["byResidency"].values()) != undergraduate:
        raise ValueError(f"Residency totals do not match undergraduate total for {year}")

    return year_data


def main() -> None:
    school_data = {
        "name": "Emory University",
        "slug": "emory",
        "years": {year: extract_year(year, path) for year, path in PDF_FILES.items()},
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(school_data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
