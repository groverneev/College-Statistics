#!/usr/bin/env python3
"""
Extract USC Common Data Set data from USC's official archive pages.
"""

from __future__ import annotations

import io
import json
import re
from pathlib import Path
from typing import Callable

import pdfplumber
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.5",
}

YEAR_URLS = {
    "2016-2017": "https://oir.usc.edu/common-data-set-archive/common-data-set-2016-2017/",
    "2017-2018": "https://oir.usc.edu/common-data-set-archive/common-data-set-2017-2018/",
    "2018-2019": "https://oir.usc.edu/common-data-set-archive/common-data-set-2018-2019/",
    "2019-2020": "https://oir.usc.edu/common-data-set-archive/common-data-set-2019-2020/",
    "2020-2021": "https://oir.usc.edu/common-data-set-archive/common-data-set-template/",
    "2021-2022": "https://oir.usc.edu/common-data-set-archive/common-data-set-2021-2022/",
    "2022-2023": "https://oir.usc.edu/common-data-set-archive/common-data-set-2022-2023/",
    "2023-2024": "https://oir.usc.edu/common-data-set-archive/common-data-set-2023-2024/",
    "2024-2025": "https://oir.usc.edu/common-data-set-archive/common-data-set-2024-2025/",
}


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\xa0", " ")).strip()


def parse_int(value: str) -> int:
    match = re.search(r"\d[\d,\s]*", value or "")
    return int(re.sub(r"[,\s]", "", match.group(0))) if match else 0


def parse_money(value: str) -> int:
    return parse_int((value or "").replace("$", ""))


def parse_percent(value: str) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)", value or "")
    return (float(match.group(1)) / 100) if match else 0.0


def fetch_html(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def fetch_html_tables(url: str) -> list[list[list[str]]]:
    soup = fetch_html(url)
    tables: list[list[list[str]]] = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [clean(cell.get_text(" ", strip=True)) for cell in tr.find_all(["th", "td"])]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables


def fetch_pdf_tables(pdf_url: str) -> list[list[list[str]]]:
    response = requests.get(pdf_url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    tables: list[list[list[str]]] = []
    with pdfplumber.open(io.BytesIO(response.content)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                rows = []
                for row in table:
                    cells = [clean(cell or "") for cell in row]
                    if any(cells):
                        rows.append(cells)
                if rows:
                    tables.append(rows)
    return tables


def find_table(tables: list[list[list[str]]], predicate: Callable[[list[list[str]]], bool]) -> list[list[str]]:
    for table in tables:
        if predicate(table):
            return table
    raise ValueError("Required table not found")


def find_row_starts(table: list[list[str]], prefix: str) -> list[str]:
    prefix = prefix.lower()
    for row in table:
        if row and row[0].lower().startswith(prefix):
            return row
    raise ValueError(f"Required row not found: {prefix}")


def find_row_contains(table: list[list[str]], fragment: str) -> list[str]:
    fragment = fragment.lower()
    for row in table:
        if row and fragment in row[0].lower():
            return row
    raise ValueError(f"Required row not found: {fragment}")


def find_row_with_terms(table: list[list[str]], *terms: str) -> list[str]:
    lowered = [term.lower() for term in terms]
    for row in table:
        if row:
            value = row[0].lower()
            if all(term in value for term in lowered):
                return row
    raise ValueError(f"Required row not found: {' | '.join(terms)}")


def build_year_data(
    *,
    applied: int,
    admitted: int,
    enrolled: int,
    men_applied: int,
    women_applied: int,
    men_admitted: int,
    women_admitted: int,
    men_enrolled: int,
    women_enrolled: int,
    sat_submission_rate: float,
    act_submission_rate: float,
    sat_erw: tuple[int, int, int],
    sat_math: tuple[int, int, int],
    act_composite: tuple[int, int, int],
    undergrad: int,
    graduate: int,
    by_race: dict[str, int],
    in_state: int,
    out_of_state: int,
    tuition: int,
    fees: int,
    room_and_board: int,
    aid_population: int,
    aid_recipients: int,
    fully_met: int,
    avg_package: int,
    avg_grant: int,
) -> dict:
    year_data = {
        "admissions": {
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
        },
        "testScores": {},
        "demographics": {
            "enrollment": {
                "total": undergrad + graduate,
                "undergraduate": undergrad,
                "graduate": graduate,
            },
            "byRace": by_race,
            "byResidency": {
                "inState": in_state,
                "outOfState": out_of_state,
                "international": by_race["international"],
            },
        },
        "costs": {
            "tuition": tuition,
            "fees": fees,
            "roomAndBoard": room_and_board,
            "totalCOA": tuition + fees + room_and_board,
        },
        "financialAid": {
            "percentReceivingAid": round(aid_recipients / aid_population, 4) if aid_population else 0,
            "averageAidPackage": avg_package,
            "averageNeedBasedGrant": avg_grant,
            "percentNeedFullyMet": round(fully_met / aid_recipients, 4) if aid_recipients else 0,
        },
    }

    if sat_submission_rate > 0 and any(sat_erw) and any(sat_math):
        year_data["testScores"]["sat"] = {
            "composite": {
                "p25": sat_erw[0] + sat_math[0],
                "p50": sat_erw[1] + sat_math[1],
                "p75": sat_erw[2] + sat_math[2],
            },
            "readingWriting": {
                "p25": sat_erw[0],
                "p50": sat_erw[1],
                "p75": sat_erw[2],
            },
            "math": {
                "p25": sat_math[0],
                "p50": sat_math[1],
                "p75": sat_math[2],
            },
            "submissionRate": sat_submission_rate,
        }

    if act_submission_rate > 0 and any(act_composite):
        year_data["testScores"]["act"] = {
            "composite": {
                "p25": act_composite[0],
                "p50": act_composite[1],
                "p75": act_composite[2],
            },
            "submissionRate": act_submission_rate,
        }

    return year_data


def extract_from_html_tables(tables: list[list[list[str]]]) -> dict:
    applied_table = find_table(tables, lambda t: any(row and "men who applied" in row[0].lower() for row in t))
    admitted_table = find_table(tables, lambda t: any(row and "men who were admitted" in row[0].lower() for row in t))
    men_enrolled_table = find_table(tables, lambda t: any(row and "men who enrolled" in row[0].lower() for row in t))
    women_enrolled_table = find_table(tables, lambda t: any(row and "women who enrolled" in row[0].lower() for row in t))

    men_applied = parse_int(find_row_contains(applied_table, "men who applied")[1])
    women_applied = parse_int(find_row_contains(applied_table, "women who applied")[1])
    men_admitted = parse_int(find_row_contains(admitted_table, "men who were admitted")[1])
    women_admitted = parse_int(find_row_contains(admitted_table, "women who were admitted")[1])
    men_enrolled = parse_int(find_row_with_terms(men_enrolled_table, "full-time", "men who enrolled")[1])
    men_enrolled += parse_int(find_row_with_terms(men_enrolled_table, "part-time", "men who enrolled")[1])
    women_enrolled = parse_int(find_row_with_terms(women_enrolled_table, "full-time", "women who enrolled")[1])
    women_enrolled += parse_int(find_row_with_terms(women_enrolled_table, "part-time", "women who enrolled")[1])

    applied = men_applied + women_applied
    admitted = men_admitted + women_admitted
    enrolled = men_enrolled + women_enrolled

    submissions = find_table(tables, lambda t: t and t[0][:3] == ["", "Percent", "Number"] and any("Submitting SAT Scores" in " ".join(row) for row in t))
    sat_submission_rate = parse_percent(find_row_starts(submissions, "Submitting SAT Scores")[1])
    act_submission_rate = parse_percent(find_row_starts(submissions, "Submitting ACT Scores")[1])

    scores = find_table(tables, lambda t: t and t[0] and t[0][0] == "Assessment")
    sat_erw_row = find_row_contains(scores, "SAT Evidence-Based Reading")
    sat_math_row = find_row_starts(scores, "SAT Math")
    act_row = find_row_starts(scores, "ACT Composite")
    if len(sat_erw_row) >= 4:
        sat_erw = (parse_int(sat_erw_row[1]), parse_int(sat_erw_row[2]), parse_int(sat_erw_row[3]))
        sat_math = (parse_int(sat_math_row[1]), parse_int(sat_math_row[2]), parse_int(sat_math_row[3]))
        act_composite = (parse_int(act_row[1]), parse_int(act_row[2]), parse_int(act_row[3]))
    else:
        sat_erw = (parse_int(sat_erw_row[1]), (parse_int(sat_erw_row[1]) + parse_int(sat_erw_row[2])) // 2, parse_int(sat_erw_row[2]))
        sat_math = (parse_int(sat_math_row[1]), (parse_int(sat_math_row[1]) + parse_int(sat_math_row[2])) // 2, parse_int(sat_math_row[2]))
        act_composite = (parse_int(act_row[1]), (parse_int(act_row[1]) + parse_int(act_row[2])) // 2, parse_int(act_row[2]))

    b1 = find_table(tables, lambda t: any(row and row[0] == "Total graduate" for row in t))
    b2 = find_table(tables, lambda t: t and any(row and row[0] == "TOTAL" for row in t) and "Degree-Seeking Undergraduates" in " ".join(t[0]))
    f1 = find_table(tables, lambda t: any(row and row[0].startswith("Percent who are from out of state") for row in t))
    g1 = find_table(tables, lambda t: any(row and row[0] == "Tuition:" for row in t) and any(row and row[0] == "Required Fees" for row in t))
    h2_part1 = find_table(tables, lambda t: t and len(t[0]) >= 4 and "Full-time Undergrad" in " ".join(t[0]) and any(row and row[0] == "A" for row in t))
    h2_part2 = find_table(tables, lambda t: any(row and row[0] == "J" for row in t))

    undergrad = parse_int(find_row_starts(b2, "TOTAL")[3])
    graduate = sum(parse_int(cell) for cell in find_row_starts(b1, "Total graduate")[1:])

    race_map = {
        "Nonresident": "international",
        "Hispanic/Latino": "hispanicLatino",
        "Black or African American, non-Hispanic": "blackAfricanAmerican",
        "White, non-Hispanic": "white",
        "Asian, non-Hispanic": "asian",
        "American Indian or Alaska Native, non-Hispanic": "americanIndianAlaskaNative",
        "Native Hawaiian or other Pacific Islander": "nativeHawaiianPacificIslander",
        "Two or more races, non-Hispanic": "twoOrMoreRaces",
        "Race and/or ethnicity unknown": "unknown",
    }
    by_race = {key: parse_int(find_row_contains(b2, label)[3]) for label, key in race_map.items()}

    domestic = undergrad - by_race["international"]
    out_of_state = round(domestic * parse_percent(find_row_starts(f1, "Percent who are from out of state")[2]))
    in_state = domestic - out_of_state

    tuition = parse_money(find_row_starts(g1, "Tuition:")[1]) or parse_money(find_row_contains(g1, "PRIVATE INSTITUTIONS")[1])
    fees = parse_money(find_row_starts(g1, "Required Fees")[1])
    room_and_board = parse_money(find_row_starts(g1, "Room and Board")[1])

    aid_population = parse_int(find_row_starts(h2_part1, "A")[3])
    aid_recipients = parse_int(find_row_starts(h2_part1, "D")[3])
    fully_met = parse_int(find_row_starts(h2_part1, "H")[3])
    avg_package = parse_money(find_row_starts(h2_part2, "J")[3])
    avg_grant = parse_money(find_row_starts(h2_part2, "K")[3])

    return build_year_data(
        applied=applied,
        admitted=admitted,
        enrolled=enrolled,
        men_applied=men_applied,
        women_applied=women_applied,
        men_admitted=men_admitted,
        women_admitted=women_admitted,
        men_enrolled=men_enrolled,
        women_enrolled=women_enrolled,
        sat_submission_rate=sat_submission_rate,
        act_submission_rate=act_submission_rate,
        sat_erw=sat_erw,
        sat_math=sat_math,
        act_composite=act_composite,
        undergrad=undergrad,
        graduate=graduate,
        by_race=by_race,
        in_state=in_state,
        out_of_state=out_of_state,
        tuition=tuition,
        fees=fees,
        room_and_board=room_and_board,
        aid_population=aid_population,
        aid_recipients=aid_recipients,
        fully_met=fully_met,
        avg_package=avg_package,
        avg_grant=avg_grant,
    )


def extract_from_pdf_page(page_url: str) -> dict:
    soup = fetch_html(page_url)
    pdf_url = next((a["href"] for a in soup.find_all("a", href=True) if a["href"].lower().endswith(".pdf")), None)
    if not pdf_url:
        raise ValueError("PDF link not found on USC page")

    tables = fetch_pdf_tables(pdf_url)

    applied_table = find_table(tables, lambda t: any(row and "men who applied" in row[0].lower() for row in t))
    admitted_table = find_table(tables, lambda t: any(row and "men who were admitted" in row[0].lower() for row in t))
    men_enrolled_table = find_table(tables, lambda t: any(row and "men who enrolled" in row[0].lower() for row in t))
    women_enrolled_table = find_table(tables, lambda t: any(row and "women who enrolled" in row[0].lower() for row in t))
    submissions = find_table(tables, lambda t: any(row and row[0] == "Percent submitting SAT scores" for row in t))
    scores = find_table(
        tables,
        lambda t: any(row and "SAT Math" in row[0] for row in t)
        and any(
            row and (
                "SAT Evidence-Based Reading" in row[0]
                or "SAT Critical Reading" in row[0]
            )
            for row in t
        ),
    )
    b1 = find_table(tables, lambda t: any(row and row[0] == "Total undergraduates" for row in t) and any(row and row[0] == "Total graduate" for row in t))
    b2 = find_table(tables, lambda t: any(row and row[0] == "TOTAL" for row in t) and any(row and "Nonresident" in row[0] for row in t))
    f1 = find_table(tables, lambda t: any(row and "Percent who are from out of state" in row[0] for row in t))
    g1 = find_table(tables, lambda t: any(row and "Tuition:" in row[0] for row in t) and any(row and "REQUIRED FEES:" in row[0] for row in t))
    h2_part1 = find_table(tables, lambda t: any(row and row[0].startswith("a)") for row in t))
    h2_part2 = find_table(tables, lambda t: any(row and "average financial aid package" in row[0].lower() for row in t))

    men_applied = parse_int(find_row_contains(applied_table, "men who applied")[1])
    women_applied = parse_int(find_row_contains(applied_table, "women who applied")[1])
    men_admitted = parse_int(find_row_contains(admitted_table, "men who were admitted")[1])
    women_admitted = parse_int(find_row_contains(admitted_table, "women who were admitted")[1])
    men_enrolled = parse_int(find_row_with_terms(men_enrolled_table, "full-time", "men who enrolled")[1]) + parse_int(find_row_with_terms(men_enrolled_table, "part-time", "men who enrolled")[1])
    women_enrolled = parse_int(find_row_with_terms(women_enrolled_table, "full-time", "women who enrolled")[1]) + parse_int(find_row_with_terms(women_enrolled_table, "part-time", "women who enrolled")[1])

    sat_submission_rate = parse_percent(find_row_starts(submissions, "Percent submitting SAT scores")[1])
    act_submission_rate = parse_percent(find_row_starts(submissions, "Percent submitting ACT scores")[1])

    try:
        sat_erw_row = find_row_contains(scores, "SAT Evidence-Based Reading")
    except ValueError:
        sat_erw_row = find_row_contains(scores, "SAT Critical Reading")
    sat_math_row = find_row_starts(scores, "SAT Math")
    act_row = find_row_starts(scores, "ACT Composite")
    sat_erw = (parse_int(sat_erw_row[1]), (parse_int(sat_erw_row[1]) + parse_int(sat_erw_row[2])) // 2, parse_int(sat_erw_row[2]))
    sat_math = (parse_int(sat_math_row[1]), (parse_int(sat_math_row[1]) + parse_int(sat_math_row[2])) // 2, parse_int(sat_math_row[2]))
    act_composite = (parse_int(act_row[1]), (parse_int(act_row[1]) + parse_int(act_row[2])) // 2, parse_int(act_row[2]))

    undergrad = parse_int(find_row_starts(b2, "TOTAL")[3])
    graduate = sum(parse_int(cell) for cell in find_row_starts(b1, "Total graduate")[1:])

    race_map = {
        "Nonresident": "international",
        "Hispanic/Latino": "hispanicLatino",
        "Black or African American, non-Hispanic": "blackAfricanAmerican",
        "White, non-Hispanic": "white",
        "Asian, non-Hispanic": "asian",
        "American Indian or Alaska Native, non-Hispanic": "americanIndianAlaskaNative",
        "Native Hawaiian or other Pacific Islander": "nativeHawaiianPacificIslander",
        "Two or more races, non-Hispanic": "twoOrMoreRaces",
        "Race and/or ethnicity unknown": "unknown",
    }
    by_race = {key: parse_int(find_row_contains(b2, label)[3]) for label, key in race_map.items()}

    domestic = undergrad - by_race["international"]
    out_of_state = round(domestic * parse_percent(find_row_contains(f1, "Percent who are from out of state")[2]))
    in_state = domestic - out_of_state

    tuition = parse_money(find_row_contains(g1, "Tuition:")[1])
    fees = parse_money(find_row_contains(g1, "REQUIRED FEES")[1])
    room_and_board = parse_money(find_row_contains(g1, "ROOM AND BOARD")[1])

    aid_population = parse_int(find_row_contains(h2_part1, "degree-seeking undergraduate students")[2])
    aid_recipients = parse_int(find_row_contains(h2_part2, "awarded any financial aid")[2])
    fully_met = parse_int(find_row_contains(h2_part2, "need was fully met")[2])
    avg_package = parse_money(find_row_contains(h2_part2, "average financial aid package")[2])
    avg_grant = parse_money(find_row_contains(h2_part2, "need-based scholarship and grant award")[2])

    return build_year_data(
        applied=men_applied + women_applied,
        admitted=men_admitted + women_admitted,
        enrolled=men_enrolled + women_enrolled,
        men_applied=men_applied,
        women_applied=women_applied,
        men_admitted=men_admitted,
        women_admitted=women_admitted,
        men_enrolled=men_enrolled,
        women_enrolled=women_enrolled,
        sat_submission_rate=sat_submission_rate,
        act_submission_rate=act_submission_rate,
        sat_erw=sat_erw,
        sat_math=sat_math,
        act_composite=act_composite,
        undergrad=undergrad,
        graduate=graduate,
        by_race=by_race,
        in_state=in_state,
        out_of_state=out_of_state,
        tuition=tuition,
        fees=fees,
        room_and_board=room_and_board,
        aid_population=aid_population,
        aid_recipients=aid_recipients,
        fully_met=fully_met,
        avg_package=avg_package,
        avg_grant=avg_grant,
    )


def extract_year(url: str) -> dict:
    year = int(url.rsplit("-", 2)[-2]) if "template" not in url else 2020
    if year <= 2019:
        return extract_from_pdf_page(url)
    tables = fetch_html_tables(url)
    return extract_from_html_tables(tables)


def main() -> None:
    school_data = {
        "name": "University of Southern California",
        "slug": "usc",
        "years": {year: extract_year(url) for year, url in YEAR_URLS.items()},
    }

    output_path = Path("src/data/schools/usc.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(school_data, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {output_path}")
    for year, data in school_data["years"].items():
        ug = data["demographics"]["enrollment"]["undergraduate"]
        race_total = sum(data["demographics"]["byRace"].values())
        residency_total = sum(data["demographics"]["byResidency"].values())
        print(year, data["admissions"]["applied"], ug, race_total, residency_total)
        if race_total != ug or residency_total != ug:
            raise ValueError(f"Consistency check failed for {year}")


if __name__ == "__main__":
    main()
