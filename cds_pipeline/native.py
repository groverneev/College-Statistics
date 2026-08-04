from __future__ import annotations

import re

from .models import MetricObservation, SectionExtraction, SectionPacket, SourceEvidence


def _label(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip() if value else ""


def _number(value: str | None) -> int | float | None:
    if not value:
        return None
    cleaned = value.replace("$", "").replace(",", "").replace(" ", "").strip()
    percent = cleaned.endswith("%")
    if percent:
        cleaned = cleaned[:-1]
    if not re.fullmatch(r"[-+]?\d+(?:\.\d+)?", cleaned):
        return None
    number = float(cleaned)
    if percent:
        return number / 100
    return int(number) if number.is_integer() else number


def _normalized_positions(value: str) -> tuple[str, list[int]]:
    normalized: list[str] = []
    positions: list[int] = []
    for index, character in enumerate(value):
        if character.isalnum():
            normalized.append(character.lower())
            positions.append(index)
        elif normalized and normalized[-1] != " ":
            normalized.append(" ")
            positions.append(index)
    return "".join(normalized).strip(), positions


def _source_quote(page_text: str, label: str, raw_value: str) -> str:
    normalized, positions = _normalized_positions(page_text)
    normalized_label = _label(label)
    normalized_value = _label(raw_value)
    value_matches = [match for match in re.finditer(re.escape(normalized_value), normalized)]
    if not value_matches:
        return raw_value.strip()
    label_index = normalized.find(normalized_label) if normalized_label else -1
    if label_index >= 0:
        match = min(
            value_matches,
            key=lambda item: (
                item.start() < label_index,
                abs(item.start() - (label_index + len(normalized_label))),
            ),
        )
        normalized_start = label_index
    else:
        match = value_matches[0]
        normalized_start = max(0, match.start() - 80)
    original_start = positions[min(normalized_start, len(positions) - 1)]
    original_end = positions[min(match.end() - 1, len(positions) - 1)] + 1
    if original_end - original_start > 240:
        original_start = max(original_start, original_end - 220)
    line_end = page_text.find("\n", original_end)
    if line_end != -1 and line_end - original_start <= 240:
        original_end = line_end
    quote = page_text[original_start:original_end].strip()
    return quote[-240:] or raw_value.strip()


def _observation(
    path: str,
    value: int | float,
    *,
    packet_page,
    question_id: str,
    quote: str,
    label: str,
) -> MetricObservation:
    return MetricObservation(
        path=path,
        value=value,
        evidence=[
            SourceEvidence(
                document_id=packet_page.document_id,
                page=packet_page.page,
                question_id=question_id,
                quote=_source_quote(packet_page.text, label, quote),
            )
        ],
        method="native-rule",
        confidence=1.0,
        review_required=False,
        notes="Stable CDS table row and column.",
    )


def _page_for(packet: SectionPacket, question_id: str):
    return next((page for page in packet.pages if question_id in page.question_ids), None)


def _rows(page):
    for table in page.tables:
        for row in table.rows:
            if row:
                yield row


def _extract_admissions(packet: SectionPacket) -> list[MetricObservation]:
    mappings = (
        ("total first time first year degree seeking who applied", "admissions.applied", "C1"),
        ("total first time first year degree seeking who were admitted", "admissions.admitted", "C1"),
        ("total first time first year degree seeking who enrolled", "admissions.enrolled", "C1"),
        ("total first time first year men who applied", "admissions.byGender.men.applied", "C1"),
        ("total first time first year men who were admitted", "admissions.byGender.men.admitted", "C1"),
        ("total full time first time first year men who enrolled", "admissions.byGender.men.enrolled", "C1"),
        ("total first time first year women who applied", "admissions.byGender.women.applied", "C1"),
        ("total first time first year women who were admitted", "admissions.byGender.women.admitted", "C1"),
        ("total full time first time first year women who enrolled", "admissions.byGender.women.enrolled", "C1"),
        ("number of early decision applications received", "admissions.earlyDecision.applied", "C21"),
        ("number of applicants admitted under early decision", "admissions.earlyDecision.admitted", "C21"),
    )
    observations: list[MetricObservation] = []
    for page in packet.pages:
        for row in _rows(page):
            row_label = _label(row[0])
            for needle, path, question_id in mappings:
                if needle not in row_label or len(row) < 2:
                    continue
                value = _number(row[1])
                if value is not None:
                    observations.append(
                        _observation(path, value, packet_page=page, question_id=question_id, quote=row[1] or "", label=row[0] or path)
                    )
                break
    return observations


def _extract_costs(packet: SectionPacket) -> list[MetricObservation]:
    page = _page_for(packet, "G1")
    if page is None:
        return []
    mappings = (
        ("private institutions tuition", "costs.tuition"),
        ("required fees", "costs.fees"),
        ("food and housing on campus", "costs.roomAndBoard"),
        ("housing only on campus", "costs.room"),
        ("food only on campus meal plan", "costs.board"),
    )
    observations: list[MetricObservation] = []
    for row in _rows(page):
        row_label = _label(row[0])
        for needle, path in mappings:
            if needle not in row_label or len(row) < 2:
                continue
            value = _number(row[1])
            if value is not None:
                observations.append(
                    _observation(path, value, packet_page=page, question_id="G1", quote=row[1] or "", label=row[0] or path)
                )
            break
    return observations


def _extract_test_scores(packet: SectionPacket) -> list[MetricObservation]:
    page = _page_for(packet, "C9")
    if page is None:
        return []
    observations: list[MetricObservation] = []
    score_rows = {
        "sat composite": ("testScores.sat.composite.p25", "testScores.sat.composite.p75"),
        "sat evidence based reading and writing": (
            "testScores.sat.readingWriting.p25",
            "testScores.sat.readingWriting.p75",
        ),
        "sat math": ("testScores.sat.math.p25", "testScores.sat.math.p75"),
        "act composite": ("testScores.act.composite.p25", "testScores.act.composite.p75"),
    }
    for row in _rows(page):
        row_label = _label(row[0])
        if row_label == "submitting sat scores" and len(row) > 1:
            value = _number(row[1])
            if value is not None:
                observations.append(_observation("testScores.sat.submissionRate", value, packet_page=page, question_id="C9", quote=row[1] or "", label=row[0] or "Submitting SAT Scores"))
        elif row_label == "submitting act scores" and len(row) > 1:
            value = _number(row[1])
            if value is not None:
                observations.append(_observation("testScores.act.submissionRate", value, packet_page=page, question_id="C9", quote=row[1] or "", label=row[0] or "Submitting ACT Scores"))
        elif row_label in score_rows and len(row) > 3:
            for path, cell in zip(score_rows[row_label], (row[1], row[3])):
                value = _number(cell)
                if value is not None:
                    observations.append(_observation(path, value, packet_page=page, question_id="C9", quote=cell or "", label=row[0] or path))
    return observations


def _extract_enrollment(packet: SectionPacket) -> list[MetricObservation]:
    observations: list[MetricObservation] = []
    b1 = _page_for(packet, "B1")
    if b1 is not None:
        totals = (
            (r"(?im)^\s*Total all Undergraduate\s+([\d,]+)", "demographics.enrollment.undergraduate"),
            (r"(?im)^\s*Total all Graduate and Professional\s+([\d,]+)", "demographics.enrollment.graduate"),
            (r"(?im)^\s*GRAND TOTAL ALL STUDENTS\s+([\d,]+)", "demographics.enrollment.total"),
        )
        for pattern, path in totals:
            match = re.search(pattern, b1.text)
            if match and (value := _number(match.group(1))) is not None:
                observations.append(_observation(path, value, packet_page=b1, question_id="B1", quote=match.group(1), label=match.group(0)))
    b2 = _page_for(packet, "B2")
    if b2 is None:
        return observations
    mappings = {
        "international": "demographics.byRace.international",
        "hispanic latino": "demographics.byRace.hispanicLatino",
        "black or african american non hispanic": "demographics.byRace.blackAfricanAmerican",
        "white non hispanic": "demographics.byRace.white",
        "asian non hispanic": "demographics.byRace.asian",
        "american indian or alaska native non hispanic": "demographics.byRace.americanIndianAlaskaNative",
        "native hawaiian or other pacific islander non hispanic": "demographics.byRace.nativeHawaiianPacificIslander",
        "two or more races non hispanic": "demographics.byRace.twoOrMoreRaces",
        "race and or ethnicity unknown": "demographics.byRace.unknown",
    }
    for row in _rows(b2):
        path = mappings.get(_label(row[0]))
        if path and len(row) > 1:
            value = _number(row[-1])
            if value is not None:
                observations.append(_observation(path, value, packet_page=b2, question_id="B2", quote=row[-1] or "", label=row[0] or path))
    return observations


def _extract_financial_aid(packet: SectionPacket) -> list[MetricObservation]:
    page = _page_for(packet, "H2")
    if page is None:
        return []
    mappings = (
        (("number of degree seeking undergraduate students",), "_source.financialAid.cohortSize"),
        (("determined to have", "financial need"), "_source.financialAid.financialNeedCount"),
        (("line c who were awarded any financial aid",), "_source.financialAid.aidRecipientCount"),
        (("whose need was fully met",), "_source.financialAid.needFullyMetCount"),
        (("average financial aid package",), "financialAid.averageAidPackage"),
        (("average need based scholarship and grant award",), "financialAid.averageNeedBasedGrant"),
    )
    observations: list[MetricObservation] = []
    for row in _rows(page):
        row_label = _label(row[0])
        for needles, path in mappings:
            if not all(needle in row_label for needle in needles) or len(row) < 2:
                continue
            value = _number(row[1])
            if value is not None:
                observations.append(_observation(path, value, packet_page=page, question_id="H2", quote=row[1] or "", label=row[0] or path))
            break
    return observations


EXTRACTORS = {
    "admissions": _extract_admissions,
    "costs": _extract_costs,
    "test_scores": _extract_test_scores,
    "enrollment": _extract_enrollment,
    "financial_aid": _extract_financial_aid,
}


REQUIRED_NATIVE_PATHS = {
    "admissions": {"admissions.applied", "admissions.admitted", "admissions.enrolled"},
    "costs": {"costs.tuition", "costs.fees", "costs.roomAndBoard"},
    "test_scores": {
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
    },
    "enrollment": {
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
    },
    "financial_aid": {
        "_source.financialAid.cohortSize",
        "_source.financialAid.aidRecipientCount",
        "_source.financialAid.financialNeedCount",
        "_source.financialAid.needFullyMetCount",
        "financialAid.averageAidPackage",
        "financialAid.averageNeedBasedGrant",
    },
}


BLOCKING_PATHS = {
    "admissions": {"admissions.applied", "admissions.admitted", "admissions.enrolled"},
    "costs": {"costs.tuition", "costs.fees", "costs.roomAndBoard"},
    "enrollment": REQUIRED_NATIVE_PATHS["enrollment"],
}


def blocking_paths(packet: SectionPacket) -> set[str]:
    if packet.domain == "admissions_factors":
        return set(packet.metric_paths)
    return set(BLOCKING_PATHS.get(packet.domain, set()))


def extract_packet_native(packet: SectionPacket) -> tuple[SectionExtraction, bool]:
    extractor = EXTRACTORS.get(packet.domain)
    observations = extractor(packet) if extractor else []
    allowed = set(packet.metric_paths)
    unique = {observation.path: observation for observation in observations if observation.path in allowed}
    required = REQUIRED_NATIVE_PATHS.get(packet.domain, set())
    return (
        SectionExtraction(
            observations=list(unique.values()),
            notes=["Stable CDS tables parsed deterministically before model extraction."],
        ),
        bool(required) and required.issubset(unique),
    )
