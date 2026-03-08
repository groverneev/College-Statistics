#!/usr/bin/env python3
"""
University of Michigan Ann Arbor CDS extractor.

Parses the PDFs in College-Data/University of Michigan Ann Arbor and writes
src/data/schools/umich.json.
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


PDF_DIR = Path("College-Data/University of Michigan Ann Arbor")
OUTPUT_PATH = Path("src/data/schools/umich.json")


def clean_text(text: str) -> str:
    text = text.encode("ascii", "ignore").decode()
    text = text.replace("\r", "")
    return text


def extract_number(value: str) -> int:
    return int(value.replace(",", "").replace("$", "").strip())


def extract_numbers_no_percent(text: str) -> list[int]:
    pattern = r"(?<![\d.])\d{1,3}(?:,\d{3})*(?![\d.%])"
    return [extract_number(match) for match in re.findall(pattern, text)]


def extract_first_matching_int(text: str, patterns: list[str]) -> int:
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return extract_number(match.group(1))
    return 0


def load_pdf_text(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return clean_text("\n".join(page.extract_text() or "" for page in pdf.pages))


def extract_year_from_filename(filename: str) -> str:
    match = re.search(r"(\d{4})[-_](\d{2,4})", filename)
    if not match:
        raise ValueError(f"Could not extract year from {filename}")

    start = int(match.group(1))
    end_raw = match.group(2)
    end = int(end_raw) if len(end_raw) == 4 else 2000 + int(end_raw)
    return f"{start}-{end}"


def find_section(text: str, start_marker: str, end_markers: list[str]) -> str:
    start = text.lower().find(start_marker.lower())
    if start == -1:
        return ""

    end = len(text)
    for marker in end_markers:
        idx = text.lower().find(marker.lower(), start + len(start_marker))
        if idx != -1:
            end = min(end, idx)
    return text[start:end]


def extract_admissions(text: str) -> dict:
    data = {
        "applied": 0,
        "admitted": 0,
        "enrolled": 0,
        "acceptanceRate": 0,
        "yield": 0,
    }

    men = {
        "applied": extract_first_matching_int(
            text,
            [
                r"Total first-time, first-year \(freshman\) men who applied\s+(\d[\d,]*)",
                r"Total applications by men .*?admission\s+(\d[\d,]*)",
                r"Total men who applied .*?admission\s+(\d[\d,]*)",
            ],
        ),
        "admitted": extract_first_matching_int(
            text,
            [
                r"Total first-time, first-year \(freshman\) men who were admitted\s+(\d[\d,]*)",
                r"Total offers to men .*?admission\s+(\d[\d,]*)",
                r"Total men offered .*?admission\s+(\d[\d,]*)",
            ],
        ),
        "enrolled": extract_first_matching_int(
            text,
            [
                r"Total full-time, first-time, first-year \(freshman\) men who enrolled\s+(\d[\d,]*)",
                r"Total full-time, first-time, first-year men who enrolled\s+(\d[\d,]*)",
            ],
        ) + extract_first_matching_int(
            text,
            [
                r"Total part-time, first-time, first-year \(freshman\) men who enrolled\s+(\d[\d,]*)",
                r"Total part-time, first-time, first-year men who enrolled\s+(\d[\d,]*)",
            ],
        ),
    }
    women = {
        "applied": extract_first_matching_int(
            text,
            [
                r"Total first-time, first-year \(freshman\) women who applied\s+(\d[\d,]*)",
                r"Total applications by women .*?admission\s+(\d[\d,]*)",
                r"Total women who applied .*?admission\s+(\d[\d,]*)",
            ],
        ),
        "admitted": extract_first_matching_int(
            text,
            [
                r"Total first-time, first-year \(freshman\) women who were admitted\s+(\d[\d,]*)",
                r"Total offers to women .*?admission\s+(\d[\d,]*)",
                r"Total women offered .*?admission\s+(\d[\d,]*)",
            ],
        ),
        "enrolled": extract_first_matching_int(
            text,
            [
                r"Total full-time, first-time, first-year \(freshman\) women who enrolled\s+(\d[\d,]*)",
                r"Total full-time, first-time, first-year women who enrolled\s+(\d[\d,]*)",
            ],
        ) + extract_first_matching_int(
            text,
            [
                r"Total part-time, first-time, first-year \(freshman\) women who enrolled\s+(\d[\d,]*)",
                r"Total part-time, first-time, first-year women who enrolled\s+(\d[\d,]*)",
            ],
        ),
    }

    total_applied_match = re.search(
        r"Total first-time, first-year students who applied\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)",
        text,
        re.I,
    )
    total_admitted_match = re.search(
        r"Total first-time, first-year students admitted\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)",
        text,
        re.I,
    )
    total_enrolled_match = re.search(
        r"Total first-time, first-year students enrolled\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)",
        text,
        re.I,
    )

    if total_applied_match:
        data["applied"] = extract_number(total_applied_match.group(3))
        men["applied"] = extract_number(total_applied_match.group(1))
        women["applied"] = extract_number(total_applied_match.group(2))
    if total_admitted_match:
        data["admitted"] = extract_number(total_admitted_match.group(3))
        men["admitted"] = extract_number(total_admitted_match.group(1))
        women["admitted"] = extract_number(total_admitted_match.group(2))
    if total_enrolled_match:
        data["enrolled"] = extract_number(total_enrolled_match.group(3))
        men["enrolled"] = extract_number(total_enrolled_match.group(1))
        women["enrolled"] = extract_number(total_enrolled_match.group(2))

    if data["applied"] == 0 and men["applied"] and women["applied"]:
        data["applied"] = men["applied"] + women["applied"]
    if data["admitted"] == 0 and men["admitted"] and women["admitted"]:
        data["admitted"] = men["admitted"] + women["admitted"]
    if data["enrolled"] == 0 and men["enrolled"] and women["enrolled"]:
        data["enrolled"] = men["enrolled"] + women["enrolled"]

    if data["applied"] > 0 and data["admitted"] > 0:
        data["acceptanceRate"] = round(data["admitted"] / data["applied"], 4)
    if data["admitted"] > 0 and data["enrolled"] > 0:
        data["yield"] = round(data["enrolled"] / data["admitted"], 4)

    data["byGender"] = {
        "men": men,
        "women": women,
    }
    return data


def build_score_block(match: re.Match[str]) -> dict:
    nums = [int(group) for group in match.groups() if group]
    if len(nums) == 3:
        return {"p25": nums[0], "p50": nums[1], "p75": nums[2]}
    return {"p25": nums[0], "p50": (nums[0] + nums[1]) // 2, "p75": nums[1]}


def extract_test_scores(text: str) -> dict:
    data = {}
    joined = text.replace("\n", " ")
    lines = [" ".join(line.split()) for line in text.splitlines() if line.strip()]

    sat_submit_match = re.search(r"(?:Percent submitting SAT scores|Submitting SAT Scores)\s+(\d+(?:\.\d+)?)%", joined, re.I)
    act_submit_match = re.search(r"(?:Percent submitting ACT scores|Submitting ACT Scores)\s+(\d+(?:\.\d+)?)%", joined, re.I)
    sat_submission = (float(sat_submit_match.group(1)) / 100) if sat_submit_match else 0
    act_submission = (float(act_submit_match.group(1)) / 100) if act_submit_match else 0

    sat_data = {
        "composite": {"p25": 0, "p50": 0, "p75": 0},
        "readingWriting": {"p25": 0, "p50": 0, "p75": 0},
        "math": {"p25": 0, "p50": 0, "p75": 0},
        "submissionRate": sat_submission,
    }

    sat_line_patterns = {
        "composite": [
            r"SAT Composite(?:\s*\([^)]+\))?\s+(\d{3,4})\s+(\d{3,4})\s+(\d{3,4})$",
            r"SAT Composite\s+(\d{3,4})\s+(\d{3,4})(?:\s+800 to 1600)?$",
        ],
        "readingWriting": [
            r"SAT Evidence[- ]based Reading and Writing(?:\s*\([^)]+\))?\s+(\d{3})\s+(\d{3})\s+(\d{3})$",
            r"SAT Evidence[- ]based Reading and Writing\s+(\d{3})\s+(\d{3})$",
            r"SAT Critical Reading\s+(\d{3})\s+(\d{3})$",
        ],
        "math": [
            r"SAT Math(?:\s*\([^)]+\))?\s+(\d{3})\s+(\d{3})\s+(\d{3})$",
            r"SAT Math\s+(\d{3})\s+(\d{3})$",
        ],
    }

    for line in lines:
        for field, patterns in sat_line_patterns.items():
            if sat_data[field]["p25"]:
                continue
            for pattern in patterns:
                match = re.search(pattern, line, re.I)
                if match:
                    sat_data[field] = build_score_block(match)
                    break

    if sat_data["composite"]["p25"] == 0 and sat_data["readingWriting"]["p25"] and sat_data["math"]["p25"]:
        sat_data["composite"] = {
            "p25": sat_data["readingWriting"]["p25"] + sat_data["math"]["p25"],
            "p50": sat_data["readingWriting"]["p50"] + sat_data["math"]["p50"],
            "p75": sat_data["readingWriting"]["p75"] + sat_data["math"]["p75"],
        }

    if sat_data["readingWriting"]["p25"] and sat_data["math"]["p25"]:
        data["sat"] = sat_data

    act_data = {
        "composite": {"p25": 0, "p50": 0, "p75": 0},
        "submissionRate": act_submission,
    }
    for line in lines:
        for pattern in [
            r"ACT Composite(?:\s*\([^)]+\))?\s+(\d{2})\s+(\d{2})\s+(\d{2})$",
            r"ACT Composite\s+(\d{2})\s+(\d{2})$",
        ]:
            match = re.search(pattern, line, re.I)
            if match:
                act_data["composite"] = build_score_block(match)
                break
        if act_data["composite"]["p25"]:
            break

    if act_data["composite"]["p25"]:
        data["act"] = act_data

    return data


def extract_demographics(text: str) -> dict:
    data = {
        "enrollment": {"total": 0, "undergraduate": 0, "graduate": 0},
        "byRace": {
            "international": 0,
            "hispanicLatino": 0,
            "blackAfricanAmerican": 0,
            "white": 0,
            "asian": 0,
            "americanIndianAlaskaNative": 0,
            "nativeHawaiianPacificIslander": 0,
            "twoOrMoreRaces": 0,
            "unknown": 0,
        },
        "byResidency": {"inState": 0, "outOfState": 0, "international": 0},
    }

    undergrad_match = re.search(
        r"(?:Total all undergraduates|Total of all undergraduate students enrolled)\s+(\d{1,3}(?:,\d{3})*)",
        text,
        re.I,
    )
    graduate_match = re.search(
        r"(?:Total all graduate|Total of all graduate students enrolled)\s+(\d{1,3}(?:,\d{3})*)",
        text,
        re.I,
    )
    if undergrad_match:
        data["enrollment"]["undergraduate"] = extract_number(undergrad_match.group(1))
    if graduate_match:
        data["enrollment"]["graduate"] = extract_number(graduate_match.group(1))

    b2_section = find_section(text, "B2", ["B3", "B4", "Persistence"])
    b2_section = re.sub(r"American Indian or Alaska Native, non-\s+Hispanic", "American Indian or Alaska Native, non-Hispanic", b2_section, flags=re.I)
    b2_section = re.sub(r"Native Hawaiian or other Pacific Islander, non-\s+Hispanic", "Native Hawaiian or other Pacific Islander, non-Hispanic", b2_section, flags=re.I)

    mapping = {
        "international": ["Nonresident aliens", "International (nonresidents)", "US nonresidents"],
        "hispanicLatino": ["Hispanic/Latino"],
        "blackAfricanAmerican": ["Black or African American, non-Hispanic"],
        "white": ["White, non-Hispanic"],
        "asian": ["Asian, non-Hispanic"],
        "americanIndianAlaskaNative": ["American Indian or Alaska Native, non-Hispanic"],
        "nativeHawaiianPacificIslander": ["Native Hawaiian or other Pacific Islander, non-Hispanic"],
        "twoOrMoreRaces": ["Two or more races, non-Hispanic"],
        "unknown": ["Race and/or ethnicity unknown"],
    }

    for field, labels in mapping.items():
        for label in labels:
            match = re.search(rf"{re.escape(label)}\s+(.*)", b2_section, re.I)
            if match:
                nums = extract_numbers_no_percent(match.group(1))
                if nums:
                    data["byRace"][field] = nums[-1]
                    break

    by_race_total = sum(data["byRace"].values())
    if by_race_total and abs(by_race_total - data["enrollment"]["undergraduate"]) <= 100:
        data["enrollment"]["undergraduate"] = by_race_total

    out_pct_match = re.search(
        r"out of state.*?(\d+(?:\.\d+)?)%\s+(\d+(?:\.\d+)?)%",
        text,
        re.I | re.S,
    )
    if out_pct_match:
        out_pct = float(out_pct_match.group(2)) / 100
        international = data["byRace"]["international"]
        domestic = data["enrollment"]["undergraduate"] - international
        out_of_state = round(domestic * out_pct)
        data["byResidency"] = {
            "inState": domestic - out_of_state,
            "outOfState": out_of_state,
            "international": international,
        }

    data["enrollment"]["total"] = data["enrollment"]["undergraduate"] + data["enrollment"]["graduate"]
    return data


def extract_costs(text: str) -> dict:
    data = {"tuition": 0, "fees": 0, "roomAndBoard": 0, "totalCOA": 0}
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for i, line in enumerate(lines):
        if "Tuition: In-state:" in line:
            nums = re.findall(r"\$([\d,]+)", line)
            if nums:
                data["tuition"] = extract_number(nums[0])
                break
        if "PUBLIC INSTITUTIONS In-state" in line:
            nums = re.findall(r"\$([\d,]+)", line)
            if nums:
                data["tuition"] = extract_number(nums[0])
                break
        if "In-state (out-of-district):" in line and i > 0:
            nums = re.findall(r"\$([\d,]+)", lines[i - 1])
            if nums:
                data["tuition"] = extract_number(nums[0])
                break

    for i, line in enumerate(lines):
        if "Required Fees (all students):" in line or "REQUIRED FEES:" in line or "REQUIRED FEES (all students)" in line:
            nums = re.findall(r"\$([\d,]+)", line)
            if nums:
                data["fees"] = extract_number(nums[0])
                break

    for i, line in enumerate(lines):
        if "Food and Housing (on-campus):" in line:
            nums = re.findall(r"\$([\d,]+)", line)
            if nums:
                data["roomAndBoard"] = extract_number(nums[0])
                break
        if "FOOD AND HOUSING (on-campus)" in line:
            nums = re.findall(r"\$([\d,]+)", line)
            if nums:
                data["roomAndBoard"] = extract_number(nums[0])
                break
        if "ROOM AND BOARD (on-campus)" in line:
            nums = re.findall(r"\$([\d,]+)", line)
            if nums:
                data["roomAndBoard"] = extract_number(nums[0])
                break
        if "ROOM AND BOARD:" in line and i + 1 < len(lines):
            nums = re.findall(r"\$([\d,]+)", lines[i + 1])
            if nums:
                data["roomAndBoard"] = extract_number(nums[0])
                break

    data["totalCOA"] = data["tuition"] + data["fees"] + data["roomAndBoard"]
    return data


def extract_financial_aid(text: str) -> dict:
    data = {
        "percentReceivingAid": 0,
        "averageAidPackage": 0,
        "averageNeedBasedGrant": 0,
        "percentNeedFullyMet": 0,
    }

    h2_section = ""
    for start_marker in [
        "H2 a)",
        "H2 Number of Enrolled Students Awarded Aid",
        "H2. Number of Enrolled Students Awarded Aid",
    ]:
        h2_section = find_section(text, start_marker, ["H2A", "H4", "H5"])
        if h2_section:
            break
    rows: dict[str, str] = {}
    current_label = None
    current_lines: list[str] = []
    for raw_line in h2_section.splitlines():
        line = " ".join(raw_line.split())
        if not line or "CDS-H Financial Aid Page" in line or "Common Data Set" in line:
            continue
        if line.startswith("H2A"):
            break
        match = re.match(r"^H2\s*([a-m])\)\s*(.*)$", line, re.I)
        if match:
            if current_label:
                rows[current_label] = " ".join(current_lines)
            current_label = match.group(1).upper()
            current_lines = [match.group(2)] if match.group(2) else []
            continue
        match = re.match(r"^([A-M])\.\s*(.*)$", line)
        if match:
            if current_label:
                rows[current_label] = " ".join(current_lines)
            current_label = match.group(1)
            current_lines = [match.group(2)] if match.group(2) else []
            continue
        match = re.match(r"^([A-M])\s+(.*)$", line)
        if match and match.group(2).startswith(("Number", "On average", "The average", "Average")):
            if current_label:
                rows[current_label] = " ".join(current_lines)
            current_label = match.group(1)
            current_lines = [match.group(2)]
            continue
        match = re.match(r"^([A-M])\.?$", line)
        if match:
            if current_label:
                rows[current_label] = " ".join(current_lines)
            current_label = match.group(1)
            current_lines = []
            continue
        if current_label:
            current_lines.append(line)

    if current_label:
        rows[current_label] = " ".join(current_lines)

    def second_value(row_label: str) -> int:
        nums = extract_numbers_no_percent(rows.get(row_label, ""))
        return nums[-2] if len(nums) >= 2 else 0

    students = second_value("A")
    determined_need = second_value("C")
    awarded_aid = second_value("D")
    fully_met = second_value("H")

    if students:
        data["percentReceivingAid"] = round(awarded_aid / students, 4)
    if determined_need:
        data["percentNeedFullyMet"] = round(fully_met / determined_need, 4)

    avg_package = re.findall(r"\$([\d,]+)", rows.get("J", ""))
    avg_grant = re.findall(r"\$([\d,]+)", rows.get("K", ""))
    if len(avg_package) >= 2:
        data["averageAidPackage"] = extract_number(avg_package[1])
    if len(avg_grant) >= 2:
        data["averageNeedBasedGrant"] = extract_number(avg_grant[1])

    return data


def extract_year_data(text: str) -> dict:
    return {
        "admissions": extract_admissions(text),
        "testScores": extract_test_scores(text),
        "demographics": extract_demographics(text),
        "costs": extract_costs(text),
        "financialAid": extract_financial_aid(text),
    }


def main() -> None:
    school_data = {
        "name": "University of Michigan Ann Arbor",
        "slug": "umich",
        "years": {},
    }

    for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
        year = extract_year_from_filename(pdf_path.name)
        text = load_pdf_text(pdf_path)
        school_data["years"][year] = extract_year_data(text)
        admissions = school_data["years"][year]["admissions"]
        print(
            f"{year}: {admissions['applied']:,} applied, "
            f"{admissions['admitted']:,} admitted, {admissions['enrolled']:,} enrolled"
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(school_data, f, indent=2)
        f.write("\n")

    print(f"\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
