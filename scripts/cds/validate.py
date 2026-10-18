from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import SCHOOLS_DIR, YEAR_RE, flatten, get_path, load_json  # noqa: E402
from fields import ACADEMIC_FACTORS, FACTOR_LEVELS, NONACADEMIC_FACTORS  # noqa: E402

YEAR_SHAPE = {
    "admissions": {"applied", "admitted", "enrolled", "acceptanceRate", "yield", "earlyDecision", "earlyAction", "byGender"},
    "testScores": {"sat", "act"},
    "demographics": {"enrollment", "byRace", "byResidency"},
    "costs": {"tuition", "fees", "roomAndBoard", "totalCOA"},
    "financialAid": {"percentReceivingAid", "averageAidPackage", "averageNeedBasedGrant", "percentNeedFullyMet", "averageNetPrice"},
}
LEAVES = {
    "admissions.earlyDecision": {"applied", "admitted"},
    "admissions.earlyAction": {"applied", "admitted"},
    "admissions.byGender": {"men", "women"},
    "testScores.sat": {"composite", "readingWriting", "math", "submissionRate"},
    "testScores.act": {"composite", "submissionRate"},
    "demographics.enrollment": {"total", "undergraduate", "graduate"},
    "demographics.byRace": {
        "international", "hispanicLatino", "blackAfricanAmerican", "white", "asian",
        "americanIndianAlaskaNative", "nativeHawaiianPacificIslander", "twoOrMoreRaces", "unknown",
    },
    "demographics.byResidency": {"inState", "outOfState", "international"},
}
FRACTIONS = {
    "admissions.acceptanceRate", "admissions.yield", "testScores.sat.submissionRate",
    "testScores.act.submissionRate", "financialAid.percentReceivingAid", "financialAid.percentNeedFullyMet",
}
DOLLARS = {
    "costs.tuition", "costs.fees", "costs.roomAndBoard", "costs.totalCOA",
    "financialAid.averageAidPackage", "financialAid.averageNeedBasedGrant", "financialAid.averageNetPrice",
}
SWING_FIELDS = [
    "admissions.applied", "admissions.admitted", "admissions.enrolled",
    "demographics.enrollment.undergraduate", "costs.tuition", "financialAid.averageAidPackage",
]
SWING_LIMIT = 0.4


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")

    def warn(self, where: str, message: str) -> None:
        self.warnings.append(f"{where}: {message}")


def num(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_shape(year: str, data: dict, report: Report) -> None:
    for section, allowed in YEAR_SHAPE.items():
        if section not in data:
            report.error(year, f"missing {section}")
            continue
        for key in set(data[section]) - allowed:
            report.error(year, f"unknown key {section}.{key}")
    for prefix, allowed in LEAVES.items():
        node = get_path(data, prefix)
        if isinstance(node, dict):
            for key in set(node) - allowed:
                report.error(year, f"unknown key {prefix}.{key}")
    for gender in ("men", "women"):
        node = get_path(data, f"admissions.byGender.{gender}")
        if isinstance(node, dict):
            for key in set(node) - {"applied", "admitted", "enrolled"}:
                report.error(year, f"unknown key admissions.byGender.{gender}.{key}")
    for test, parts in (("sat", ("composite", "readingWriting", "math")), ("act", ("composite",))):
        for part in parts:
            node = get_path(data, f"testScores.{test}.{part}")
            if isinstance(node, dict):
                for key in set(node) - {"p25", "p50", "p75"}:
                    report.error(year, f"unknown key testScores.{test}.{part}.{key}")
    if "demographics" in data:
        for key in ("enrollment", "byRace"):
            if key not in data["demographics"]:
                report.error(year, f"missing demographics.{key}")
    residency = get_path(data, "demographics.byResidency")
    if isinstance(residency, dict) and set(residency) != LEAVES["demographics.byResidency"]:
        report.error(year, "byResidency needs inState, outOfState and international together")


def check_values(year: str, data: dict, report: Report) -> None:
    flat = flatten(data)
    for path, value in flat.items():
        if isinstance(value, dict) and not value:
            continue
        if not num(value):
            report.error(year, f"{path} is not a number ({value!r})")
            continue
        if value < 0:
            report.error(year, f"{path} is negative")
        if path in FRACTIONS:
            if value > 1:
                report.error(year, f"{path}={value} is above 1; percentages must be fractions")
        elif path not in DOLLARS and not float(value).is_integer():
            report.error(year, f"{path}={value} should be a whole number")

    a = data.get("admissions", {})
    applied, admitted, enrolled = a.get("applied"), a.get("admitted"), a.get("enrolled")
    if num(applied) and num(admitted) and admitted > applied:
        report.error(year, f"admitted {admitted} > applied {applied}")
    if num(admitted) and num(enrolled) and enrolled > admitted:
        report.error(year, f"enrolled {enrolled} > admitted {admitted}")
    if num(applied) and num(admitted) and applied:
        expected = round(admitted / applied, 4)
        if not num(a.get("acceptanceRate")) or abs(a["acceptanceRate"] - expected) > 0.0001:
            report.error(year, f"acceptanceRate {a.get('acceptanceRate')} != {expected}")
    if num(admitted) and num(enrolled) and admitted:
        expected = round(enrolled / admitted, 4)
        if not num(a.get("yield")) or abs(a["yield"] - expected) > 0.0001:
            report.error(year, f"yield {a.get('yield')} != {expected}")

    for stage in ("applied", "admitted", "enrolled"):
        men = get_path(a, f"byGender.men.{stage}")
        women = get_path(a, f"byGender.women.{stage}")
        total = a.get(stage)
        if num(men) and num(women) and num(total):
            if men + women > total:
                report.error(year, f"men+women {stage} {men + women} > total {total}")
            elif total and (total - men - women) / total > 0.03:
                report.warn(year, f"men+women {stage} is {total - men - women} short of total {total}")

    for plan in ("earlyDecision", "earlyAction"):
        plan_applied = get_path(a, f"{plan}.applied")
        plan_admitted = get_path(a, f"{plan}.admitted")
        if num(plan_applied) and num(plan_admitted) and plan_admitted > plan_applied:
            report.error(year, f"{plan} admitted > applied")
        if num(plan_applied) and num(applied) and plan_applied > applied:
            report.error(year, f"{plan} applied > total applied")

    ranges = {
        "testScores.sat.composite": (400, 1600),
        "testScores.sat.readingWriting": (200, 800),
        "testScores.sat.math": (200, 800),
        "testScores.act.composite": (1, 36),
    }
    for path, (low, high) in ranges.items():
        node = get_path(data, path) or {}
        points = [node.get(p) for p in ("p25", "p50", "p75")]
        for point, value in zip(("p25", "p50", "p75"), points):
            if num(value) and not low <= value <= high:
                report.error(year, f"{path}.{point}={value} outside {low}-{high}")
        present = [v for v in points if num(v)]
        if present != sorted(present):
            report.error(year, f"{path} percentiles not increasing: {points}")
    sat = get_path(data, "testScores.sat") or {}
    for point in ("p25", "p75"):
        comp = get_path(sat, f"composite.{point}")
        rw = get_path(sat, f"readingWriting.{point}")
        math = get_path(sat, f"math.{point}")
        if num(comp) and num(rw) and num(math) and abs(comp - (rw + math)) > 100:
            report.warn(year, f"SAT composite {point} {comp} far from section sum {rw + math}")

    enrollment = get_path(data, "demographics.enrollment") or {}
    ug, grad, total = enrollment.get("undergraduate"), enrollment.get("graduate"), enrollment.get("total")
    if num(ug) and num(grad) and num(total) and ug + grad != total:
        report.error(year, f"enrollment undergraduate {ug} + graduate {grad} != total {total}")
    race = get_path(data, "demographics.byRace") or {}
    race_sum = sum(v for v in race.values() if num(v))
    if race and num(ug) and ug:
        gap = abs(race_sum - ug) / ug
        if gap > 0.05:
            report.error(year, f"byRace sums to {race_sum}, undergraduate is {ug}")
        elif gap > 0.01:
            report.warn(year, f"byRace sums to {race_sum}, undergraduate is {ug}")
    residency = get_path(data, "demographics.byResidency") or {}
    if residency and num(ug) and ug and abs(sum(residency.values()) - ug) / ug > 0.05:
        report.warn(year, f"byResidency sums to {sum(residency.values())}, undergraduate is {ug}")
    if num(enrolled) and num(ug) and enrolled > ug:
        report.error(year, f"first-year enrolled {enrolled} > undergraduates {ug}")

    costs = data.get("costs", {})
    parts = [costs.get(k) for k in ("tuition", "fees", "roomAndBoard")]
    if all(num(p) for p in parts) and costs.get("totalCOA") != sum(parts):
        report.error(year, f"totalCOA {costs.get('totalCOA')} != {sum(parts)}")
    if num(costs.get("tuition")) and not 1000 <= costs["tuition"] <= 120000:
        report.warn(year, f"tuition {costs['tuition']} looks implausible")

    aid = data.get("financialAid", {})
    if num(aid.get("averageNeedBasedGrant")) and num(aid.get("averageAidPackage")):
        if aid["averageNeedBasedGrant"] > aid["averageAidPackage"] * 1.05:
            report.warn(year, "average need-based grant exceeds average aid package")


def check_trends(school: dict, report: Report) -> None:
    years = sorted(school["years"])
    for earlier, later in zip(years, years[1:]):
        if int(later[:4]) != int(earlier[:4]) + 1:
            report.warn(later, f"gap after {earlier}")
            continue
        for path in SWING_FIELDS:
            before = get_path(school["years"][earlier], path)
            after = get_path(school["years"][later], path)
            if num(before) and num(after) and before:
                change = (after - before) / before
                if abs(change) > SWING_LIMIT:
                    report.warn(later, f"{path} changed {change:+.0%} from {earlier} ({before} -> {after})")
        before = get_path(school["years"][earlier], "costs.tuition")
        after = get_path(school["years"][later], "costs.tuition")
        if num(before) and num(after) and after < before * 0.97:
            report.warn(later, f"tuition fell from {before} to {after}")


def check_profile(school: dict, report: Report) -> None:
    factors = get_path(school, "profile.admissionsFactors")
    if factors is None:
        report.warn("profile", "no admissionsFactors")
        return
    for key in ("sourceYear", "sourcePdf", "section"):
        if not factors.get(key):
            report.error("profile", f"admissionsFactors.{key} missing")
    for group, expected in (("academic", ACADEMIC_FACTORS), ("nonacademic", NONACADEMIC_FACTORS)):
        got = factors.get(group, {})
        if set(got) != set(expected):
            report.error("profile", f"admissionsFactors.{group} keys differ: {sorted(set(expected) ^ set(got))}")
        for key, level in got.items():
            if level not in FACTOR_LEVELS:
                report.error("profile", f"admissionsFactors.{group}.{key}={level!r}")


def validate(path: Path) -> Report:
    report = Report()
    school = load_json(path)
    if school.get("slug") != path.stem:
        report.error("school", f"slug {school.get('slug')!r} != filename {path.stem!r}")
    if not school.get("name"):
        report.error("school", "missing name")
    if not school.get("years"):
        report.error("school", "no years")
    for year, data in school.get("years", {}).items():
        if not YEAR_RE.match(year):
            report.error(year, "bad year key")
            continue
        check_shape(year, data, report)
        check_values(year, data, report)
    check_trends(school, report)
    check_profile(school, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("slugs", nargs="*", help="defaults to every school")
    args = parser.parse_args()
    paths = [SCHOOLS_DIR / f"{slug}.json" for slug in args.slugs] or sorted(SCHOOLS_DIR.glob("*.json"))

    failed = False
    for path in paths:
        report = validate(path)
        status = "FAIL" if report.errors else "ok"
        print(f"{path.stem}: {status} ({len(report.errors)} errors, {len(report.warnings)} warnings)")
        for line in report.errors:
            print(f"  ERROR {line}")
        for line in report.warnings:
            print(f"  warn  {line}")
        failed = failed or bool(report.errors)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
