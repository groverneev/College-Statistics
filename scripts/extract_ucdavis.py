#!/usr/bin/env python3
"""
Build the UC Davis dataset from official CDS PDFs.

UC Davis uses a mix of older CDS layouts, a 2020 transitional PDF, and newer
2023/2024 templates. This extractor normalizes the fields we surface on the
site and writes `src/data/schools/ucdavis.json`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber


YEAR_FILES = {
    "2016-2017": "2016-17.pdf",
    "2017-2018": "2017-18.pdf",
    "2018-2019": "2018-19-full.pdf",
    "2020-2021": "2020-21.pdf",
    "2023-2024": "2023-24.pdf",
    "2024-2025": "2024-25.pdf",
}

CostOverride = dict[str, int]

OFFICIAL_COSTS: dict[str, CostOverride] = {
    "2016-2017": {"tuition": 11502, "fees": 2880, "roomAndBoard": 16136},
    "2017-2018": {"tuition": 11502, "fees": 2961, "roomAndBoard": 15765},
    "2018-2019": {"tuition": 11442, "fees": 3050, "roomAndBoard": 15863},
    "2020-2021": {"tuition": 11442, "fees": 3212, "roomAndBoard": 16480},
    "2023-2024": {"tuition": 13146, "fees": 3618, "roomAndBoard": 19426},
    "2024-2025": {"tuition": 13602, "fees": 3749, "roomAndBoard": 20771},
}


WEB_YEAR_OVERRIDES: dict[str, dict] = {
    "2019-2020": {
        "admissions": {
            "applied": 78093,
            "admitted": 31035,
            "enrolled": 5957,
            "acceptanceRate": 0.3974,
            "yield": 0.1919,
        },
        "testScores": {
            "sat": {
                "composite": {"p25": 1145, "p50": 1275, "p75": 1405},
                "readingWriting": {"p25": 565, "p50": 620, "p75": 670},
                "math": {"p25": 580, "p50": 660, "p75": 735},
                "submissionRate": 0.74,
            },
            "act": {
                "composite": {"p25": 25, "p50": 28, "p75": 31},
                "submissionRate": 0.26,
            },
        },
        "demographics": {
            "enrollment": {
                "total": 39629,
                "undergraduate": 30982,
                "graduate": 8647,
            },
            "byRace": {
                "international": 5190,
                "hispanicLatino": 6974,
                "blackAfricanAmerican": 1181,
                "white": 7004,
                "americanIndianAlaskaNative": 187,
                "asian": 10018,
                "nativeHawaiianPacificIslander": 0,
                "twoOrMoreRaces": 0,
                "unknown": 428,
            },
            "byResidency": {
                "inState": 25470,
                "outOfState": 1041,
                "international": 4471,
            },
        },
        "costs": {
            "tuition": 11442,
            "fees": 3053,
            "roomAndBoard": 15863,
            "totalCOA": 30358,
        },
        "financialAid": {
            "percentReceivingAid": 0.5677,
            "averageAidPackage": 21848,
            "averageNeedBasedGrant": 19310,
            "percentNeedFullyMet": 0.2086,
        },
    },
    "2021-2022": {
        "admissions": {
            "applied": 87136,
            "admitted": 42474,
            "enrolled": 7482,
            "acceptanceRate": 0.4874,
            "yield": 0.1762,
        },
        "testScores": {},
        "demographics": {
            "enrollment": {
                "total": 41155,
                "undergraduate": 31657,
                "graduate": 9498,
            },
            "byRace": {
                "international": 4905,
                "hispanicLatino": 7146,
                "blackAfricanAmerican": 1188,
                "white": 6772,
                "americanIndianAlaskaNative": 106,
                "asian": 10705,
                "nativeHawaiianPacificIslander": 111,
                "twoOrMoreRaces": 0,
                "unknown": 724,
            },
            "byResidency": {
                "inState": 26168,
                "outOfState": 1286,
                "international": 4203,
            },
        },
        "costs": {
            "tuition": 11442,
            "fees": 3203,
            "roomAndBoard": 17018,
            "totalCOA": 31663,
        },
        "financialAid": {
            "percentReceivingAid": 0.7122,
            "averageAidPackage": 25311,
            "averageNeedBasedGrant": 22005,
            "percentNeedFullyMet": 0.2114,
        },
    },
    "2022-2023": {
        "admissions": {
            "applied": 94748,
            "admitted": 35377,
            "enrolled": 6399,
            "acceptanceRate": 0.3734,
            "yield": 0.1809,
        },
        "testScores": {},
        "demographics": {
            "enrollment": {
                "total": 40772,
                "undergraduate": 31532,
                "graduate": 9240,
            },
            "byRace": {
                "international": 4216,
                "hispanicLatino": 7223,
                "blackAfricanAmerican": 1120,
                "white": 6708,
                "americanIndianAlaskaNative": 116,
                "asian": 11287,
                "nativeHawaiianPacificIslander": 109,
                "twoOrMoreRaces": 0,
                "unknown": 753,
            },
            "byResidency": {
                "inState": 25896,
                "outOfState": 1506,
                "international": 4130,
            },
        },
        "costs": {
            "tuition": 11928,
            "fees": 3330,
            "roomAndBoard": 17692,
            "totalCOA": 32950,
        },
        "financialAid": {
            "percentReceivingAid": 0.6811,
            "averageAidPackage": 25371,
            "averageNeedBasedGrant": 21623,
            "percentNeedFullyMet": 0.2292,
        },
    },
}


PDF_YEAR_OVERRIDES: dict[str, dict] = {
    # UC Davis's public enrollment dashboards provide much cleaner race and
    # residency counts than the 2020 transitional CDS PDF extraction.
    "2020-2021": {
        "demographics": {
            "enrollment": {
                "total": 40031,
                "undergraduate": 31162,
                "graduate": 8869,
            },
            "byRace": {
                "international": 5124,
                "hispanicLatino": 7159,
                "blackAfricanAmerican": 1209,
                "white": 6663,
                "americanIndianAlaskaNative": 179,
                "asian": 10385,
                "nativeHawaiianPacificIslander": 0,
                "twoOrMoreRaces": 0,
                "unknown": 443,
            },
            "byResidency": {
                "inState": 25759,
                "outOfState": 1035,
                "international": 4368,
            },
        },
    },
}


def squish(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_number(value: str | None) -> int:
    if not value:
        return 0
    cleaned = re.sub(r"[^0-9.]", "", value)
    if not cleaned:
        return 0
    return int(round(float(cleaned)))


def parse_percent(value: str | None) -> float:
    if not value:
        return 0.0
    cleaned = value.replace("%", "").strip()
    if not cleaned:
        return 0.0
    return float(cleaned) / 100


def numbers_from_row(row: list[str | None]) -> list[int]:
    numbers: list[int] = []
    for cell in row:
        if cell is None:
            continue
        matches = re.findall(r"\$?\s*[\d][\d,\.\s]*", str(cell))
        for match in matches:
            value = parse_number(match)
            if value:
                numbers.append(value)
    return numbers


def find_table_row(pages: list[dict], pattern: str) -> list[str | None] | None:
    regex = re.compile(pattern, re.IGNORECASE)
    for page in pages:
        for table in page["tables"]:
            for row in table:
                row_text = " ".join(str(cell) for cell in row if cell)
                if regex.search(row_text):
                    return row
    return None


def find_best_row_values(pages: list[dict], pattern: str) -> list[int]:
    regex = re.compile(pattern, re.IGNORECASE)
    best: list[int] = []
    for page in pages:
        for table in page["tables"]:
            for row in table:
                row_text = " ".join(str(cell) for cell in row if cell)
                if not regex.search(row_text):
                    continue
                values = numbers_from_row(row)
                if len(values) > len(best) or (len(values) == len(best) and sum(values) > sum(best)):
                    best = values
    return best


def find_row_values(pages: list[dict], pattern: str) -> list[int]:
    row = find_table_row(pages, pattern)
    return numbers_from_row(row) if row else []


def load_pages(pdf_path: Path) -> list[dict]:
    pages: list[dict] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            pages.append(
                {
                    "text": page.extract_text() or "",
                    "tables": page.extract_tables() or [],
                }
            )
    return pages


def extract_admissions(text: str, year: str) -> dict:
    if year == "2023-2024":
        applied_match = re.search(
            r"Total first-time, first-year students who applied in Fall 2023\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
            text,
        )
        admitted_match = re.search(
            r"Total first-time, first-year students admitted in Fall 2023\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
            text,
        )
        enrolled_match = re.search(
            r"Total first-time, first-year students enrolled in Fall 2023\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
            text,
        )
        applied = sum(parse_number(group) for group in applied_match.groups())
        admitted = sum(parse_number(group) for group in admitted_match.groups())
        enrolled = sum(parse_number(group) for group in enrolled_match.groups())
    else:
        def sum_matches(patterns: list[str]) -> int:
            total = 0
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    total += parse_number(match.group(1))
            return total

        applied = sum_matches(
            [
                r"Total first-time, first-year(?: \(freshman\))? men who applied\s+([\d,\.\s]+)",
                r"Total first-time, first-year(?: \(freshman\))? women who applied\s+([\d,\.\s]+)",
                r"Total first-time, first-year another gender who applied\s+([\d,\.\s]+)",
            ]
        )
        admitted = sum_matches(
            [
                r"Total first-time, first-year(?: \(freshman\))? men who were admitted\s+([\d,\.\s]+)",
                r"Total first-time, first-year(?: \(freshman\))? women who were admitted\s+([\d,\.\s]+)",
                r"Total first-time, first-year another gender who were admitted\s+([\d,\.\s]+)",
            ]
        )
        enrolled = sum_matches(
            [
                r"Total full-time, first-time, first-year(?: \(freshman\))? men who enrolled\s+([\d,\.\s]+)",
                r"Total part-time, first-time, first-year(?: \(freshman\))? men who enrolled\s+([\d,\.\s]+)",
                r"Total full-time, first-time, first-year(?: \(freshman\))? women who enrolled\s+([\d,\.\s]+)",
                r"Total part-time, first-time, first-year(?: \(freshman\))? women who enrolled\s+([\d,\.\s]+)",
                r"Total full-time, first-time, first-year another gender who enrolled\s+([\d,\.\s]+)",
                r"Total part-time, first-time, first-year another gender who enrolled\s+([\d,\.\s]+)",
            ]
        )

    return {
        "applied": applied,
        "admitted": admitted,
        "enrolled": enrolled,
        "acceptanceRate": round(admitted / applied, 4) if applied else 0,
        "yield": round(enrolled / admitted, 4) if admitted else 0,
    }


def extract_test_scores(text: str, pages: list[dict], year: str) -> dict:
    if year in {"2023-2024", "2024-2025"}:
        return {}

    sat_submit_match = re.search(
        r"(?:Percent submitting SAT scores|Submitting SAT Scores)\s+(\d+(?:\.\d+)?)%",
        text,
        re.IGNORECASE,
    )
    act_submit_match = re.search(
        r"(?:Percent submitting ACT scores|Submitting ACT Scores)\s+(\d+(?:\.\d+)?)%",
        text,
        re.IGNORECASE,
    )

    sat_rw_row = find_table_row(pages, r"SAT (?:Evidence-Based Reading(?: and Writing)?|Critical Reading)")
    sat_math_row = find_table_row(pages, r"SAT Math")
    sat_composite_row = find_table_row(pages, r"SAT Composite")
    act_row = find_table_row(pages, r"ACT Composite")

    data: dict = {}

    if sat_rw_row and sat_math_row:
        rw_vals = numbers_from_row(sat_rw_row)
        math_vals = numbers_from_row(sat_math_row)
        comp_vals = numbers_from_row(sat_composite_row) if sat_composite_row else []
        if len(rw_vals) >= 2 and len(math_vals) >= 2:
            rw25, rw75 = rw_vals[:2]
            math25, math75 = math_vals[:2]
            if len(comp_vals) >= 2:
                comp25, comp75 = comp_vals[:2]
            else:
                comp25 = rw25 + math25
                comp75 = rw75 + math75
            data["sat"] = {
                "composite": {"p25": comp25, "p50": (comp25 + comp75) // 2, "p75": comp75},
                "readingWriting": {"p25": rw25, "p50": (rw25 + rw75) // 2, "p75": rw75},
                "math": {"p25": math25, "p50": (math25 + math75) // 2, "p75": math75},
                "submissionRate": round(parse_percent(sat_submit_match.group(1)) if sat_submit_match else 0, 4),
            }

    if act_row:
        act_vals = numbers_from_row(act_row)
        if len(act_vals) >= 2:
            act25, act75 = act_vals[:2]
            data["act"] = {
                "composite": {"p25": act25, "p50": (act25 + act75) // 2, "p75": act75},
                "submissionRate": round(parse_percent(act_submit_match.group(1)) if act_submit_match else 0, 4),
            }

    return data


def extract_enrollment(pages: list[dict]) -> dict:
    undergrad_values = find_best_row_values(pages, r"Total undergraduate")
    graduate_values = find_best_row_values(pages, r"Total graduate")

    undergraduate = sum(undergrad_values)
    graduate = sum(graduate_values)
    return {
        "total": undergraduate + graduate,
        "undergraduate": undergraduate,
        "graduate": graduate,
    }


def extract_by_race(text: str, pages: list[dict], year: str, undergraduate: int) -> dict:
    if year == "2023-2024":
        flat = squish(text.replace("\u00ad", "-").replace("\u0002", " "))
        patterns = {
            "international": [r"International \(nonresidents\)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)"],
            "hispanicLatino": [r"Hispanic/Latino\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)"],
            "blackAfricanAmerican": [r"Black or African American, non-Hispanic\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)"],
            "white": [r"White, non-Hispanic\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)"],
            "americanIndianAlaskaNative": [r"American Indian or Alaska Native, non\W*Hispanic\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)"],
            "asian": [r"Asian, non-Hispanic\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)"],
            "nativeHawaiianPacificIslander": [r"Native Hawaiian or other Pacific Islander,?\s*non\W*Hispanic\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)"],
            "twoOrMoreRaces": [r"Two or more races, non-Hispanic\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)"],
            "unknown": [r"Race and/or ethnicity unknown\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)"],
        }

        result: dict[str, int] = {}
        for field, options in patterns.items():
            value = 0
            for pattern in options:
                match = re.search(pattern, flat, re.IGNORECASE)
                if match:
                    value = parse_number(match.groups()[-1])
                    break
            result[field] = value
    else:
        label_patterns = {
            "international": r"International \(nonresidents\)|Nonresidents|Nonresident aliens",
            "hispanicLatino": r"Hispanic/Latino",
            "blackAfricanAmerican": r"Black or African American, non-Hispanic",
            "white": r"White, non-Hispanic",
            "americanIndianAlaskaNative": r"American Indian or Alaska Native, non",
            "asian": r"Asian, non-Hispanic",
            "nativeHawaiianPacificIslander": r"Native Hawaiian or other Pacific Islander",
            "twoOrMoreRaces": r"Two or more races, non-Hispanic",
            "unknown": r"Race and/or ethnicity unknown",
        }

        result = {}
        for field, pattern in label_patterns.items():
            values = find_best_row_values(pages, pattern)
            result[field] = values[1] if len(values) >= 2 else (values[-1] if values else 0)

    # Older UC Davis B2 tables omit some non-degree undergrads from the racial
    # breakdown, so roll the remainder into unknown to keep chart totals aligned.
    gap = undergraduate - sum(result.values())
    if gap > 0:
        result["unknown"] += gap

    return result


def extract_residency(text: str, undergraduate: int, international: int) -> dict:
    flat = squish(text)
    match = re.search(
        r"Percent who are from out of state.*?(\d+(?:\.\d+)?)%\s+(\d+(?:\.\d+)?)%",
        flat,
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


def extract_costs(text: str, pages: list[dict], year: str) -> dict:
    override = OFFICIAL_COSTS[year]
    return {
        **override,
        "totalCOA": override["tuition"] + override["fees"] + override["roomAndBoard"],
    }


def extract_h2_rows(pages: list[dict]) -> dict[str, list[int]]:
    rows: dict[str, list[int]] = {}
    for page in pages:
        page_text = page["text"]
        if "Number of Enrolled Students Awarded Aid" not in page_text and "H2" not in page_text:
            continue
        for table in page["tables"]:
            for row in table:
                cells = [str(cell).strip() for cell in row if cell not in (None, "")]
                if not cells:
                    continue
                first = cells[0]
                key = None
                if re.match(r"^[A-Qa-q]$", first):
                    key = first.upper()
                else:
                    match = re.match(r"^([A-Qa-q])(?:[.)])\s", first)
                    if match:
                        key = match.group(1).upper()
                if not key:
                    continue
                values = numbers_from_row(row)
                if len(values) >= 3:
                    rows[key] = values[-3:]
    return rows


def extract_financial_aid(text: str, pages: list[dict]) -> dict:
    h2_rows = extract_h2_rows(pages)

    total = h2_rows.get("A", [0, 0, 0])[1]
    awarded = h2_rows.get("D", [0, 0, 0])[1]
    met = h2_rows.get("H", [0, 0, 0])[1]
    package = h2_rows.get("J", [0, 0, 0])[1]
    grant = h2_rows.get("K", [0, 0, 0])[1]
    if not grant:
        grant_values = find_best_row_values(pages, r"Average need-based scholarship")
        grant = grant_values[1] if len(grant_values) >= 2 else 0

    return {
        "percentReceivingAid": round(awarded / total, 4) if total else 0,
        "averageAidPackage": package,
        "averageNeedBasedGrant": grant,
        "percentNeedFullyMet": round(met / awarded, 4) if awarded else 0,
    }


def build_year_data(pdf_path: Path, year: str) -> dict:
    pages = load_pages(pdf_path)
    text = "\n".join(page["text"] for page in pages)
    enrollment = extract_enrollment(pages)
    by_race = extract_by_race(text, pages, year, enrollment["undergraduate"])

    return {
        "admissions": extract_admissions(text, year),
        "testScores": extract_test_scores(text, pages, year),
        "demographics": {
            "enrollment": enrollment,
            "byRace": by_race,
            "byResidency": extract_residency(text, enrollment["undergraduate"], by_race["international"]),
        },
        "costs": extract_costs(text, pages, year),
        "financialAid": extract_financial_aid(text, pages),
    }


def deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def main() -> None:
    base_dir = Path("College-Data/UCDavis")
    output_path = Path("src/data/schools/ucdavis.json")

    years: dict[str, dict] = {}

    for year, filename in YEAR_FILES.items():
        year_data = build_year_data(base_dir / filename, year)
        if year in PDF_YEAR_OVERRIDES:
            year_data = deep_merge(year_data, PDF_YEAR_OVERRIDES[year])
        years[year] = year_data

    for year, year_data in WEB_YEAR_OVERRIDES.items():
        years[year] = year_data

    ordered_years = {
        year: years[year]
        for year in sorted(years.keys(), key=lambda value: int(value.split("-")[0]))
    }

    school_data = {
        "name": "University of California, Davis",
        "slug": "ucdavis",
        "years": ordered_years,
    }

    output_path.write_text(json.dumps(school_data, indent=2) + "\n")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
