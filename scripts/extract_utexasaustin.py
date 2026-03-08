#!/usr/bin/env python3
"""
UT Austin CDS extractor.

Uses local CDS PDFs for available years and a Box preview fallback for the
missing 2022-2023 report.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import pdfplumber
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "College-Data" / "UTexasAustin"
OUTPUT_PATH = ROOT / "src" / "data" / "schools" / "utexasaustin.json"
MISSING_2022_URL = (
    "https://utexas.app.box.com/file/1175204890159"
    "?s=obiyu5y2t1g3mj4lv0ntwd9nsg911hjt"
)

YEAR_FILE_MAP = {
    "2016-2017": "IMA_PUB_CDS 2016-2017_AY.pdf",
    "2017-2018": "IMA_PUB_CDS_2017-2018_AY.pdf",
    "2018-2019": "IRRIS_PUB_CDS_2018-2019_AY.pdf",
    "2019-2020": "IRRIS_PUB_CDS_2019-2020_AY.pdf",
    "2020-2021": "IRRIS_PUB_CDS_2020-2021_AY.pdf",
    "2021-2022": "IRRIS_PUB_CDS_2021-2022_AY.pdf",
    "2023-2024": "IRRIS_PUB_CDS_2023-2024_AY.pdf",
    "2024-2025": "IRRIS_PUB_CDS_2024-2025_AY.pdf",
}


def extract_number(value: str) -> int:
    cleaned = re.sub(r"[^\d]", "", value or "")
    return int(cleaned) if cleaned else 0


def extract_dollar(value: str) -> int:
    match = re.search(r"\$?\s*([\d,]+)", value or "")
    return extract_number(match.group(1)) if match else 0


def normalize_text(text: str) -> str:
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2068", "").replace("\u2069", "")
    return text


def lines_from_text(text: str) -> list[str]:
    cleaned_lines = []
    for raw_line in normalize_text(text).splitlines():
        raw_line = re.sub(r"\b(\d)\s+(\d,\d{3})\b", r"\1\2", raw_line)
        raw_line = re.sub(r"\b(\d)\s+,(\d{3})\b", r"\1,\2", raw_line)
        raw_line = re.sub(r"\b(\d)\s+(\d{2,3})\b", r"\1\2", raw_line)
        raw_line = re.sub(r"\b(\d)\s+(\d)\b", r"\1\2", raw_line)
        line = re.sub(r"\s+", " ", raw_line).strip()
        line = re.sub(r"^[A-Z]\d+[A-Z]?(?:\s+[a-z]\))?\s*", "", line)
        if line:
            cleaned_lines.append(line)
    return cleaned_lines


def extract_local_pdf_text(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def extract_box_preview_pages() -> dict[int, str]:
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1400,2500")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(MISSING_2022_URL)
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(8)

        pages = driver.find_elements(By.XPATH, "//div[contains(@aria-label, 'Page')]")
        page_texts: dict[int, str] = {}

        for page in pages:
            label = page.get_attribute("aria-label") or ""
            if "Page" not in label:
                continue
            numbers = re.findall(r"\d+", label)
            if not numbers:
                continue
            page_number = int(numbers[-1])
            driver.execute_script(
                'arguments[0].scrollIntoView({block:"center"})',
                page,
            )
            time.sleep(1.5)
            text = page.text.strip()
            if text:
                page_texts[page_number] = text

        return page_texts
    finally:
        driver.quit()


def extract_box_preview_text() -> str:
    return "\n".join(extract_box_preview_pages().values())


def parse_total_from_lines(lines: list[str], label_patterns: list[str]) -> int:
    for line in lines:
        if not line.startswith("Total"):
            continue
        for label in label_patterns:
            if re.search(label, line, re.IGNORECASE):
                numbers = re.findall(r"[\d,]+", line)
                if numbers:
                    return extract_number(numbers[0])
    return 0


def parse_admissions(text: str) -> dict:
    lines = lines_from_text(text)
    data = {
        "applied": 0,
        "admitted": 0,
        "enrolled": 0,
        "acceptanceRate": 0,
        "yield": 0,
    }

    for line in lines:
        lowered = line.lower()
        numbers = [extract_number(value) for value in re.findall(r"[\d,]+", line)]

        if "total first-time, first-year students who applied in fall" in lowered and len(numbers) >= 3:
            data["applied"] = sum(numbers[-3:])
        elif "total first-time, first-year students admitted in fall" in lowered and len(numbers) >= 3:
            data["admitted"] = sum(numbers[-3:])
        elif "total first-time, first-year students enrolled in fall" in lowered and len(numbers) >= 3:
            data["enrolled"] = sum(numbers[-3:])
        elif "total first-time, first-year (degree seeking) who applied" in lowered and len(numbers) >= 4:
            data["applied"] = numbers[-1]
        elif "total first-time, first-year (degree seeking) who were admitted" in lowered and len(numbers) >= 4:
            data["admitted"] = numbers[-1]
        elif "total first-time, first-year (degree seeking) enrolled" in lowered and len(numbers) >= 4:
            data["enrolled"] = numbers[-1]
        elif "total first-time, first-year who applied" in lowered and len(numbers) >= 4:
            data["applied"] = numbers[0]
        elif "total first-time, first-year who were admitted" in lowered and len(numbers) >= 4:
            data["admitted"] = numbers[0]
        elif "total first-time, first-year who enrolled" in lowered and len(numbers) >= 4:
            data["enrolled"] = numbers[0]

    if not all(data[key] for key in ("applied", "admitted", "enrolled")):
        category_patterns = {
            "men": r"\bmen\b",
            "women": r"\bwomen\b",
            "another gender": r"another gender",
            "unknown gender": r"unknown gender",
        }
        gender_totals = {"applied": 0, "admitted": 0, "enrolled": 0}

        for line in lines:
            lowered = line.lower()
            for category_pattern in category_patterns.values():
                if not re.search(category_pattern, lowered):
                    continue
                numbers = re.findall(r"[\d,]+", line)
                if not numbers:
                    continue
                value = extract_number(numbers[-1])
                if "who applied" in lowered:
                    gender_totals["applied"] += value
                elif "who were admitted" in lowered:
                    gender_totals["admitted"] += value
                elif "who enrolled" in lowered:
                    gender_totals["enrolled"] += value

        for key in gender_totals:
            if not data[key]:
                data[key] = gender_totals[key]

    if data["applied"] and data["admitted"]:
        data["acceptanceRate"] = round(data["admitted"] / data["applied"], 4)
    if data["admitted"] and data["enrolled"]:
        data["yield"] = round(data["enrolled"] / data["admitted"], 4)

    return data


def parse_test_scores(text: str) -> dict:
    flat = normalize_text(text).replace("\n", " ")
    data: dict = {}

    sat_submission = re.search(r"Percent submitting SAT scores\s+(\d+(?:\.\d+)?)%", flat, re.IGNORECASE)
    act_submission = re.search(r"Percent submitting ACT scores\s+(\d+(?:\.\d+)?)%", flat, re.IGNORECASE)

    sat_rw = re.search(
        r"SAT (?:Evidence-Based Reading and Writing|Critical Reading)\s+(\d{3})\s+(\d{3})",
        flat,
        re.IGNORECASE,
    )
    sat_math = re.search(r"SAT Math\s+(\d{3})\s+(\d{3})", flat, re.IGNORECASE)
    sat_comp = re.search(r"SAT Composite\s+(\d{4})\s+(\d{4})", flat, re.IGNORECASE)
    act_comp = re.search(r"ACT Composite\s+(\d{2})\s+(\d{2})", flat, re.IGNORECASE)

    if sat_rw and sat_math:
        rw25, rw75 = map(int, sat_rw.groups())
        math25, math75 = map(int, sat_math.groups())
        comp25 = rw25 + math25
        comp75 = rw75 + math75
        if sat_comp:
            comp25, comp75 = map(int, sat_comp.groups())
        data["sat"] = {
            "composite": {"p25": comp25, "p50": (comp25 + comp75) // 2, "p75": comp75},
            "readingWriting": {"p25": rw25, "p50": (rw25 + rw75) // 2, "p75": rw75},
            "math": {"p25": math25, "p50": (math25 + math75) // 2, "p75": math75},
            "submissionRate": round((float(sat_submission.group(1)) / 100), 4) if sat_submission else 0,
        }

    if act_comp:
        p25, p75 = map(int, act_comp.groups())
        data["act"] = {
            "composite": {"p25": p25, "p50": (p25 + p75) // 2, "p75": p75},
            "submissionRate": round((float(act_submission.group(1)) / 100), 4) if act_submission else 0,
        }

    # Test-optional years often leave C9 blank; return an empty object in those cases.
    return data


def parse_enrollment(flat_text: str) -> tuple[int, int]:
    undergrad_patterns = [
        r"Total all undergraduates\s+([\d,]+)",
        r"Total of all undergraduate students enrolled\s+([\d,]+)",
    ]
    grad_patterns = [
        r"Total all graduate\s+([\d,]+)",
        r"Total of all graduate students enrolled\s+([\d,]+)",
    ]

    undergraduate = 0
    graduate = 0

    for pattern in undergrad_patterns:
        match = re.search(pattern, flat_text, re.IGNORECASE)
        if match:
            undergraduate = extract_number(match.group(1))
            break

    for pattern in grad_patterns:
        match = re.search(pattern, flat_text, re.IGNORECASE)
        if match:
            graduate = extract_number(match.group(1))
            break

    return undergraduate, graduate


def parse_race_counts(flat_text: str) -> dict:
    row_patterns = {
        "international": [
            r"(?:Nonresidents|Nonresident aliens|International \(nonresidents\))\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"
        ],
        "hispanicLatino": [r"Hispanic/Latino\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"],
        "blackAfricanAmerican": [
            r"Black or African American,\s+non-?\s*Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"
        ],
        "white": [r"White,\s+non-?\s*Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"],
        "asian": [r"Asian,\s+non-?\s*Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"],
        "americanIndianAlaskaNative": [
            r"American Indian or Alaska Native,\s+non-?\s*Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)",
            r"American Indian or Alaska Native,\s+non-\s*([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+Hispanic",
        ],
        "nativeHawaiianPacificIslander": [
            r"Native Hawaiian or other Pacific Islander,\s+non-?\s*Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)",
            r"Native Hawaiian or other Pacific Islander,\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+non-?\s*Hispanic",
        ],
        "twoOrMoreRaces": [r"Two or more races,\s+non-?\s*Hispanic\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"],
        "unknown": [r"Race and/or ethnicity unknown\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"],
    }

    counts = {key: 0 for key in row_patterns}
    for key, patterns in row_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, flat_text, re.IGNORECASE)
            if match:
                counts[key] = extract_number(match.group(3))
                break

    return counts


def parse_residency(flat_text: str, undergraduate: int, international: int) -> dict:
    match = re.search(
        r"Percent who are from out of state.*?(\d+(?:\.\d+)?)%?\s+(\d+(?:\.\d+)?)%",
        flat_text,
        re.IGNORECASE,
    )

    out_pct = float(match.group(2)) if match else 0.0
    domestic = max(undergraduate - international, 0)
    out_of_state = int(round(domestic * out_pct / 100))
    in_state = domestic - out_of_state

    return {
        "inState": in_state,
        "outOfState": out_of_state,
        "international": international,
    }


def parse_demographics(text: str) -> dict:
    flat = normalize_text(text).replace("\n", " ")
    undergraduate, graduate = parse_enrollment(flat)
    by_race = parse_race_counts(flat)

    return {
        "enrollment": {
            "total": undergraduate + graduate,
            "undergraduate": undergraduate,
            "graduate": graduate,
        },
        "byRace": by_race,
        "byResidency": parse_residency(flat, undergraduate, by_race["international"]),
    }


def parse_costs(text: str) -> dict:
    flat = normalize_text(text).replace("\n", " ")
    tuition = 0
    fees = 0
    room_board = 0

    tuition_match = re.search(
        r"Tuition:\s*Out-of-state:?\s*\$([\d,]+)",
        flat,
        re.IGNORECASE,
    )
    if not tuition_match:
        tuition_match = re.search(r"Out-of-state:\s*\$([\d,]+)", flat, re.IGNORECASE)
    if tuition_match:
        tuition = extract_number(tuition_match.group(1))

    fees_match = re.search(r"Required Fees:?\s*\$([\d,]+)", flat, re.IGNORECASE)
    if fees_match:
        fees = extract_number(fees_match.group(1))

    room_match = re.search(
        r"(?:Room and Board|Food and housing) \(on-campus\):\s*\$([\d,]+)",
        flat,
        re.IGNORECASE,
    )
    if not room_match:
        room_match = re.search(r"ROOM AND BOARD:\s*\(on-campus\)\s*\$([\d,]+)", flat, re.IGNORECASE)
    if room_match:
        room_board = extract_number(room_match.group(1))

    return {
        "tuition": tuition,
        "fees": fees,
        "roomAndBoard": room_board,
        "totalCOA": tuition + fees + room_board,
    }


def parse_h2_row(flat_text: str, phrase: str) -> list[float]:
    pattern = rf"{phrase}\s+([\d,]+%?)\s+([\d,]+%?)\s+([\d,]+%?)"
    match = re.search(pattern, flat_text, re.IGNORECASE)
    if not match:
        return [0, 0, 0]
    values = []
    for value in match.groups():
        if "%" in value:
            values.append(float(value.replace("%", "").replace(",", "")))
        else:
            values.append(extract_number(value))
    return values


def parse_h2_letter_row(flat_text: str, row_letters: list[str], dollar: bool = False) -> list[int]:
    token = r"\$\s*([\d,]+)" if dollar else r"([\d,]+)"
    for row_letter in row_letters:
        pattern = rf"(?:H2\s*)?{row_letter}\)\s+.*?{token}\s+{token}\s+{token}"
        match = re.search(pattern, flat_text, re.IGNORECASE)
        if match:
            return [extract_number(group) for group in match.groups()]
    return [0, 0, 0]


def parse_h2_line_values(lines: list[str], phrases: list[str]) -> list[int]:
    phrase_lowers = [phrase.lower() for phrase in phrases]
    for index, line in enumerate(lines):
        lowered = line.lower()
        if not any(phrase in lowered for phrase in phrase_lowers):
            continue
        values: list[int] = []
        for look_ahead in range(index, min(index + 5, len(lines))):
            line_values = re.findall(r"\$?\s*[\d,]+(?:\.\d+)?%?", lines[look_ahead])
            for raw_value in line_values:
                if "%" in raw_value:
                    continue
                number = extract_number(raw_value)
                if number:
                    values.append(number)
            if len(values) >= 3:
                return values[-3:]
    return [0, 0, 0]


def parse_financial_aid(text: str) -> dict:
    lines = lines_from_text(text)

    row_a = parse_h2_line_values(lines, ["Number of degree-seeking undergraduate"])
    row_d = parse_h2_line_values(
        lines,
        [
            "Number of students in line c who were awarded",
            "Number of students in line (c) who were awarded",
        ],
    )
    row_h = parse_h2_line_values(
        lines,
        [
            "Number of students in line d whose need was fully",
            "Number of students in line (d) whose need was fully",
            "Number of students in line (d) who need was fully",
        ],
    )
    row_j = parse_h2_line_values(
        lines,
        [
            "The average financial aid package of those in line",
        ],
    )
    row_k = parse_h2_line_values(
        lines,
        [
            "Average need-based scholarship and grant award",
            "Average need-based scholarship or grant award",
        ],
    )

    students = int(row_a[1]) if row_a else 0
    awarded = int(row_d[1]) if row_d else 0
    fully_met = int(row_h[1]) if row_h else 0
    avg_package = int(row_j[1]) if row_j else 0
    avg_grant = int(row_k[1]) if row_k else 0

    return {
        "percentReceivingAid": round(awarded / students, 4) if students else 0,
        "averageAidPackage": avg_package,
        "averageNeedBasedGrant": avg_grant,
        "percentNeedFullyMet": round(fully_met / awarded, 4) if awarded else 0,
    }


def extract_year_data(text: str) -> dict:
    return {
        "admissions": parse_admissions(text),
        "testScores": parse_test_scores(text),
        "demographics": parse_demographics(text),
        "costs": parse_costs(text),
        "financialAid": parse_financial_aid(text),
    }


def extract_2022_box_year_data(page_texts: dict[int, str]) -> dict:
    page3 = page_texts[3]
    page7 = page_texts[7]
    page18 = page_texts[18]
    page19 = page_texts[19]
    financial_text = "\n".join(page_texts.get(page, "") for page in (22, 23))

    admissions_section = page7.split("C1-C2: Applications", 1)[1].split("C2", 1)[0]
    admission_numbers = [extract_number(value) for value in re.findall(r"[\d,]+", admissions_section)]
    applied_men, applied_women, admitted_men, admitted_women, enrolled_men_ft, enrolled_men_pt, enrolled_women_ft, enrolled_women_pt = admission_numbers[:8]

    flat_page3 = normalize_text(page3).replace("\n", " ")
    undergraduate, graduate = parse_enrollment(flat_page3)

    b2_section = page3.split("B2", 1)[1].split("Persistence", 1)[0]
    b2_numbers = [extract_number(value) for value in re.findall(r"[\d,]+", b2_section)]

    race_rows = [b2_numbers[index : index + 3] for index in range(0, 30, 3)]
    by_race = {
        "international": race_rows[0][2],
        "hispanicLatino": race_rows[1][2],
        "blackAfricanAmerican": race_rows[2][2],
        "white": race_rows[3][2],
        "americanIndianAlaskaNative": race_rows[4][2],
        "asian": race_rows[5][2],
        "nativeHawaiianPacificIslander": race_rows[6][2],
        "twoOrMoreRaces": race_rows[7][2],
        "unknown": race_rows[8][2],
    }

    admissions = {
        "applied": applied_men + applied_women,
        "admitted": admitted_men + admitted_women,
        "enrolled": enrolled_men_ft + enrolled_men_pt + enrolled_women_ft + enrolled_women_pt,
        "acceptanceRate": 0,
        "yield": 0,
    }
    admissions["acceptanceRate"] = round(admissions["admitted"] / admissions["applied"], 4)
    admissions["yield"] = round(admissions["enrolled"] / admissions["admitted"], 4)

    financial_lines = lines_from_text(financial_text)

    def parse_box_row(row_letter: str) -> list[int]:
        for index, line in enumerate(financial_lines):
            if line == row_letter:
                values: list[int] = []
                for look_ahead in range(index + 1, min(index + 10, len(financial_lines))):
                    matches = re.findall(r"\$?\s*[\d,]+", financial_lines[look_ahead])
                    for raw_value in matches:
                        number = extract_number(raw_value)
                        if number:
                            values.append(number)
                if len(values) >= 3:
                    return values[-3:]
        return [0, 0, 0]

    row_a = parse_box_row("A")
    row_d = parse_box_row("D")
    row_h = parse_box_row("H")
    row_j = parse_box_row("J")
    row_k = parse_box_row("K")
    financial_aid = {
        "percentReceivingAid": round(row_d[1] / row_a[1], 4) if row_a[1] else 0,
        "averageAidPackage": row_j[1],
        "averageNeedBasedGrant": row_k[1],
        "percentNeedFullyMet": round(row_h[1] / row_d[1], 4) if row_d[1] else 0,
    }

    return {
        "admissions": admissions,
        "testScores": {},
        "demographics": {
            "enrollment": {
                "total": undergraduate + graduate,
                "undergraduate": undergraduate,
                "graduate": graduate,
            },
            "byRace": by_race,
            "byResidency": parse_residency(
                normalize_text(page18).replace("\n", " "),
                undergraduate,
                by_race["international"],
            ),
        },
        "costs": parse_costs(page19),
        "financialAid": financial_aid,
    }


def validate_year(year: str, year_data: dict) -> None:
    enrollment = year_data["demographics"]["enrollment"]
    by_race = year_data["demographics"]["byRace"]
    by_residency = year_data["demographics"]["byResidency"]

    assert enrollment["total"] == enrollment["undergraduate"] + enrollment["graduate"], year
    assert sum(by_race.values()) == enrollment["undergraduate"], year
    assert sum(by_residency.values()) == enrollment["undergraduate"], year


def main() -> None:
    school_data = {
        "name": "The University of Texas at Austin",
        "slug": "utexasaustin",
        "years": {},
    }

    for year, filename in YEAR_FILE_MAP.items():
        text = extract_local_pdf_text(SOURCE_DIR / filename)
        school_data["years"][year] = extract_year_data(text)

    school_data["years"]["2022-2023"] = extract_2022_box_year_data(extract_box_preview_pages())

    for year, year_data in school_data["years"].items():
        validate_year(year, year_data)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(school_data, f, indent=2)

    for year in sorted(school_data["years"]):
        admissions = school_data["years"][year]["admissions"]
        costs = school_data["years"][year]["costs"]
        print(
            f"{year}: applied={admissions['applied']:,}, admitted={admissions['admitted']:,}, "
            f"enrolled={admissions['enrolled']:,}, coa=${costs['totalCOA']:,}"
        )


if __name__ == "__main__":
    main()
