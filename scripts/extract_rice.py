#!/usr/bin/env python3
"""
Extract Rice University CDS data from the official Rice PDF archive.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber


PDF_FILES = {
    "2016-2017": Path("College-Data/RiceUniversity/rice-2016-2017.pdf"),
    "2017-2018": Path("College-Data/RiceUniversity/rice-2017-2018.pdf"),
    "2018-2019": Path("College-Data/RiceUniversity/rice-2018-2019.pdf"),
    "2019-2020": Path("College-Data/RiceUniversity/rice-2019-2020.pdf"),
    "2020-2021": Path("College-Data/RiceUniversity/rice-2020-2021.pdf"),
    "2021-2022": Path("College-Data/RiceUniversity/rice-2021-2022.pdf"),
    "2022-2023": Path("College-Data/RiceUniversity/rice-2022-2023.pdf"),
    "2023-2024": Path("College-Data/RiceUniversity/rice-2023-2024.pdf"),
    "2024-2025": Path("College-Data/RiceUniversity/rice-2024-2025.pdf"),
}

OUTPUT_PATH = Path("src/data/schools/rice.json")


def load_lines(pdf_path: Path) -> list[str]:
    with pdfplumber.open(str(pdf_path)) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return [line.strip() for line in text.splitlines() if line.strip()]


def numbers_in_text(text: str) -> list[int]:
    values = []
    for raw in re.findall(r"\d[\d,]*(?:\.\d+)?", text):
        cleaned = raw.replace(",", "")
        values.append(int(round(float(cleaned))))
    if re.match(r"^[A-Z]\d+\b", text.strip()) and values and values[0] < 100:
        values = values[1:]
    return values


def percents_in_text(text: str) -> list[float]:
    return [float(raw) for raw in re.findall(r"(\d+(?:\.\d+)?)%", text)]


def dollar_amounts(text: str) -> list[int]:
    return [int(round(float(raw.replace(",", "")))) for raw in re.findall(r"\$ ?([\d,]+(?:\.\d+)?)", text)]


def normalize(text: str) -> str:
    return (
        text.lower()
        .replace("‐", "-")
        .replace("–", "-")
        .replace("—", "-")
        .replace("‑", "-")
        .replace("freshmen", "first-year")
    )


def find_line_index(lines: list[str], pattern: str) -> int:
    regex = re.compile(pattern, re.IGNORECASE)
    for index, line in enumerate(lines):
        if regex.search(line):
            return index
    raise ValueError(f"Missing line matching {pattern}")


def find_joined_index(lines: list[str], pattern: str, scan: int = 3) -> int:
    regex = re.compile(pattern, re.IGNORECASE)
    for index in range(len(lines)):
        joined = " ".join(lines[index : index + scan])
        if regex.search(joined):
            return index
    raise ValueError(f"Missing joined text matching {pattern}")


def line_window(lines: list[str], pattern: str, size: int = 3) -> str:
    index = find_line_index(lines, pattern)
    return " ".join(lines[index : index + size])


def joined_window(lines: list[str], pattern: str, size: int = 4, scan: int = 3) -> str:
    index = find_joined_index(lines, pattern, scan)
    return " ".join(lines[index : index + size])


def find_numbers_after(lines: list[str], pattern: str, size: int = 2) -> list[int]:
    return numbers_in_text(line_window(lines, pattern, size))


def find_first_line(lines: list[str], predicates: list[str]) -> str:
    for line in lines:
        lowered = normalize(line)
        if any(predicate in lowered for predicate in predicates):
            return line
    raise ValueError(f"Missing line for predicates: {predicates}")


def find_first_line_startswith(lines: list[str], prefixes: list[str]) -> str:
    for line in lines:
        lowered = normalize(line)
        if any(lowered.startswith(prefix) for prefix in prefixes):
            return line
    raise ValueError(f"Missing line starting with one of: {prefixes}")


def find_joined_text(lines: list[str], predicates: list[str], size: int = 4, scan: int = 4) -> str:
    for index in range(len(lines)):
        joined = " ".join(lines[index : index + scan])
        lowered = normalize(joined)
        if all(predicate in lowered for predicate in predicates):
            return " ".join(lines[index : index + size])
    raise ValueError(f"Missing joined text for predicates: {predicates}")


def extract_h2_chunk(lines: list[str]) -> str:
    start = find_joined_index(lines, r"H2 Number of Enrolled Students Awarded Aid", 2)
    for end in range(start + 1, len(lines)):
        lowered = normalize(lines[end])
        if lowered.startswith("h2a number of enrolled students awarded non-need-based") or lowered.startswith(
            "h2a number of enrolled students award"
        ):
            return "\n".join(lines[start:end])
    return "\n".join(lines[start:])


def extract_h2_row_chunk(chunk: str, start_pattern: str, next_pattern: str) -> str:
    normalized_chunk = normalize(chunk)
    regex = re.compile(start_pattern + r"(.*?)" + next_pattern, re.IGNORECASE | re.DOTALL)
    match = regex.search(normalized_chunk)
    if not match:
        raise ValueError(f"Missing H2 row chunk for pattern {start_pattern}")
    return match.group(1)


def clean_count_values(values: list[int]) -> list[int]:
    cleaned = [value for value in values if value >= 10]
    if len(cleaned) > 2:
        cleaned = [value for value in cleaned if not (1900 <= value <= 2100 and len(cleaned) > 2)]
    return cleaned


def repair_split_money_values(values: list[int]) -> list[int]:
    repaired: list[int] = []
    index = 0
    while index < len(values):
        current = values[index]
        if current < 10 and index + 1 < len(values) and 1000 <= values[index + 1] < 10000:
            repaired.append(current * 10000 + values[index + 1])
            index += 2
            continue
        repaired.append(current)
        index += 1
    return repaired


def extract_admissions(lines: list[str]) -> dict:
    applied = None
    admitted = None
    enrolled = None

    total_patterns = {
        "applied": [
            "total first-time, first-year (degree-seeking) who applied",
            "total first-time, first-year who applied",
        ],
        "admitted": [
            "total first-time, first-year (degree-seeking) who were admitted",
            "total first-time, first-year who were admitted",
        ],
        "enrolled": [
            "total first-time, first-year (degree-seeking) who enrolled",
            "total first-time, first-year who enrolled",
        ],
    }

    for field, patterns in total_patterns.items():
        for line in lines:
            lowered = normalize(line)
            if any(pattern in lowered for pattern in patterns) and "men who" not in lowered and "women who" not in lowered:
                values = numbers_in_text(line)
                if values:
                    if field == "applied":
                        applied = values[0]
                    elif field == "admitted":
                        admitted = values[0]
                    else:
                        enrolled = values[0]
                    break
        if field == "applied" and applied is not None:
            continue
        if field == "admitted" and admitted is not None:
            continue
        if field == "enrolled" and enrolled is not None:
            continue

    if applied is None:
        applied = 0
    if admitted is None:
        admitted = 0

    if applied == 0:
        for line in lines:
            lowered = normalize(line)
            if "who applied" in lowered and "total first-time, first-year" in lowered:
                values = numbers_in_text(line)
                if values:
                    applied += values[-1]

    if admitted == 0:
        for line in lines:
            lowered = normalize(line)
            if "who were admitted" in lowered and "total first-time, first-year" in lowered:
                values = numbers_in_text(line)
                if values:
                    admitted += values[-1]

    if enrolled is None:
        h2_chunk = extract_h2_chunk(lines)
        a_values = clean_count_values(
            numbers_in_text(
                extract_h2_row_chunk(
                    h2_chunk,
                    r"(?:^|\n)(?:H2\s*a\)|A)\s+Number of degree-seeking undergraduate",
                    r"(?:^|\n)(?:H2\s*b\)|B)\s+Number of students in line a",
                )
            )
        )
        enrolled = a_values[0]

    ed_applied = find_numbers_after(
        lines, r"Number of early decision applications received", 2
    )[0]
    ed_admitted = find_numbers_after(
        lines, r"Number of applicants admitted under early decision plan", 2
    )[0]

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
    sat_submission = percents_in_text(
        find_first_line_startswith(
            lines,
            ["c9 percent submitting sat scores", "percent submitting sat scores", "submitting sat scores"],
        )
    )[0] / 100
    act_submission = percents_in_text(
        find_first_line_startswith(
            lines,
            ["c9 percent submitting act scores", "percent submitting act scores", "submitting act scores"],
        )
    )[0] / 100

    sat_erw_raw = numbers_in_text(
        find_first_line(
            lines,
            [
                "sat_r evidenced-based reading and writing",
                "sat_r evidence-based reading and writing",
                "sat evidenced-based reading and writing",
                "sat evidence-based reading and writing",
                "sat critical reading",
            ],
        )
    )[-3:]
    sat_math_raw = numbers_in_text(find_first_line(lines, ["sat_r math section", "sat math"]))[-3:]

    if len(sat_erw_raw) == 2:
        sat_erw = [sat_erw_raw[0], (sat_erw_raw[0] + sat_erw_raw[1]) // 2, sat_erw_raw[1]]
    else:
        sat_erw = sat_erw_raw

    if len(sat_math_raw) == 2:
        sat_math = [sat_math_raw[0], (sat_math_raw[0] + sat_math_raw[1]) // 2, sat_math_raw[1]]
    else:
        sat_math = sat_math_raw

    try:
        sat_composite_line = find_first_line_startswith(lines, ["c9 sat composite", "sat composite"])
        sat_composite_raw = numbers_in_text(sat_composite_line)
        if len(sat_composite_raw) < 2:
            raise ValueError("Composite row did not include score values")
        sat_composite_raw = sat_composite_raw[-3:]
        if len(sat_composite_raw) == 2:
            sat_composite = [
                sat_composite_raw[0],
                (sat_composite_raw[0] + sat_composite_raw[1]) // 2,
                sat_composite_raw[1],
            ]
        else:
            sat_composite = sat_composite_raw
    except ValueError:
        sat_composite = [
            sat_erw[0] + sat_math[0],
            sat_erw[1] + sat_math[1],
            sat_erw[2] + sat_math[2],
        ]

    act_composite_raw = numbers_in_text(
        find_first_line_startswith(lines, ["c9 act composite", "act composite"])
    )[-3:]
    if len(act_composite_raw) == 2:
        act_composite = [
            act_composite_raw[0],
            (act_composite_raw[0] + act_composite_raw[1]) // 2,
            act_composite_raw[1],
        ]
    else:
        act_composite = act_composite_raw

    return {
        "sat": {
            "composite": {"p25": sat_composite[0], "p50": sat_composite[1], "p75": sat_composite[2]},
            "readingWriting": {"p25": sat_erw[0], "p50": sat_erw[1], "p75": sat_erw[2]},
            "math": {"p25": sat_math[0], "p50": sat_math[1], "p75": sat_math[2]},
            "submissionRate": round(sat_submission, 4),
        },
        "act": {
            "composite": {"p25": act_composite[0], "p50": act_composite[1], "p75": act_composite[2]},
            "submissionRate": round(act_submission, 4),
        },
    }


def extract_b2_value(lines: list[str], label_patterns: list[str]) -> int:
    first_tokens = [pattern.split()[0] for pattern in label_patterns]
    for index, line in enumerate(lines):
        lowered = normalize(line)
        if any(pattern in lowered for pattern in label_patterns) and (
            lowered.startswith("b2 ") or any(lowered.startswith(token) for token in first_tokens)
        ):
            values = numbers_in_text(line)
            if values:
                return values[-1]
            values = numbers_in_text(" ".join(lines[index : index + 2]))
            if values:
                return values[-1]
    raise ValueError(f"Missing B2 row for {label_patterns[0]}")


def extract_demographics(lines: list[str]) -> dict:
    total = find_numbers_after(lines, r"GRAND TOTAL ALL STUDENTS", 1)[-1]

    undergraduate = 0
    graduate = 0
    for line in lines:
        lowered = normalize(line)
        if "total all undergraduates" in lowered or "grand total undergraduate students" in lowered:
            undergraduate = numbers_in_text(line)[-1]
        if "total all graduate" in lowered or "total graduate students" in lowered:
            graduate = numbers_in_text(line)[-1]
    if not undergraduate or not graduate:
        raise ValueError("Missing undergraduate or graduate enrollment totals")

    by_race = {
        "international": extract_b2_value(lines, ["nonresident aliens", "nonresidents"]),
        "hispanicLatino": extract_b2_value(lines, ["hispanic/latino"]),
        "blackAfricanAmerican": extract_b2_value(lines, ["black or african american"]),
        "white": extract_b2_value(lines, ["white, non-hispanic"]),
        "asian": extract_b2_value(lines, ["asian, non-hispanic", "asian"]),
        "americanIndianAlaskaNative": extract_b2_value(
            lines, ["american indian or alaska native"]
        ),
        "nativeHawaiianPacificIslander": extract_b2_value(
            lines, ["native hawaiian or other pacific islander"]
        ),
        "twoOrMoreRaces": extract_b2_value(lines, ["two or more races"]),
        "unknown": extract_b2_value(lines, ["race and/or ethnicity unknown"]),
    }

    race_total = sum(by_race.values())
    if race_total < undergraduate:
        by_race["unknown"] += undergraduate - race_total

    out_of_state_pct = 0.0
    for index, line in enumerate(lines):
        if "Percent who are from out of state" in line:
            window = " ".join(lines[index : index + 2])
            percents = percents_in_text(window)
            if percents:
                out_of_state_pct = percents[-1] / 100
                break
    if out_of_state_pct == 0:
        raise ValueError("Missing out-of-state percentage")

    domestic = undergraduate - by_race["international"]
    out_of_state = round(domestic * out_of_state_pct)
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
    tuition = 0
    fees = 0
    room_board = 0

    for index, line in enumerate(lines):
        lowered = normalize(line)
        if tuition == 0:
            tuition_amounts = dollar_amounts(line)
            if lowered.startswith("tuition:") and tuition_amounts:
                tuition = tuition_amounts[-1]
            elif "private institutions" in lowered and index + 2 < len(lines):
                next_amounts = dollar_amounts(lines[index + 1])
                if next_amounts and normalize(lines[index + 2]).startswith("tuition:"):
                    tuition = next_amounts[-1]

        if fees == 0 and lowered.startswith("required fees:"):
            fee_amounts = dollar_amounts(line)
            if fee_amounts:
                fees = fee_amounts[-1]

        if room_board == 0:
            if lowered.startswith("food and housing (on-campus):"):
                room_board_amounts = dollar_amounts(line)
                if room_board_amounts:
                    room_board = room_board_amounts[-1]
            elif lowered.startswith("g1 room and board:") or lowered.startswith("room and board:"):
                room_board_amounts = dollar_amounts(line)
                if room_board_amounts:
                    room_board = room_board_amounts[-1]
                elif index + 1 < len(lines):
                    next_amounts = dollar_amounts(lines[index + 1])
                    if next_amounts:
                        room_board = next_amounts[-1]

    return {
        "tuition": tuition,
        "fees": fees,
        "roomAndBoard": room_board,
        "totalCOA": tuition + fees + room_board,
    }


def extract_financial_aid(lines: list[str]) -> dict:
    chunk = extract_h2_chunk(lines)

    a_values = numbers_in_text(
        extract_h2_row_chunk(
            chunk,
            r"(?:^|\n)(?:H2\s*a\)|A)\s+Number of degree-seeking undergraduate",
            r"(?:^|\n)(?:H2\s*b\)|B)\s+Number of students in line a",
        )
    )
    d_values = numbers_in_text(
        extract_h2_row_chunk(
            chunk,
            r"(?:^|\n)(?:H2\s*d\)|D)\s+Number of students in line c who were",
            r"(?:^|\n)(?:H2\s*e\)|E)\s+Number of students in line d who were",
        )
    )
    h_values = numbers_in_text(
        extract_h2_row_chunk(
            chunk,
            r"(?:^|\n)(?:H2\s*h\)|H)\s+Number of students in line d whose need was",
            r"(?:^|\n)(?:H2\s*i\)|I)\s+On average",
        )
    )
    average_package_chunk = extract_h2_row_chunk(
        chunk,
        r"(?:^|\n)(?:H2\s*j\)|J)\s+(?:The\s+)?average financial aid package",
        r"(?:^|\n)(?:H2\s+Average need-based scholarship and grant|Average need-based scholarship and grant|K\s+\$|k\))",
    )
    average_grant_chunk = extract_h2_row_chunk(
        chunk,
        r"(?:^|\n)(?:H2\s+Average need-based scholarship and grant|Average need-based scholarship and grant|k\))",
        r"(?:^|\n)(?:H2\s*l\)|L)\s+Average need-based self-help award",
    )

    average_package_values = dollar_amounts(average_package_chunk)
    if not average_package_values:
        average_package_values = repair_split_money_values(
            [value for value in numbers_in_text(average_package_chunk) if value >= 1000]
        )

    average_grant_values = dollar_amounts(average_grant_chunk)
    if not average_grant_values:
        average_grant_values = repair_split_money_values(
            [value for value in numbers_in_text(average_grant_chunk) if value >= 1000]
        )

    a = clean_count_values(a_values)[-1]
    d = clean_count_values(d_values)[-1]
    h = clean_count_values(h_values)[-1]
    average_package = average_package_values[-1]
    average_grant = average_grant_values[-1]

    return {
        "percentReceivingAid": round(d / a, 4) if a else 0,
        "averageAidPackage": average_package,
        "averageNeedBasedGrant": average_grant,
        "percentNeedFullyMet": round(h / d, 4) if d else 0,
    }


def extract_year(pdf_path: Path) -> dict:
    lines = load_lines(pdf_path)
    year_data = {
        "admissions": extract_admissions(lines),
        "testScores": extract_test_scores(lines),
        "demographics": extract_demographics(lines),
        "costs": extract_costs(lines),
        "financialAid": extract_financial_aid(lines),
    }

    undergraduate = year_data["demographics"]["enrollment"]["undergraduate"]
    if sum(year_data["demographics"]["byRace"].values()) != undergraduate:
        raise ValueError(f"Race totals do not match undergraduate total for {pdf_path.name}")
    if sum(year_data["demographics"]["byResidency"].values()) != undergraduate:
        raise ValueError(f"Residency totals do not match undergraduate total for {pdf_path.name}")

    return year_data


def main() -> None:
    school_data = {
        "name": "Rice University",
        "slug": "rice",
        "years": {year: extract_year(path) for year, path in PDF_FILES.items()},
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(school_data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
