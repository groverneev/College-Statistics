from __future__ import annotations

import re

from .models import MetricObservation, SectionExtraction, SectionPacket, SourceEvidence


def _label(value: str | None) -> str:
    if not value:
        return ""
    value = value.lower().replace("ﬃ", "ffi").replace("ﬁ", "fi").replace("ﬂ", "fl")
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


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


def _numbers(value: str) -> list[int | float]:
    return [
        number
        for token in re.findall(r"\$?\d[\d,]*(?:\.\d+)?%?", value)
        if (number := _number(token)) is not None
    ]


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
    compact_label = _label(label).replace(" ", "")
    compact_value = _label(raw_value).replace(" ", "")
    if compact_label and compact_value:
        for line in page_text.splitlines():
            compact_line = _label(line).replace(" ", "")
            if compact_label in compact_line and compact_value in compact_line:
                return line.strip()[-240:]
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


def _summed_row_observation(
    path: str,
    values: list[int | float],
    *,
    packet_page,
    question_id: str,
    quote: str,
) -> MetricObservation:
    return MetricObservation(
        path=path,
        value=sum(values),
        evidence=[
            SourceEvidence(
                document_id=packet_page.document_id,
                page=packet_page.page,
                question_id=question_id,
                quote=quote.strip(),
            )
        ],
        method="native-rule",
        confidence=1.0,
        review_required=False,
        notes="Deterministic sum of the numeric C1 gender columns in the quoted row.",
    )


def _summed_cells_observation(
    path: str,
    cells: list[tuple[object, str]],
    *,
    question_id: str,
) -> MetricObservation:
    return MetricObservation(
        path=path,
        value=sum(_number(raw) or 0 for _, raw in cells),
        evidence=[
            SourceEvidence(
                document_id=page.document_id,
                page=page.page,
                question_id=question_id,
                quote=raw,
            )
            for page, raw in cells
        ],
        method="native-rule",
        confidence=1.0,
        review_required=False,
        notes="Deterministic sum of cited C1 gender cells.",
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

    row_specs = (
        (
            "applied",
            "admissions.applied",
            "admissions.byGender.men.applied",
            "admissions.byGender.women.applied",
        ),
        (
            "admitted",
            "admissions.admitted",
            "admissions.byGender.men.admitted",
            "admissions.byGender.women.admitted",
        ),
        (
            "enrolled",
            "admissions.enrolled",
            "admissions.byGender.men.enrolled",
            "admissions.byGender.women.enrolled",
        ),
    )
    for page in packet.pages:
        compact_rows = (
            (r"(?im)^\s*CategoryApplied[^\n]*$", "admissions.applied", "applied"),
            (r"(?im)^\s*Admitted\s+All[^\n]*$", "admissions.admitted", "admitted"),
            (r"(?im)^\s*Enrolled\s+Full-Time[^\n]*$", "admissions.enrolled", "enrolled"),
        )
        for pattern, total_path, verb in compact_rows:
            match = re.search(pattern, page.text)
            if not match:
                continue
            raw_values = re.findall(r"\d[\d,]*", match.group(0))
            values = [value for raw in raw_values if (value := _number(raw)) is not None]
            if len(values) < 2:
                continue
            observations.append(
                _summed_row_observation(
                    total_path,
                    values,
                    packet_page=page,
                    question_id="C1",
                    quote=match.group(0),
                )
            )
            for path, index in (
                (f"admissions.byGender.men.{verb}", 0),
                (f"admissions.byGender.women.{verb}", 1),
            ):
                observations.append(
                    _observation(
                        path,
                        values[index],
                        packet_page=page,
                        question_id="C1",
                        quote=raw_values[index],
                        label=match.group(0),
                    )
                )

        for verb, total_path, men_path, women_path in row_specs:
            match = re.search(
                rf"(?im)^\s*Total first-time,\s*first-year students (?:who )?{verb}"
                rf"(?: in Fall \d{{4}})?\s+(?P<values>[\d,]+(?:\s+[\d,]+)+)\s*$",
                page.text,
            )
            if not match:
                continue
            raw_values = re.findall(r"\d[\d,]*(?:\.\d+)?", match.group("values"))
            values = [value for raw in raw_values if (value := _number(raw)) is not None]
            if len(values) < 2:
                continue
            quote = match.group("values").strip()
            observations.extend(
                [
                    _summed_row_observation(
                        total_path,
                        values,
                        packet_page=page,
                        question_id="C1",
                        quote=quote,
                    ),
                    _observation(
                        men_path,
                        values[0],
                        packet_page=page,
                        question_id="C1",
                        quote=raw_values[0],
                        label=f"Total first-time, first-year students {verb}",
                    ),
                    _observation(
                        women_path,
                        values[1],
                        packet_page=page,
                        question_id="C1",
                        quote=raw_values[1],
                        label=f"Total first-time, first-year students {verb}",
                    ),
                ]
            )

        separate_rows: dict[str, list[tuple[object, str]]] = {}
        for gender, gender_key in (
            ("men", "men"),
            ("women", "women"),
            ("of another gender", "another"),
            ("another gender", "another"),
            ("unknown gender", "unknown"),
        ):
            for verb, suffix in (("applied", "applied"), ("were admitted", "admitted"), ("enrolled", "enrolled")):
                match = re.search(
                    rf"(?im)(?:^|\n).*?(?:C1(?:\d{{2}})?\s+)?Total (?:full-time,\s*)?first-time,\s*first-year(?:\s*\(freshman\))?\s+"
                    rf"{re.escape(gender)}\s+who\s+(?:were\s+)?{verb.replace('were ', '')}\s+([\d,]+)(?:\s+.*)?$",
                    page.text,
                )
                if not match:
                    continue
                raw = match.group(1)
                value = _number(raw)
                if value is None:
                    continue
                separate_rows.setdefault(suffix, []).append((page, raw))
                if gender_key in {"men", "women"}:
                    observations.append(
                        _observation(
                            f"admissions.byGender.{gender_key}.{suffix}",
                            value,
                            packet_page=page,
                            question_id="C1",
                            quote=raw,
                            label=match.group(0),
                        )
                    )
        for suffix, cells in separate_rows.items():
            if len(cells) >= 2:
                observations.append(
                    _summed_cells_observation(
                        f"admissions.{suffix}", cells, question_id="C1"
                    )
                )

        direct_totals = (
            (r"Total first-time,\s*first-year \(degree-seeking\) who applied\s+([\d,]+)", "admissions.applied"),
            (r"Total first-time,\s*first-year \(degree-seeking\) who were admitted\s+([\d,]+)", "admissions.admitted"),
            (r"Total first-time,\s*first-year \(degree-seeking\)(?: who)? enrolled\s+([\d,]+)", "admissions.enrolled"),
        )
        for pattern, path in direct_totals:
            match = re.search(pattern, page.text, flags=re.IGNORECASE)
            if match and (value := _number(match.group(1))) is not None:
                observations.append(
                    _observation(
                        path,
                        value,
                        packet_page=page,
                        question_id="C1",
                        quote=match.group(1),
                        label=match.group(0),
                    )
                )

        early_decision_specs = (
            (
                r"(?im)^\s*Number of early decision applications received by your institution:\s*([\d,]+)\s*$",
                "admissions.earlyDecision.applied",
            ),
            (
                r"(?im)^\s*Number of applicants admitted under early decision plan:\s*([\d,]+)\s*$",
                "admissions.earlyDecision.admitted",
            ),
        )
        for pattern, path in early_decision_specs:
            match = re.search(pattern, page.text)
            if match and (value := _number(match.group(1))) is not None:
                observations.append(
                    _observation(
                        path,
                        value,
                        packet_page=page,
                        question_id="C21",
                        quote=match.group(1),
                        label=match.group(0),
                    )
                )

    observed_paths = {observation.path for observation in observations}
    for page in packet.pages:
        for row in _rows(page):
            row_label = _label(row[0])
            for needle, path, question_id in mappings:
                if path in observed_paths or needle not in row_label or len(row) < 2:
                    continue
                value = _number(row[1])
                if value is not None:
                    observations.append(
                        _observation(path, value, packet_page=page, question_id=question_id, quote=row[1] or "", label=row[0] or path)
                    )
                    observed_paths.add(path)
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
    text_specs = (
        (
            r"(?im)^\s*PRIVATE INSTITUTIONS?\s+(\$\s*[\d,]+(?:\.\d+)?)",
            "costs.tuition",
            "Private Institution",
        ),
        (r"(?im)^\s*Tuition:\s*(\$\s*[\d,]+(?:\.\d+)?)", "costs.tuition", "Tuition"),
        (r"(?im)^\s*(?:G1\s+)?Required Fees:?\s*(\$\s*[\d,]+(?:\.\d+)?)", "costs.fees", "Required Fees"),
        (
            r"(?im)^\s*(?:\(on-campus\)|Room and Board \(on-campus\)):?\s*(\$\s*[\d,]+(?:\.\d+)?)",
            "costs.roomAndBoard",
            "Room and Board (on-campus)",
        ),
        (
            r"(?im)^\s*ROOM AND BOARD:\s*(\$\s*[\d,]+(?:\.\d+)?)",
            "costs.roomAndBoard",
            "Room and Board",
        ),
        (
            r"(?im)^\s*Food and Housing \(on-campus\):\s*(\$[\d,]+(?:\.\d+)?)",
            "costs.roomAndBoard",
            "Food and Housing (on-campus)",
        ),
        (
            r"(?im)^\s*Housing Only \(on-campus\):\s*(\$[\d,]+(?:\.\d+)?)",
            "costs.room",
            "Housing Only (on-campus)",
        ),
        (
            r"(?im)^\s*Food Only \(on-campus meal plan\):\s*(\$[\d,]+(?:\.\d+)?)",
            "costs.board",
            "Food Only (on-campus meal plan)",
        ),
    )
    for pattern, path, label in text_specs:
        match = re.search(pattern, page.text)
        if match and (value := _number(match.group(1))) is not None:
            observations.append(
                _observation(
                    path,
                    value,
                    packet_page=page,
                    question_id="G1",
                    quote=match.group(1),
                    label=label,
                )
            )

    observed_paths = {observation.path for observation in observations}
    for row in _rows(page):
        row_label = _label(row[0])
        for needle, path in mappings:
            if path in observed_paths or needle not in row_label or len(row) < 2:
                continue
            if path in {"costs.room", "costs.board"} and "costs.roomAndBoard" in observed_paths:
                continue
            value = _number(row[1])
            if value is not None:
                observations.append(
                    _observation(path, value, packet_page=page, question_id="G1", quote=row[1] or "", label=row[0] or path)
                )
                observed_paths.add(path)
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
    text_score_labels = {
        "SAT Composite": score_rows["sat composite"],
        "SAT Evidence-Based Reading and Writing": score_rows[
            "sat evidence based reading and writing"
        ],
        "SAT Math": score_rows["sat math"],
        "ACT Composite": score_rows["act composite"],
    }
    for packet_page in packet.pages:
        for test_name, path in (
            ("SAT", "testScores.sat.submissionRate"),
            ("ACT", "testScores.act.submissionRate"),
        ):
            match = re.search(
                rf"(?im)^\s*(?:C9\s+)?(?:Percent\s+)?Submitting {test_name}(?: scores)?\s+(\d+(?:\.\d+)?%)",
                packet_page.text,
            )
            if match and (value := _number(match.group(1))) is not None:
                observations.append(
                    _observation(
                        path,
                        value,
                        packet_page=packet_page,
                        question_id="C9",
                        quote=match.group(1),
                        label=f"Submitting {test_name} Scores",
                    )
                )
        reading_match = re.search(
            r"(?im)^\s*(?:C9\s+)?SAT Evidence-Based(?:\s+Reading)?"
            r"\s*(?:and\s+Writing)?\s+(?P<values>\d+(?:\.\d+)?(?:\s+\d+(?:\.\d+)?){1,3})",
            packet_page.text,
        )
        if reading_match:
            raw_values = re.findall(r"\d+(?:\.\d+)?", reading_match.group("values"))
            p75_raw = raw_values[2] if len(raw_values) == 3 else raw_values[1]
            for path, raw in (
                ("testScores.sat.readingWriting.p25", raw_values[0]),
                ("testScores.sat.readingWriting.p75", p75_raw),
            ):
                if (value := _number(raw)) is not None:
                    observations.append(
                        _observation(
                            path,
                            value,
                            packet_page=packet_page,
                            question_id="C9",
                            quote=raw,
                            label="SAT Evidence-Based Reading and Writing",
                        )
                    )
        for label, (p25_path, p75_path) in text_score_labels.items():
            if label == "SAT Evidence-Based Reading and Writing":
                continue
            match = re.search(
                rf"(?im)^\s*(?:C9\s+)?{re.escape(label)}(?:\s*\([^\n]*\))?\s+"
                r"(?P<values>\d+(?:\.\d+)?(?:\s+\d+(?:\.\d+)?){1,3})\s*$",
                packet_page.text,
            )
            if not match:
                continue
            raw_values = re.findall(r"\d+(?:\.\d+)?", match.group("values"))
            p75_raw = raw_values[2] if len(raw_values) == 3 else raw_values[1]
            for path, raw in ((p25_path, raw_values[0]), (p75_path, p75_raw)):
                value = _number(raw)
                if value is not None:
                    observations.append(
                        _observation(
                            path,
                            value,
                            packet_page=packet_page,
                            question_id="C9",
                            quote=raw,
                            label=label,
                        )
                    )

    observed_paths = {observation.path for observation in observations}
    for packet_page in packet.pages:
        for table in packet_page.tables:
            table_text = _label(
                " ".join(cell or "" for row in table.rows for cell in row)
            )
            has_median_percentile_column = "50th percentile" in table_text
            for row in table.rows:
                if not row:
                    continue
                row_label = _label(row[0])
                if row_label in {"submitting sat scores", "submitting act scores"} and len(row) > 1:
                    path = (
                        "testScores.sat.submissionRate"
                        if "sat" in row_label
                        else "testScores.act.submissionRate"
                    )
                    value = _number(row[1])
                    normalized_percent = isinstance(value, (int, float)) and value > 1
                    if normalized_percent:
                        value /= 100
                    if path not in observed_paths and value is not None:
                        observation = _observation(
                            path,
                            value,
                            packet_page=packet_page,
                            question_id="C9",
                            quote=row[1] or "",
                            label=row[0] or path,
                        )
                        if normalized_percent:
                            observation.notes = "Percent value normalized from CDS numeric percent cell."
                        observations.append(observation)
                        observed_paths.add(path)
                elif row_label in score_rows:
                    numeric_cells = [
                        (cell, value)
                        for cell in row[1:]
                        if (value := _number(cell)) is not None
                    ]
                    if len(numeric_cells) < 2:
                        continue
                    p75_index = 2 if has_median_percentile_column and len(numeric_cells) >= 3 else 1
                    selected = (numeric_cells[0], numeric_cells[p75_index])
                    for path, (cell, value) in zip(score_rows[row_label], selected):
                        if path not in observed_paths:
                            observations.append(
                                _observation(
                                    path,
                                    value,
                                    packet_page=packet_page,
                                    question_id="C9",
                                    quote=cell or "",
                                    label=row[0] or path,
                                )
                            )
                            observed_paths.add(path)
    return observations


def _extract_enrollment(packet: SectionPacket) -> list[MetricObservation]:
    observations: list[MetricObservation] = []
    totals = (
        (
            r"(?im)^\s*(?:(?:B1\s+)?Total\s+(?:of\s+)?all\s+undergraduates?(?:\s+students)?(?:\s+enrolled)?|Totalallundergraduates):?\s+([\d,]+)\s*$",
            "demographics.enrollment.undergraduate",
        ),
        (
            r"(?im)^\s*(?:(?:B1\s+)?Total\s+(?:of\s+)?all\s+graduate(?:\s+and\s+professional)?(?:\s+students?)?(?:\s+enrolled)?|Totalallgraduate):?\s+([\d,]+)(?:\s+.*)?$",
            "demographics.enrollment.graduate",
        ),
        (
            r"(?im)^\s*(?:B1\s+)?(?:GRAND TOTAL ALL STUDENTS|GrandTotalAllStudents):?\s+([\d,]+)\s*$",
            "demographics.enrollment.total",
        ),
    )
    for page in packet.pages:
        for pattern, path in totals:
            match = re.search(pattern, page.text)
            if match and (value := _number(match.group(1))) is not None:
                observations.append(
                    _observation(
                        path,
                        value,
                        packet_page=page,
                        question_id="B1",
                        quote=match.group(1),
                        label=match.group(0),
                    )
                )

        split_race_patterns = (
            (
                r"(?im)^\s*(?:B2\s+)?Black or African American, non-\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*\n\s*Hispanic\s*$",
                "demographics.byRace.blackAfricanAmerican",
            ),
            (
                r"(?im)^\s*(?:B2\s+)?Native Hawaiian or other Pacific\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*\n\s*Islander, non-Hispanic\s*$",
                "demographics.byRace.nativeHawaiianPacificIslander",
            ),
        )
        for pattern, path in split_race_patterns:
            match = re.search(pattern, page.text)
            if match and (value := _number(match.group(3))) is not None:
                observations.append(
                    _observation(
                        path,
                        value,
                        packet_page=page,
                        question_id="B2",
                        quote=match.group(3),
                        label=match.group(0),
                    )
                )

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
    text_race_patterns = (
        (r"(?:International \(nonresidents\)|Nonresident aliens?|Nonresidents?)", "demographics.byRace.international"),
        (r"Hispanic/Latino", "demographics.byRace.hispanicLatino"),
        (r"Black or African American, non-\s*Hispanic", "demographics.byRace.blackAfricanAmerican"),
        (r"White, non-\s*Hispanic", "demographics.byRace.white"),
        (r"Asian, non-\s*Hispanic", "demographics.byRace.asian"),
        (r"American Indian or Alaska Native,\s*(?:non-\s*Hispanic|non-)", "demographics.byRace.americanIndianAlaskaNative"),
        (r"Native Hawaiian or other Pacific Islander,\s*(?:non-\s*Hispanic|non-)?", "demographics.byRace.nativeHawaiianPacificIslander"),
        (r"Two or more races, non-\s*Hispanic", "demographics.byRace.twoOrMoreRaces"),
        (r"Race and/or ethnicity unknown", "demographics.byRace.unknown"),
    )
    for page in packet.pages:
        for label_pattern, path in text_race_patterns:
            match = re.search(
                rf"(?im)^\s*(?:B2\s+)?{label_pattern}\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)(?:\s*(?:non-)?Hispanic)?\s*$",
                page.text,
            )
            if match and (value := _number(match.group(3))) is not None:
                observations.append(
                    _observation(
                        path,
                        value,
                        packet_page=page,
                        question_id="B2",
                        quote=match.group(3),
                        label=match.group(0),
                    )
                )

    observed_paths = {observation.path for observation in observations}
    for page in packet.pages:
        for row in _rows(page):
            path = mappings.get(_label(row[0]))
            if path in observed_paths or not path or len(row) < 2:
                continue
            value = _number(row[-1])
            if value is not None:
                observations.append(_observation(path, value, packet_page=page, question_id="B2", quote=row[-1] or "", label=row[0] or path))
                observed_paths.add(path)
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

    observed_paths = {observation.path for observation in observations}
    text_specs = (
        (
            r"H\. Number of students in line \(D\) who(?:se)? need was fully met.*?(\d[\d,]*)",
            "_source.financialAid.needFullyMetCount",
            "H. Number of students in line (D) whose need was fully met",
        ),
        (
            r"J\. The average financial aid package of those in line \(D\).*?(\$[\d,]+(?:\.\d+)?)",
            "financialAid.averageAidPackage",
            "J. The average financial aid package of those in line (D)",
        ),
        (
            r"K\. Average need-based scholarship or grant award of.*?(\$[\d,]+(?:\.\d+)?)",
            "financialAid.averageNeedBasedGrant",
            "K. Average need-based scholarship or grant award of those in line (E)",
        ),
    )
    for packet_page in packet.pages:
        flattened = re.sub(r"\s+", " ", packet_page.text)
        for pattern, path, label in text_specs:
            if path in observed_paths:
                continue
            match = re.search(pattern, flattened, flags=re.IGNORECASE)
            if match and (value := _number(match.group(1))) is not None:
                observations.append(
                    _observation(
                        path,
                        value,
                        packet_page=packet_page,
                        question_id="H2",
                        quote=match.group(1),
                        label=label,
                    )
                )
                observed_paths.add(path)
    return observations


def _extract_admissions_factors(packet: SectionPacket) -> list[MetricObservation]:
    factors = (
        ("rigor of secondary school record", "profile.admissionsFactors.academic.rigorOfSecondarySchoolRecord"),
        ("class rank", "profile.admissionsFactors.academic.classRank"),
        ("academic grade point average gpa", "profile.admissionsFactors.academic.academicGpa"),
        ("academic gpa", "profile.admissionsFactors.academic.academicGpa"),
        ("standardized test scores", "profile.admissionsFactors.academic.standardizedTestScores"),
        ("application essay", "profile.admissionsFactors.academic.applicationEssay"),
        ("recommendations", "profile.admissionsFactors.academic.recommendations"),
        ("recommendation", "profile.admissionsFactors.academic.recommendations"),
        ("interview", "profile.admissionsFactors.nonacademic.interview"),
        ("extracurriculuar activities", "profile.admissionsFactors.nonacademic.extracurricularActivities"),
        ("extracurricular activities", "profile.admissionsFactors.nonacademic.extracurricularActivities"),
        ("talent ability", "profile.admissionsFactors.nonacademic.talentAbility"),
        ("character personal qualities", "profile.admissionsFactors.nonacademic.characterPersonalQualities"),
        ("first generation", "profile.admissionsFactors.nonacademic.firstGeneration"),
        ("alumni ae relation", "profile.admissionsFactors.nonacademic.alumniRelation"),
        ("geographical residence", "profile.admissionsFactors.nonacademic.geographicalResidence"),
        ("state residency", "profile.admissionsFactors.nonacademic.stateResidency"),
        ("religious affiliation commitment", "profile.admissionsFactors.nonacademic.religiousAffiliationCommitment"),
        ("religious affilitation commitment", "profile.admissionsFactors.nonacademic.religiousAffiliationCommitment"),
        ("volunteer work", "profile.admissionsFactors.nonacademic.volunteerWork"),
        ("work experience", "profile.admissionsFactors.nonacademic.workExperience"),
        ("level of applicant s interest", "profile.admissionsFactors.nonacademic.levelOfApplicantsInterest"),
    )
    ratings = (
        ("not considered", "not_considered"),
        ("very important", "very_important"),
        ("important", "important"),
        ("considered", "considered"),
    )
    observations: list[MetricObservation] = []
    found: set[str] = set()
    for page in packet.pages:
        lines = page.text.splitlines()
        for raw_line in lines:
            line = _label(raw_line)
            compact_line = line.replace(" ", "")
            for needle, path in factors:
                if path in found or needle.replace(" ", "") not in compact_line:
                    continue
                rating = next(
                    (
                        value
                        for label, value in ratings
                        if compact_line.endswith(label.replace(" ", ""))
                    ),
                    None,
                )
                if rating is None:
                    continue
                observations.append(
                    MetricObservation(
                        path=path,
                        value=rating,
                        evidence=[
                            SourceEvidence(
                                document_id=page.document_id,
                                page=page.page,
                                question_id="C7",
                                quote=raw_line.strip()[-240:],
                            )
                        ],
                        method="native-rule",
                        confidence=1.0,
                        review_required=False,
                        notes="Exact C7 row label and rating parsed deterministically.",
                    )
                )
                found.add(path)
                break
        checkbox_ratings = ("very_important", "important", "considered", "not_considered")
        for index, raw_line in enumerate(lines):
            boxes = re.findall(r"[☒☐]", raw_line)
            if len(boxes) < 4 or "☒" not in boxes:
                continue
            rating = checkbox_ratings[boxes.index("☒")]
            label_text = raw_line.split("☒", 1)[0].split("☐", 1)[0]
            candidates = [label_text]
            if index > 0:
                candidates.append(lines[index - 1] + " " + label_text)
            if index + 1 < len(lines):
                candidates.extend(
                    [
                        label_text + " " + lines[index + 1],
                        (lines[index - 1] if index > 0 else "")
                        + " "
                        + label_text
                        + " "
                        + lines[index + 1],
                    ]
                )
            for candidate in candidates:
                compact_candidate = _label(candidate).replace(" ", "")
                match = next(
                    (
                        (needle, path)
                        for needle, path in factors
                        if path not in found
                        and needle.replace(" ", "") in compact_candidate
                    ),
                    None,
                )
                if match is None:
                    continue
                _, path = match
                quote_lines = lines[max(0, index - 1) : min(len(lines), index + 2)]
                observations.append(
                    MetricObservation(
                        path=path,
                        value=rating,
                        evidence=[
                            SourceEvidence(
                                document_id=page.document_id,
                                page=page.page,
                                question_id="C7",
                                quote="\n".join(quote_lines).strip()[-240:],
                            )
                        ],
                        method="native-rule",
                        confidence=1.0,
                        review_required=False,
                        notes="Exact C7 checkbox column parsed deterministically.",
                    )
                )
                found.add(path)
                break
    return observations


EXTRACTORS = {
    "admissions": _extract_admissions,
    "costs": _extract_costs,
    "test_scores": _extract_test_scores,
    "enrollment": _extract_enrollment,
    "financial_aid": _extract_financial_aid,
    "admissions_factors": _extract_admissions_factors,
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


def _section_is_explicitly_incomplete(packet: SectionPacket) -> bool:
    text = "\n".join(page.text for page in packet.pages)
    race_row_with_totals = re.search(
        r"(?im)^(?:B2\d*\s+)?(?:Nonresidents?|Hispanic/Latino|White,\s*non-Hispanic)"
        r"[^\n]*\b[\d,]+\s+[\d,]+\s+[\d,]+\s*$",
        text,
    )
    return bool(
        (
            packet.domain == "admissions"
            and re.search(r"(?m)^C101\b", text)
            and not re.search(r"(?m)^C(?:109|110)\b", text)
        )
        or (
            packet.domain == "costs"
            and re.search(r"(?m)^G101\b", text)
            and not re.search(r"(?m)^G(?:107|108)\b", text)
        )
        or (
            packet.domain == "enrollment"
            and re.search(r"(?m)^B101\b", text)
            and not re.search(r"(?im)Total\s+All\s+Undergraduates", text)
        )
        or (
            packet.domain == "enrollment"
            and re.search(r"(?im)^\s*B2[.\s]", text)
            and not race_row_with_totals
        )
        or (
            packet.domain == "admissions_factors"
            and 0 < len(re.findall(r"(?m)^C7\d{2}\b", text)) < len(packet.metric_paths)
        )
    )


def blocking_paths(packet: SectionPacket) -> set[str]:
    if _section_is_explicitly_incomplete(packet):
        return set()
    if packet.domain == "admissions_factors":
        return set(packet.metric_paths)
    if packet.domain == "costs" and not re.search(
        r"\$\s*\d", " ".join(page.text for page in packet.pages)
    ):
        return set()
    return set(BLOCKING_PATHS.get(packet.domain, set()))


def extract_packet_native(packet: SectionPacket) -> tuple[SectionExtraction, bool]:
    extractor = EXTRACTORS.get(packet.domain)
    observations = extractor(packet) if extractor else []
    allowed = set(packet.metric_paths)
    unique = {observation.path: observation for observation in observations if observation.path in allowed}
    required = REQUIRED_NATIVE_PATHS.get(packet.domain, set())
    if packet.domain == "costs" and not re.search(
        r"\$\s*\d", " ".join(page.text for page in packet.pages)
    ):
        # A routed G1 page with no reported currency values is an intentionally
        # blank section, not a reason to ask a model to invent costs.
        required = set()
    elif packet.domain == "financial_aid":
        required = set(unique)
    elif packet.domain == "test_scores":
        # Score rows change across CDS versions (some omit SAT composite or
        # medians entirely). They enrich a year but never gate publication.
        required = set(unique)
    elif packet.domain == "admissions_factors":
        required = set(packet.metric_paths)
    coded_section_is_incomplete = _section_is_explicitly_incomplete(packet)
    if coded_section_is_incomplete:
        required = set(unique)
    return (
        SectionExtraction(
            observations=list(unique.values()),
            notes=[
                "Coded CDS section is explicitly incomplete; model fallback was suppressed."
                if coded_section_is_incomplete
                else (
                    "C7 deterministically verified from exact row labels and ratings."
                    if packet.domain == "admissions_factors"
                    else "Stable CDS tables parsed deterministically before model extraction."
                )
            ],
        ),
        (packet.domain in EXTRACTORS) and required.issubset(unique),
    )
