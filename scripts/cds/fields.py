from __future__ import annotations

from typing import Any

from common import get_path, set_path

FACTOR_LEVELS = {"very_important", "important", "considered", "not_considered"}

ACADEMIC_FACTORS = {
    "rigorOfSecondarySchoolRecord": "Rigor of secondary school record",
    "classRank": "Class rank",
    "academicGpa": "Academic GPA",
    "standardizedTestScores": "Standardized test scores",
    "applicationEssay": "Application essay",
    "recommendations": "Recommendation(s)",
}

NONACADEMIC_FACTORS = {
    "interview": "Interview",
    "extracurricularActivities": "Extracurricular activities",
    "talentAbility": "Talent/ability",
    "characterPersonalQualities": "Character/personal qualities",
    "firstGeneration": "First generation",
    "alumniRelation": "Alumni/ae relation",
    "geographicalResidence": "Geographical residence",
    "stateResidency": "State residency",
    "religiousAffiliationCommitment": "Religious affiliation/commitment",
    "volunteerWork": "Volunteer work",
    "workExperience": "Work experience",
    "levelOfApplicantsInterest": "Level of applicant's interest",
}

FIELDS: dict[str, str] = {
    "admissions.applied": "C1 total first-time, first-year students who applied (all genders, full- and part-time)",
    "admissions.admitted": "C1 total first-time, first-year students admitted",
    "admissions.enrolled": "C1 total first-time, first-year students enrolled (full- plus part-time)",
    "admissions.byGender.men.applied": "C1 men applied",
    "admissions.byGender.men.admitted": "C1 men admitted",
    "admissions.byGender.men.enrolled": "C1 men enrolled (full- plus part-time)",
    "admissions.byGender.women.applied": "C1 women applied",
    "admissions.byGender.women.admitted": "C1 women admitted",
    "admissions.byGender.women.enrolled": "C1 women enrolled (full- plus part-time)",
    "raw.C1.otherGender.applied": "C1 applied with another gender plus unknown sex, combined (omit if those rows are blank)",
    "raw.C1.otherGender.admitted": "C1 admitted with another gender plus unknown sex, combined",
    "raw.C1.otherGender.enrolled": "C1 enrolled with another gender plus unknown sex, combined",
    "admissions.earlyDecision.applied": "C21 number of early decision applications received (only if ED is offered)",
    "admissions.earlyDecision.admitted": "C21 number of applicants admitted under early decision",
    "admissions.earlyAction.applied": "C22 number of early action applications received (only if EA is offered and the count is reported)",
    "admissions.earlyAction.admitted": "C22 number of early action applicants admitted",
    "testScores.sat.composite.p25": "C9 SAT Composite 25th percentile (omit if the composite row is blank; never sum sections)",
    "testScores.sat.composite.p50": "C9 SAT Composite 50th percentile",
    "testScores.sat.composite.p75": "C9 SAT Composite 75th percentile",
    "testScores.sat.readingWriting.p25": "C9 SAT Evidence-Based Reading and Writing 25th percentile",
    "testScores.sat.readingWriting.p50": "C9 SAT Evidence-Based Reading and Writing 50th percentile",
    "testScores.sat.readingWriting.p75": "C9 SAT Evidence-Based Reading and Writing 75th percentile",
    "testScores.sat.math.p25": "C9 SAT Math 25th percentile",
    "testScores.sat.math.p50": "C9 SAT Math 50th percentile",
    "testScores.sat.math.p75": "C9 SAT Math 75th percentile",
    "testScores.sat.submissionRate": "C9 percent of enrolled first-years submitting SAT scores, as a fraction (78% -> 0.78)",
    "testScores.act.composite.p25": "C9 ACT Composite 25th percentile",
    "testScores.act.composite.p50": "C9 ACT Composite 50th percentile",
    "testScores.act.composite.p75": "C9 ACT Composite 75th percentile",
    "testScores.act.submissionRate": "C9 percent submitting ACT scores, as a fraction",
    "demographics.enrollment.undergraduate": "B1 total all undergraduates",
    "demographics.enrollment.graduate": "B1 total all graduate and professional students (0 if the school has none)",
    "demographics.enrollment.total": "B1 grand total all students",
    "demographics.byRace.international": "B2 nonresidents (formerly 'nonresident aliens'), rightmost total-undergraduates column",
    "demographics.byRace.hispanicLatino": "B2 Hispanic/Latino, same column",
    "demographics.byRace.blackAfricanAmerican": "B2 Black or African American, non-Hispanic",
    "demographics.byRace.white": "B2 White, non-Hispanic",
    "demographics.byRace.asian": "B2 Asian, non-Hispanic",
    "demographics.byRace.americanIndianAlaskaNative": "B2 American Indian or Alaska Native, non-Hispanic",
    "demographics.byRace.nativeHawaiianPacificIslander": "B2 Native Hawaiian or other Pacific Islander, non-Hispanic",
    "demographics.byRace.twoOrMoreRaces": "B2 two or more races, non-Hispanic",
    "demographics.byRace.unknown": "B2 race and/or ethnicity unknown",
    "demographics.byResidency.inState": "Undergraduate headcount from in state; only if the CDS reports all-undergraduate headcounts by residency (rare; omit all three otherwise, never derive from F1 percentages)",
    "demographics.byResidency.outOfState": "Undergraduate headcount from out of state (same rule)",
    "demographics.byResidency.international": "Undergraduate international headcount (same rule)",
    "costs.tuition": "G1 tuition, undergraduates column (not first-year-only); for public schools use in-state/in-district",
    "costs.fees": "G1 required fees, undergraduates column",
    "costs.roomAndBoard": "G1 food and housing (on-campus room and board), undergraduates column",
    "raw.H2.a": "H2 row A, full-time undergraduate column: number of degree-seeking undergraduate students",
    "raw.H2.d": "H2 row D, full-time undergraduate column: students in line C awarded any financial aid",
    "raw.H2.h": "H2 row H, full-time undergraduate column: students in line D whose need was fully met",
    "financialAid.averageAidPackage": "H2 row J, full-time undergraduate column: average financial aid package",
    "financialAid.averageNeedBasedGrant": "H2 row K, full-time undergraduate column: average need-based scholarship or grant award",
}

for key, label in ACADEMIC_FACTORS.items():
    FIELDS[f"factors.academic.{key}"] = f"C7 '{label}': very_important | important | considered | not_considered"
for key, label in NONACADEMIC_FACTORS.items():
    FIELDS[f"factors.nonacademic.{key}"] = f"C7 '{label}': very_important | important | considered | not_considered"

FACTOR_PREFIX = "factors."


def is_factor(path: str) -> bool:
    return path.startswith(FACTOR_PREFIX)


def ratio(numerator: Any, denominator: Any) -> float | None:
    if not isinstance(numerator, (int, float)) or not isinstance(denominator, (int, float)) or denominator <= 0:
        return None
    return round(numerator / denominator, 4)


def derive_year(values: dict[str, Any]) -> dict:
    year: dict = {
        "admissions": {},
        "testScores": {},
        "demographics": {"enrollment": {}, "byRace": {}},
        "costs": {},
        "financialAid": {},
    }
    for path, value in values.items():
        if value is None or path.startswith("raw.") or is_factor(path):
            continue
        set_path(year, path, value)

    admissions = year["admissions"]
    for stage in ("applied", "admitted", "enrolled"):
        if admissions.get(stage) is None:
            men = get_path(admissions, f"byGender.men.{stage}")
            women = get_path(admissions, f"byGender.women.{stage}")
            other = values.get(f"raw.C1.otherGender.{stage}") or 0
            if isinstance(men, int) and isinstance(women, int):
                admissions[stage] = men + women + other
    if (rate := ratio(admissions.get("admitted"), admissions.get("applied"))) is not None:
        admissions["acceptanceRate"] = rate
    if (rate := ratio(admissions.get("enrolled"), admissions.get("admitted"))) is not None:
        admissions["yield"] = rate

    enrollment = year["demographics"]["enrollment"]
    if enrollment.get("total") is None and isinstance(enrollment.get("undergraduate"), int):
        enrollment["total"] = enrollment["undergraduate"] + (enrollment.get("graduate") or 0)

    costs = year["costs"]
    parts = [costs.get("tuition"), costs.get("fees"), costs.get("roomAndBoard")]
    if all(isinstance(part, (int, float)) for part in parts):
        costs["totalCOA"] = sum(parts)

    aid = year["financialAid"]
    if (share := ratio(values.get("raw.H2.d"), values.get("raw.H2.a"))) is not None:
        aid["percentReceivingAid"] = share
    if (share := ratio(values.get("raw.H2.h"), values.get("raw.H2.d"))) is not None:
        aid["percentNeedFullyMet"] = share

    return year


def derive_factors(values: dict[str, Any]) -> dict | None:
    factors: dict = {}
    for path, value in values.items():
        if is_factor(path) and value is not None:
            set_path(factors, path[len(FACTOR_PREFIX):], value)
    academic = factors.get("academic", {})
    nonacademic = factors.get("nonacademic", {})
    if set(academic) != set(ACADEMIC_FACTORS) or set(nonacademic) != set(NONACADEMIC_FACTORS):
        return None
    return {
        "academic": {key: academic[key] for key in ACADEMIC_FACTORS},
        "nonacademic": {key: nonacademic[key] for key in NONACADEMIC_FACTORS},
    }
