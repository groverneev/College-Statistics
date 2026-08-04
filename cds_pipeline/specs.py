from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class DomainSpec:
    name: str
    question_ids: frozenset[str]
    metric_paths: tuple[str, ...]
    keywords: tuple[str, ...] = ()
    visual_evidence: bool = False


DOMAIN_SPECS: tuple[DomainSpec, ...] = (
    DomainSpec(
        name="enrollment",
        question_ids=frozenset({"B1", "B2"}),
        keywords=("enrollment by racial/ethnic category",),
        metric_paths=(
            "demographics.enrollment.undergraduate",
            "demographics.enrollment.graduate",
            "demographics.enrollment.total",
            "demographics.byRace.international",
            "demographics.byRace.hispanicLatino",
            "demographics.byRace.blackAfricanAmerican",
            "demographics.byRace.white",
            "demographics.byRace.asian",
            "demographics.byRace.americanIndianAlaskaNative",
            "demographics.byRace.nativeHawaiianPacificIslander",
            "demographics.byRace.twoOrMoreRaces",
            "demographics.byRace.unknown",
        ),
        visual_evidence=True,
    ),
    DomainSpec(
        name="admissions",
        question_ids=frozenset({"C1", "C2", "C20", "C21", "C22", "C23"}),
        keywords=("first-time, first-year", "early decision"),
        metric_paths=(
            "admissions.applied",
            "admissions.admitted",
            "admissions.enrolled",
            "admissions.earlyDecision.applied",
            "admissions.earlyDecision.admitted",
            "admissions.earlyAction.applied",
            "admissions.earlyAction.admitted",
            "admissions.byGender.men.applied",
            "admissions.byGender.men.admitted",
            "admissions.byGender.men.enrolled",
            "admissions.byGender.women.applied",
            "admissions.byGender.women.admitted",
            "admissions.byGender.women.enrolled",
        ),
    ),
    DomainSpec(
        name="admissions_factors",
        question_ids=frozenset({"C7"}),
        keywords=("relative importance of each", "academic factors"),
        visual_evidence=True,
        metric_paths=(
            "profile.admissionsFactors.academic.rigorOfSecondarySchoolRecord",
            "profile.admissionsFactors.academic.classRank",
            "profile.admissionsFactors.academic.academicGpa",
            "profile.admissionsFactors.academic.standardizedTestScores",
            "profile.admissionsFactors.academic.applicationEssay",
            "profile.admissionsFactors.academic.recommendations",
            "profile.admissionsFactors.nonacademic.interview",
            "profile.admissionsFactors.nonacademic.extracurricularActivities",
            "profile.admissionsFactors.nonacademic.talentAbility",
            "profile.admissionsFactors.nonacademic.characterPersonalQualities",
            "profile.admissionsFactors.nonacademic.firstGeneration",
            "profile.admissionsFactors.nonacademic.alumniRelation",
            "profile.admissionsFactors.nonacademic.geographicalResidence",
            "profile.admissionsFactors.nonacademic.stateResidency",
            "profile.admissionsFactors.nonacademic.religiousAffiliationCommitment",
            "profile.admissionsFactors.nonacademic.volunteerWork",
            "profile.admissionsFactors.nonacademic.workExperience",
            "profile.admissionsFactors.nonacademic.levelOfApplicantsInterest",
        ),
    ),
    DomainSpec(
        name="test_scores",
        question_ids=frozenset({"C8", "C9", "C10"}),
        keywords=("percent and number of first-time", "sat and act policies"),
        metric_paths=(
            "testScores.sat.composite.p25",
            "testScores.sat.composite.p75",
            "testScores.sat.readingWriting.p25",
            "testScores.sat.readingWriting.p75",
            "testScores.sat.math.p25",
            "testScores.sat.math.p75",
            "testScores.sat.submissionRate",
            "testScores.act.composite.p25",
            "testScores.act.composite.p75",
            "testScores.act.submissionRate",
        ),
    ),
    DomainSpec(
        name="costs",
        question_ids=frozenset({"G1", "G2", "G3"}),
        keywords=("undergraduate full-time tuition", "room and board"),
        metric_paths=(
            "costs.tuition",
            "costs.fees",
            "costs.room",
            "costs.board",
            "costs.roomAndBoard",
        ),
    ),
    DomainSpec(
        name="financial_aid",
        question_ids=frozenset({"H1", "H2", "H2A", "H4", "H5"}),
        keywords=("need-based financial aid", "financial aid awarded"),
        metric_paths=(
            "_source.financialAid.cohortSize",
            "_source.financialAid.aidRecipientCount",
            "_source.financialAid.financialNeedCount",
            "_source.financialAid.needFullyMetCount",
            "financialAid.averageAidPackage",
            "financialAid.averageNeedBasedGrant",
        ),
        visual_evidence=True,
    ),
)


QUESTION_RE = re.compile(
    r"(?im)^\s*([A-I])\s*(\d{1,2})([A-Z]?)\s*(?:[.():-]\s*)?(?=[A-Za-z\u2022]|$)",
)


def extract_question_ids(text: str) -> list[str]:
    return sorted(
        {f"{letter.upper()}{number}{suffix.upper()}" for letter, number, suffix in QUESTION_RE.findall(text)}
    )


def text_for_question_ids(text: str, question_ids: frozenset[str]) -> str:
    """Return only the question blocks a metric domain can actually use."""
    matches = list(QUESTION_RE.finditer(text))
    if not matches:
        return text
    blocks: list[str] = []
    for index, match in enumerate(matches):
        question_id = f"{match.group(1).upper()}{match.group(2)}{match.group(3).upper()}"
        if question_id not in question_ids:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append(text[match.start():end].strip())
    return "\n\n".join(blocks)


def domains_for_page(text: str, question_ids: list[str]) -> list[str]:
    ids = set(question_ids)
    lowered = text.lower()
    domains: list[str] = []
    for spec in DOMAIN_SPECS:
        has_question_anchor = bool(ids.intersection(spec.question_ids))
        # Keyword routing is a fallback for visually/OCR extracted pages that lost
        # question labels. Native CDS pages should route by stable question IDs to
        # avoid pulling every incidental mention of "first-year" into C1.
        has_keyword_fallback = not ids and any(keyword in lowered for keyword in spec.keywords)
        if has_question_anchor or has_keyword_fallback:
            domains.append(spec.name)
    return domains


def spec_for_domain(domain: str) -> DomainSpec:
    for spec in DOMAIN_SPECS:
        if spec.name == domain:
            return spec
    raise KeyError(f"Unknown CDS domain: {domain}")
