from __future__ import annotations

from typing import Any

from .base import BaseExtractor, ExtractionResult


DEFAULT_SECTION_TARGETS = ["B1", "B2", "C1", "C9", "F1", "G1", "H2"]
SECTION_FIELD_MAP = {
    "B1": [
        "demographics.enrollment.undergraduate",
        "demographics.enrollment.graduate",
    ],
    "B2": [
        "demographics.byRace.international",
        "demographics.byRace.hispanicLatino",
        "demographics.byRace.blackAfricanAmerican",
        "demographics.byRace.white",
        "demographics.byRace.asian",
        "demographics.byRace.americanIndianAlaskaNative",
        "demographics.byRace.nativeHawaiianPacificIslander",
        "demographics.byRace.twoOrMoreRaces",
        "demographics.byRace.unknown",
    ],
    "C1": [
        "admissions.applied",
        "admissions.admitted",
        "admissions.enrolled",
    ],
    "C9": [
        "testScores.sat.submissionRate",
        "testScores.act.submissionRate",
        "testScores.sat.composite.p25",
        "testScores.sat.composite.p50",
        "testScores.sat.composite.p75",
        "testScores.sat.readingWriting.p25",
        "testScores.sat.readingWriting.p50",
        "testScores.sat.readingWriting.p75",
        "testScores.sat.math.p25",
        "testScores.sat.math.p50",
        "testScores.sat.math.p75",
        "testScores.act.composite.p25",
        "testScores.act.composite.p50",
        "testScores.act.composite.p75",
    ],
    "F1": [
        "demographics.byResidency.inState",
        "demographics.byResidency.outOfState",
        "demographics.byResidency.international",
        "computed.demographics.outOfStatePercent",
    ],
    "G1": [
        "costs.tuition",
        "costs.fees",
        "costs.roomAndBoard",
        "costs.totalCOA",
    ],
    "H2": [
        "financialAid.percentReceivingAid",
        "financialAid.averageAidPackage",
        "financialAid.averageNeedBasedGrant",
        "financialAid.percentNeedFullyMet",
    ],
}
SECTION_PROMPTS = {
    "B1": "Extract undergraduate and graduate enrollment counts from enrollment totals. Ignore labels that are academic years.",
    "B2": "Extract undergraduate race and ethnicity counts. Map Nonresident or Nonresident alien to international.",
    "C1": "Extract total first-time, first-year applicants, admitted students, and enrolled students.",
    "C9": "Extract SAT and ACT submission rates plus the visible percentile ranges. Only use values shown in the table.",
    "F1": "Extract first-time undergraduate residency counts if visible. If the page only shows out-of-state percentage, return it as computed.demographics.outOfStatePercent.",
    "G1": "Extract tuition, required fees, room and board or food and housing, and total cost if explicitly shown.",
    "H2": "Extract percent receiving aid, average aid package, average need-based grant, and percent of need fully met for first-year students.",
}


class VisionLLMExtractor(BaseExtractor):
    name = "VisionLLMExtractor"

    def extract(self, pdf_path: str, config: dict[str, Any]) -> ExtractionResult:
        notes: list[str] = []
        vision_config = config.get("vision", {}) if isinstance(config.get("vision"), dict) else {}
        if not vision_config.get("enabled", True):
            return ExtractionResult(extractor=self.name, payload={}, notes=["Vision extraction disabled by config."])

        try:
            import fitz  # type: ignore

            document = fitz.open(pdf_path)
        except Exception as exc:
            return ExtractionResult(extractor=self.name, payload={}, notes=[f"Vision page rendering failed: {exc}"])

        try:
            client = get_vision_client(config)
        except Exception as exc:
            return ExtractionResult(extractor=self.name, payload={}, notes=[f"Vision extractor unavailable: {exc}"])

        section_aliases = vision_config.get("section_aliases", {}) if isinstance(vision_config.get("section_aliases"), dict) else {}
        section_targets = vision_config.get("section_targets", DEFAULT_SECTION_TARGETS)
        page_hints = vision_config.get("page_range_hints", {}) if isinstance(vision_config.get("page_range_hints"), dict) else {}
        max_pages_per_section = max(1, int(vision_config.get("max_pages_per_section", 2)))
        classify_batch_size = max(1, int(vision_config.get("classify_batch_size", 6)))
        render_dpi = int(vision_config.get("render_dpi", 170))
        page_count = len(document)

        try:
            section_map: dict[str, dict[str, Any]] = {}
            for page_numbers in _batched_page_numbers(page_count, classify_batch_size):
                rendered_batch = [_render_pdf_page(document, page, dpi=render_dpi) for page in page_numbers]
                try:
                    batch_result = client.classify_pages(
                        page_images=rendered_batch,
                        section_aliases=section_aliases,
                    )
                except Exception as exc:
                    notes.append(f"Classification failed for pages {page_numbers[0]}-{page_numbers[-1]}: {exc}")
                    continue

                for page_result in batch_result.get("pages", []):
                    page_number = page_result.get("page")
                    if not isinstance(page_number, int):
                        continue
                    for item in page_result.get("sections", []):
                        section = item.get("section")
                        if section not in section_targets:
                            continue
                        entry = section_map.setdefault(section, {"pages": [], "confidence": 0.0})
                        if page_number not in entry["pages"]:
                            entry["pages"].append(page_number)
                        entry["confidence"] = max(float(item.get("confidence", 0.0)), float(entry["confidence"]))

            candidates: list[dict[str, Any]] = []
            missing_sections: list[str] = []
            for section in section_targets:
                pages = _select_pages_for_section(section, section_map, page_hints, page_count)
                pages = pages[:max_pages_per_section]
                if not pages:
                    missing_sections.append(section)
                    continue

                for page in pages:
                    try:
                        extracted = client.extract_section(
                            section=section,
                            page_number=page,
                            image_bytes=_render_pdf_page(document, page, dpi=render_dpi)["image_bytes"],
                            section_prompt=SECTION_PROMPTS[section],
                            allowed_fields=SECTION_FIELD_MAP[section],
                        )
                    except Exception as exc:
                        notes.append(f"Extraction failed for {section} on page {page}: {exc}")
                        continue

                    for candidate in extracted.get("candidates", []):
                        candidates.append(
                            {
                                "field": candidate.get("field"),
                                "value": candidate.get("value"),
                                "confidence": candidate.get("confidence"),
                                "evidence_label": candidate.get("evidence_label"),
                                "page": page,
                                "section": section,
                            }
                        )
                    notes.extend(extracted.get("notes", []))

            payload = {
                "vision_sections": {
                    section: {"pages": value["pages"], "confidence": round(float(value["confidence"]), 3)}
                    for section, value in section_map.items()
                },
                "vision_field_candidates": candidates,
                "vision_missing_sections": missing_sections,
                "vision_notes": notes,
                "vision_rendered_page_count": page_count,
            }
            return ExtractionResult(extractor=self.name, payload=payload, notes=notes)
        finally:
            document.close()


def get_vision_client(config: dict[str, Any]) -> Any:
    from ..openai_client import OpenAIVisionClient

    vision_config = config.get("vision", {}) if isinstance(config.get("vision"), dict) else {}
    return OpenAIVisionClient(model=vision_config.get("model"))


def _render_pdf_page(document: Any, page_number: int, *, dpi: int) -> dict[str, Any]:
    page = document.load_page(page_number - 1)
    pixmap = page.get_pixmap(dpi=dpi, alpha=False)
    return {"page": page_number, "image_bytes": pixmap.tobytes("png")}


def _select_pages_for_section(
    section: str,
    section_map: dict[str, dict[str, Any]],
    page_hints: dict[str, Any],
    page_count: int,
) -> list[int]:
    hinted_pages = _expand_hint_pages(page_hints.get(section), page_count)
    found_pages = sorted(set(section_map.get(section, {}).get("pages", [])))
    if hinted_pages:
        intersection = [page for page in found_pages if page in hinted_pages]
        if intersection:
            return intersection
        return hinted_pages
    return found_pages


def _expand_hint_pages(raw_hint: Any, page_count: int) -> list[int]:
    if raw_hint is None:
        return []
    if isinstance(raw_hint, int):
        return [raw_hint] if 1 <= raw_hint <= page_count else []
    if isinstance(raw_hint, list):
        if len(raw_hint) == 2 and all(isinstance(item, int) for item in raw_hint):
            start, end = raw_hint
            start = max(1, start)
            end = min(page_count, end)
            return list(range(start, end + 1)) if start <= end else []
        return [item for item in raw_hint if isinstance(item, int) and 1 <= item <= page_count]
    return []


def _batched_page_numbers(page_count: int, batch_size: int) -> list[list[int]]:
    batches: list[list[int]] = []
    current: list[int] = []
    for page_number in range(1, page_count + 1):
        current.append(page_number)
        if len(current) == batch_size:
            batches.append(current)
            current = []
    if current:
        batches.append(current)
    return batches
