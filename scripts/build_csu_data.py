from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "College-Data" / "csu" / "raw"
OUT = ROOT / "src" / "data" / "csu" / "generated.ts"

FALL_YEARS = [2021, 2022, 2023, 2024, 2025]

LEVEL_CODE = {"First-Time Freshmen": "F", "Undergraduate Transfers": "U"}

NOT_A_CAMPUS = {"CalStateTEACH"}

MIN_APPLICANTS_FOR_RANKING = 250

RANKING_SIZE = 40


class SourceError(RuntimeError):
    pass


def read_rows(filename: str) -> list[list[str]]:
    path = RAW / filename
    if not path.exists():
        raise SourceError(f"missing raw export: {path.relative_to(ROOT)}")
    with path.open(encoding="utf-16") as handle:
        return [row for row in csv.reader(handle, delimiter="\t")]


def parse_number(value: str | None) -> int | float | None:
    text = (value or "").strip().replace(",", "")
    if not text or text == "-":
        return None
    if text.endswith("%"):
        try:
            return float(text[:-1])
        except ValueError:
            return None
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return None


def forward_fill(row: list[str]) -> list[str]:
    filled: list[str] = []
    last = ""
    for cell in row:
        cell = cell.strip()
        if cell:
            last = cell
        filled.append(last)
    return filled


def fall_year(label: str) -> int | None:
    match = re.search(r"\d{4}", label)
    return int(match.group()) if match else None


def measure_key(label: str) -> str:
    key = label.strip().rstrip(":").lower()
    return {"app": "applied", "admit": "admitted", "enroll": "enrolled"}.get(key, key)


def year_columns(header_year: list[str], header_measure: list[str], start: int) -> Iterator[tuple[int, int, str]]:
    for i in range(start, len(header_year)):
        year = fall_year(header_year[i]) if i < len(header_year) else None
        measure = measure_key(header_measure[i]) if i < len(header_measure) else ""
        if year is None or not measure:
            continue
        yield i, year, measure


def parse_admissions(filename: str) -> dict[str, dict[int, dict[str, Any]]]:
    rows = read_rows(filename)
    if len(rows) < 3:
        raise SourceError(f"{filename}: expected a two-row header and at least one data row")
    header_year, header_measure = forward_fill(rows[0]), rows[1]

    parsed: dict[str, dict[int, dict[str, Any]]] = {}
    for row in rows[2:]:
        if not row or not row[0].strip():
            continue
        record: dict[int, dict[str, Any]] = {}
        for i, year, measure in year_columns(header_year, header_measure, 1):
            record.setdefault(year, {})[measure] = parse_number(row[i])
        parsed[row[0].strip()] = record
    if not parsed:
        raise SourceError(f"{filename}: no data rows found")
    return parsed


def parse_disciplines() -> list[dict[str, Any]]:
    rows = read_rows("discipline-admissions.csv")
    header_year, header_measure = forward_fill(rows[0]), rows[1]

    parsed: list[dict[str, Any]] = []
    for row in rows[2:]:
        if len(row) < 5 or not row[0].strip():
            continue
        level = LEVEL_CODE.get(row[3].strip())
        if level is None:
            continue
        years: dict[int, dict[str, Any]] = {}
        for i, year, measure in year_columns(header_year, header_measure, 4):
            years.setdefault(year, {})[measure] = parse_number(row[i])
        parsed.append(
            {
                "campus": row[0].strip(),
                "area": row[1].strip(),
                "major": row[2].strip(),
                "level": level,
                "years": years,
            }
        )
    if not parsed:
        raise SourceError("discipline-admissions.csv: no data rows found")
    return parsed


def parse_ag(filename: str, header_row: int) -> dict[str, dict[str, dict[str, Any]]]:
    rows = read_rows(filename)
    years = [cell.strip() for cell in rows[header_row]]

    parsed: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows[header_row + 1 :]:
        if len(row) < 3 or not row[0].strip():
            continue
        region, measure = row[0].strip(), row[1].strip()
        for i in range(2, len(row)):
            year = years[i] if i < len(years) else ""
            if not re.match(r"\d{4}-\d{2}$", year):
                continue
            parsed.setdefault(region, {}).setdefault(year, {})[measure] = parse_number(row[i])
    if not parsed:
        raise SourceError(f"{filename}: no data rows found")
    return parsed


def ag_measure(bucket: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in bucket:
            return bucket[name]
    return None


def build() -> dict[str, Any]:
    campus_raw = parse_admissions("campus-admissions.csv")
    system_raw = parse_admissions("systemwide-admissions.csv")
    disciplines = parse_disciplines()
    statewide_raw = parse_ag("ag-statewide.csv", 0)
    county_raw = parse_ag("ag-by-county.csv", 1)

    if "Systemwide" not in system_raw:
        raise SourceError("systemwide-admissions.csv: no 'Systemwide' row")

    def admissions(record: dict[int, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        return {
            str(year): {
                "applied": record.get(year, {}).get("applied"),
                "admitted": record.get(year, {}).get("admitted"),
                "enrolled": record.get(year, {}).get("enrolled"),
            }
            for year in FALL_YEARS
        }

    system = admissions(system_raw["Systemwide"])
    campuses = {name: admissions(record) for name, record in campus_raw.items()}

    by_level: dict[str, dict[str, dict[str, int]]] = {
        code: {str(y): {"applied": 0, "admitted": 0, "enrolled": 0} for y in FALL_YEARS}
        for code in LEVEL_CODE.values()
    }
    for row in disciplines:
        for year in FALL_YEARS:
            cell = row["years"].get(year, {})
            for measure in ("applied", "admitted", "enrolled"):
                value = cell.get(measure)
                if value:
                    by_level[row["level"]][str(year)][measure] += value

    area_totals: dict[tuple[str, str, str], list[int | None]] = defaultdict(lambda: [0, 0, None])
    for row in disciplines:
        cell = row["years"].get(2025, {})
        key = (row["campus"], row["area"], row["level"])
        bucket = area_totals[key]
        if cell.get("applied"):
            bucket[0] += cell["applied"]
        if cell.get("admitted"):
            bucket[1] += cell["admitted"]
        if cell.get("enrolled"):
            bucket[2] = (bucket[2] or 0) + cell["enrolled"]

    campus_areas = [
        {"campus": campus, "area": area, "level": level, "applied": app, "admitted": adm, "enrolled": enr}
        for (campus, area, level), (app, adm, enr) in sorted(area_totals.items())
        if app
    ]

    areas: dict[str, dict[str, int | None]] = {}
    for entry in campus_areas:
        bucket = areas.setdefault(entry["area"], {"applied": 0, "admitted": 0, "enrolled": None})
        bucket["applied"] += entry["applied"]
        bucket["admitted"] += entry["admitted"]
        if entry["enrolled"] is not None:
            bucket["enrolled"] = (bucket["enrolled"] or 0) + entry["enrolled"]

    programs = []
    for row in disciplines:
        if row["level"] != "F":
            continue
        cell = row["years"].get(2025, {})
        applied, admitted = cell.get("applied"), cell.get("admitted")
        if not applied or applied < MIN_APPLICANTS_FOR_RANKING or admitted is None:
            continue
        programs.append(
            {
                "campus": row["campus"],
                "area": row["area"],
                "major": row["major"],
                "applied": applied,
                "admitted": admitted,
                "enrolled": cell.get("enrolled"),
                "admitRate": round(100 * admitted / applied, 1),
            }
        )

    most_selective = sorted(programs, key=lambda p: (p["admitRate"], -p["applied"]))[:RANKING_SIZE]
    largest = sorted(programs, key=lambda p: -p["applied"])[:RANKING_SIZE]

    academic_years = sorted(statewide_raw["Statewide"])
    latest, earliest = academic_years[-1], academic_years[0]

    statewide = [
        {
            "year": year,
            "met": ag_measure(statewide_raw["Statewide"][year], "Met CSU Requirements Statewide"),
            "graduates": ag_measure(statewide_raw["Statewide"][year], "High School Graduates Statewide"),
            "rate": ag_measure(statewide_raw["Statewide"][year], "% who Met CSU Requirements Statewide"),
        }
        for year in academic_years
    ]

    counties = []
    for name, years in sorted(county_raw.items()):
        latest_bucket = years.get(latest, {})
        rate = ag_measure(latest_bucket, "% who Met CSU Requirements", "  % who Met CSU Requirements")
        graduates = ag_measure(latest_bucket, "Total High School Graduates")
        if rate is None or not graduates:
            continue
        earliest_bucket = years.get(earliest, {})
        counties.append(
            {
                "name": name,
                "graduates": graduates,
                "met": ag_measure(latest_bucket, "Met CSU Requirements"),
                "rate": rate,
                "priorRate": ag_measure(earliest_bucket, "% who Met CSU Requirements", "  % who Met CSU Requirements"),
            }
        )

    return {
        "fallYears": FALL_YEARS,
        "academicYears": academic_years,
        "system": system,
        "campuses": campuses,
        "byLevel": by_level,
        "campusAreas": campus_areas,
        "areas": areas,
        "mostSelective": most_selective,
        "largest": largest,
        "statewide": statewide,
        "counties": counties,
    }


def literal(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False).replace("\n", "\n  ")


def render(data: dict[str, Any]) -> str:
    return f'''import type {{ CSUData }} from "./types";

export const csuData: CSUData = {literal(data)} as const;
'''


def main() -> None:
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(data), encoding="utf-8")

    campuses = [c for c in data["campuses"] if c not in NOT_A_CAMPUS]
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")
    print(f"  {len(campuses)} campuses, {len(data['areas'])} discipline areas")
    print(f"  {len(data['campusAreas'])} campus/area rows, {len(data['counties'])} counties")
    system_2025 = data["system"]["2025"]
    print(
        f"  Fall 2025 systemwide: {system_2025['applied']:,} applied, "
        f"{system_2025['admitted']:,} admitted, {system_2025['enrolled']:,} enrolled"
    )


if __name__ == "__main__":
    main()
