from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from cds_pipeline.discovery import (
    COLLEGE_TRANSITIONS_URL,
    discover_repository_candidates,
    extract_candidates_from_page,
)
from cds_pipeline.compiler import PUBLISH_REQUIRED_PATHS, compile_school
from cds_pipeline.cli import _PipelineRunFailure, _cmd_add, build_parser
from cds_pipeline.downloader import _direct_download_url, download_discovered_sources
from cds_pipeline.document import analyze_pdf
from cds_pipeline.extractor import (
    _strict_codex_schema,
    extract_packet_codex,
    extract_packet_local,
    extractor_chain,
)
from cds_pipeline.models import DiscoveryManifest, DocumentArtifact, DownloadRecord, PageArtifact, SourceCandidate
from cds_pipeline.models import PacketPage, SectionPacket, TableArtifact
from cds_pipeline.native import extract_packet_native
from cds_pipeline.ocr import OllamaOcrProvider, OcrResult, _clean_unlimited_ocr_text
from cds_pipeline.pipeline import _build_packets, _extract_packets, add_school
from cds_pipeline.registry import generate_registry
from cds_pipeline.rescue import RescueDecision, recovery_sources, run_codex_rescue
from cds_pipeline.specs import extract_question_ids
from cds_pipeline.utils import extract_year_from_filename, validate_slug
from cds_pipeline.utils import sha256_file
from cds_pipeline.validator import validate_section_extraction, validate_year_data


class EvidencePipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        try:
            import fitz  # type: ignore
        except Exception as exc:  # pragma: no cover
            self.skipTest(f"PyMuPDF unavailable: {exc}")
        self.fitz = fitz

    def test_add_routes_cds_sections_and_renders_only_visual_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf_path = root / "sample-cds-2024-25.pdf"
            self._make_pdf(
                pdf_path,
                [
                    "Common Data Set 2024-2025\nSample University",
                    "B1. Institutional Enrollment\nB2. Enrollment by racial/ethnic category",
                    "C1. First-time, first-year admission\nApplicants 1000 Admitted 300 Enrolled 200",
                    "C7. Relative importance of each academic and nonacademic factor",
                    "C9. Percent and number of first-time students submitting SAT and ACT",
                    "G1. Undergraduate full-time tuition and required fees",
                    "H1. Financial aid awarded\nH2. Need-based financial aid",
                ],
                pad=True,
            )
            manifest = add_school(
                str(root),
                school_name="Sample University",
                school_slug="sample",
                workspace_dir=root / "workspace",
                jobs=1,
                ocr_provider="none",
            )
            self.assertEqual(len(manifest.documents), 1)
            self.assertEqual(manifest.documents[0].document_type, "cds")
            self.assertEqual(manifest.documents[0].academic_year, "2024-2025")
            self.assertEqual(len(manifest.packet_paths), 6)
            rendered = [page for page in manifest.documents[0].pages if page.image_path]
            self.assertEqual([page.page for page in rendered], [2, 4, 7])

    def test_discovered_year_limit_does_not_rescan_cached_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selected = root / "college-data" / "sample-cds-2024-2025.pdf"
            selected.parent.mkdir(parents=True)
            selected.touch()
            artifact = DocumentArtifact(
                document_id="sha256:selected",
                source_path=str(selected.resolve()),
                filename=selected.name,
                sha256="selected",
                size_bytes=0,
                page_count=0,
                school_name="Sample College",
                school_slug="samplecollege",
                academic_year="2024-2025",
                year_verified=True,
                document_type="cds",
                classification_score=1,
            )

            with (
                patch("cds_pipeline.pipeline.resolve_pdf_paths") as resolve,
                patch(
                    "cds_pipeline.pipeline.discover_school",
                    return_value=SimpleNamespace(warnings=[]),
                ),
                patch(
                    "cds_pipeline.pipeline.download_discovered_sources",
                    return_value=(
                        selected.parent,
                        [SimpleNamespace(local_path=str(selected.resolve()))],
                        [],
                    ),
                ),
                patch("cds_pipeline.pipeline.analyze_pdf", return_value=artifact) as analyze,
                patch("cds_pipeline.pipeline._build_packets", return_value=[]),
            ):
                manifest = add_school(
                    "Sample College",
                    workspace_dir=root / "workspace",
                    college_data_dir=selected.parent,
                    download_years=1,
                    jobs=1,
                )

            self.assertEqual(resolve.call_count, 0)
            self.assertEqual(analyze.call_args.args[0], selected.resolve())
            self.assertEqual(len(manifest.documents), 1)

    def test_unrelated_research_pdf_is_rejected_and_not_year_2095(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf_path = root / "2603.20957v3.pdf"
            self._make_pdf(pdf_path, ["A research paper about machine learning and statistics."])
            artifact = analyze_pdf(
                pdf_path,
                school_name="Sample University",
                school_slug="sample",
                document_dir=root / "artifact",
            )
            self.assertEqual(artifact.document_type, "unknown")
            self.assertIsNone(artifact.academic_year)
            self.assertNotIn("2095-2096", artifact.year_candidates)

    def test_question_signature_recognizes_cds_without_title_phrase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf_path = root / "sample-cds-2024-25.pdf"
            self._make_pdf(
                pdf_path,
                [
                    "B1. Institutional Enrollment\nB2. Enrollment by racial category",
                    "C1. First-time admission\nC7. Relative importance\nC9. SAT submissions",
                    "G1. Undergraduate full-time tuition",
                    "H1. Financial aid\nH2. Need-based financial aid",
                ],
                pad=True,
            )
            artifact = analyze_pdf(
                pdf_path,
                school_name="Sample University",
                school_slug="sample",
                document_dir=root / "artifact",
            )
            self.assertEqual(artifact.document_type, "cds")
            self.assertGreaterEqual(artifact.classification_score, 0.85)

    def test_scanned_document_is_ocrd_before_classification(self) -> None:
        class FakeOcr:
            name = "fake-ocr"

            def extract_page(self, image_path: Path) -> OcrResult:
                return OcrResult(
                    method=self.name,
                    text=(
                        "Common Data Set 2024-2025\nSample University\n"
                        "B1. Enrollment\nB2. Race\nC1. Admissions\nC7. Factors\n"
                        "C9. Tests\nG1. Tuition\nH1. Aid\nH2. Need aid"
                    ),
                )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf_path = root / "scan-cds-2024-25.pdf"
            self._make_pdf(pdf_path, [""])
            with patch("cds_pipeline.pipeline.create_ocr_provider", return_value=FakeOcr()):
                manifest = add_school(
                    str(pdf_path),
                    school_name="Sample University",
                    school_slug="sample",
                    workspace_dir=root / "workspace",
                    jobs=1,
                    ocr_provider="fake",
                )
            self.assertEqual(manifest.documents[0].document_type, "cds")
            self.assertTrue(manifest.documents[0].year_verified)
            self.assertFalse(manifest.documents[0].ocr_pending_pages)
            self.assertEqual(len(manifest.packet_paths), 6)
            self.assertFalse(manifest.review_required)

    def test_filename_year_parser_handles_short_cds_years(self) -> None:
        self.assertEqual(extract_year_from_filename("24-25-Columbia-CDS.pdf"), "2024-2025")
        self.assertEqual(extract_year_from_filename("CDS_2425_Princeton_v2.pdf"), "2024-2025")
        self.assertEqual(extract_year_from_filename("2603.20957v3.pdf"), "unknown")

    def test_validator_blocks_impossible_admissions_order(self) -> None:
        result = validate_year_data(
            {
                "admissions": {
                    "applied": 100,
                    "admitted": 110,
                    "enrolled": 50,
                    "acceptanceRate": 1.1,
                    "yield": 0.4545,
                }
            }
        )
        self.assertGreater(result["error_count"], 0)

    def test_validator_blocks_cost_and_race_reconciliation_errors(self) -> None:
        result = validate_year_data(
            {
                "demographics": {
                    "enrollment": {"undergraduate": 100},
                    "byRace": {"white": 80, "asian": 40},
                },
                "costs": {
                    "tuition": 50,
                    "fees": 10,
                    "roomAndBoard": 20,
                    "totalCOA": 70,
                },
            }
        )
        kinds = {issue["kind"] for issue in result["issues"]}
        self.assertIn("race_total_exceeds_undergraduate", kinds)
        self.assertIn("cost_total_mismatch", kinds)

    def test_official_archive_parser_finds_pdf_and_box_links(self) -> None:
        html = """
        <a href="/files/cds-2024-2025.pdf">Common Data Set 2024-2025 [pdf]</a>
        <a href="https://sample.box.com/s/abc123">Common Data Set 2023-2024 [pdf]</a>
        <a href="/about">About the college</a>
        """
        candidates, unsupported = extract_candidates_from_page(
            html,
            page_url="https://www.sample.edu/research/common-data-set",
            official=True,
        )
        self.assertEqual([item.academic_year for item in candidates], ["2024-2025", "2023-2024"])
        self.assertTrue(all(item.official for item in candidates))
        self.assertFalse(unsupported)

    def test_repository_parser_maps_table_headers_to_years(self) -> None:
        html = """
        <table>
          <tr><th>Institution</th><th>2024-25</th><th>2023-24</th></tr>
          <tr><td>Sample University</td>
            <td><a href="https://drive.google.com/file/d/new/view">CDS</a></td>
            <td><a href="https://drive.google.com/file/d/old/view">CDS</a></td>
          </tr>
        </table>
        """

        class FakeClient:
            def get_text(self, url: str, timeout: int = 60) -> str:
                self.last_url = url
                return html

        candidates, warnings = discover_repository_candidates("Sample University", FakeClient())
        self.assertEqual(FakeClient.__name__, "FakeClient")
        self.assertEqual([item.academic_year for item in candidates], ["2024-2025", "2023-2024"])
        self.assertFalse(warnings)
        self.assertTrue(all(not item.official for item in candidates))

    def test_download_url_rewrites_drive_and_box_shares(self) -> None:
        drive = _direct_download_url("https://drive.google.com/file/d/file123/view?usp=sharing")
        box = _direct_download_url("https://sample.box.com/s/share123")
        self.assertIn("drive.usercontent.google.com/download?id=file123", drive)
        self.assertEqual(box, "https://sample.box.com/shared/static/share123.pdf")

    def test_downloader_falls_back_when_official_source_fails(self) -> None:
        discovery = DiscoveryManifest(
            school_name="Sample University",
            school_slug="sample",
            candidates=[
                SourceCandidate(
                    url="https://sample.edu/missing.pdf",
                    label="Official",
                    academic_year="2024-2025",
                    discovery_source="official_site",
                    discovery_url="https://sample.edu/archive",
                    official=True,
                    score=1.0,
                ),
                SourceCandidate(
                    url="https://drive.google.com/file/d/mirror/view",
                    label="Mirror",
                    academic_year="2024-2025",
                    discovery_source="college_transitions",
                    discovery_url=COLLEGE_TRANSITIONS_URL,
                    official=False,
                    score=0.5,
                ),
            ],
        )
        calls: list[str] = []

        def fake_download(candidate: SourceCandidate, destination: Path) -> DownloadRecord:
            calls.append(candidate.url)
            if candidate.official:
                raise ValueError("404")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(b"%PDF-mirror")
            return DownloadRecord(
                source_url=candidate.url,
                resolved_url=candidate.url,
                discovery_source=candidate.discovery_source,
                official=candidate.official,
                academic_year=candidate.academic_year,
                local_path=str(destination),
                sha256=sha256_file(destination),
                size_bytes=11,
                content_type="application/pdf",
            )

        with tempfile.TemporaryDirectory() as tmp, patch(
            "cds_pipeline.downloader._download_pdf", side_effect=fake_download
        ):
            _, records, warnings = download_discovered_sources(
                discovery, college_data_dir=tmp, years=1
            )
            _, resumed_records, resumed_warnings = download_discovered_sources(
                discovery, college_data_dir=tmp, years=1
            )
        self.assertEqual(calls, [discovery.candidates[0].url, discovery.candidates[1].url])
        self.assertEqual(len(records), 1)
        self.assertFalse(warnings)
        self.assertEqual(len(resumed_records), 1)
        self.assertFalse(resumed_warnings)

    def test_unlimited_ocr_cleanup_keeps_text_after_grounding_tags(self) -> None:
        raw = "<|ref|>table<|/ref|><|det|>table [[1,2,3,4]]<|/det|>Applicants 1,000"
        self.assertEqual(_clean_unlimited_ocr_text(raw), "tableApplicants 1,000")

    def test_ollama_ocr_uses_local_vision_model_without_key(self) -> None:
        captured: dict[str, object] = {}

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self) -> bytes:
                return json.dumps({"message": {"content": "C1 Applicants 1,000"}}).encode()

        def fake_urlopen(request, timeout):
            captured["payload"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse()

        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "page.png"
            image.write_bytes(b"not-a-real-png")
            with patch("cds_pipeline.ocr.urlopen", side_effect=fake_urlopen):
                result = OllamaOcrProvider().extract_page(image)
        self.assertEqual(result.text, "C1 Applicants 1,000")
        self.assertEqual(captured["payload"]["model"], "qwen3.5:9b")
        self.assertFalse(captured["payload"]["think"])

    def test_local_extractor_uses_ollama_schema_and_verifies_quote(self) -> None:
        packet = self._sample_packet()
        response_payload = {
            "message": {
                "content": json.dumps(
                    {
                        "observations": [
                            {
                                "path": "admissions.applied",
                                "value": 1000,
                                "confidence": 0.98,
                                "evidence": [
                                    {
                                        "document_id": "sha256:sample",
                                        "page": 3,
                                        "question_id": "C1",
                                        "quote": "Applicants 1,000",
                                    }
                                ],
                            }
                        ]
                    }
                )
            }
        }

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self) -> bytes:
                return json.dumps(response_payload).encode("utf-8")

        with patch("cds_pipeline.extractor.urlopen", return_value=FakeResponse()) as request:
            extraction = extract_packet_local(packet)
        self.assertEqual(extraction.observations[0].value, 1000)
        self.assertFalse(extraction.observations[0].review_required)
        sent = json.loads(request.call_args.args[0].data.decode("utf-8"))
        self.assertEqual(sent["model"], "gemma4:12b")
        self.assertFalse(sent["think"])
        self.assertEqual(sent["options"]["num_ctx"], 16384)
        self.assertEqual(sent["format"]["type"], "object")

    def test_native_cost_extractor_uses_first_year_column(self) -> None:
        page = PacketPage(
            document_id="sha256:costs",
            source_path="costs.pdf",
            page=20,
            question_ids=["G1"],
            text="REQUIRED FEES: $2,950 $2,850",
            tables=[
                TableArtifact(
                    rows=[
                        ["", "First-Year", "Undergraduates"],
                        ["PRIVATE INSTITUTIONS\nTuition:", "$71,700", "$71,700"],
                        ["REQUIRED FEES:", "$2,950", "$2,850"],
                        ["Food and housing (on-campus):", "$18,514", "$18,514"],
                    ]
                )
            ],
        )
        packet = SectionPacket(
            school_name="Brown University",
            school_slug="brown",
            academic_year="2024-2025",
            domain="costs",
            metric_paths=["costs.tuition", "costs.fees", "costs.roomAndBoard"],
            pages=[page],
        )
        extraction, complete = extract_packet_native(packet)
        values = {observation.path: observation.value for observation in extraction.observations}
        self.assertTrue(complete)
        self.assertEqual(values["costs.fees"], 2950)
        self.assertTrue(all(observation.method == "native-rule" for observation in extraction.observations))

    def test_native_admissions_sums_flattened_gender_columns(self) -> None:
        page = PacketPage(
            document_id="sha256:pomona",
            source_path="pomona.pdf",
            page=13,
            question_ids=["C1"],
            text=(
                "C1. Applications: First-time, First-year Students\n"
                "Total first-time, first-year students who applied in Fall 2023  4,985  7,133  3\n"
                "Total first-time, first-year students admitted in Fall 2023  377  440  2\n"
                "Total first-time, first-year students enrolled in Fall 2023  189  217  2\n"
            ),
        )
        packet = SectionPacket(
            school_name="Pomona College",
            school_slug="pomonacollege",
            academic_year="2023-2024",
            domain="admissions",
            metric_paths=[
                "admissions.applied",
                "admissions.admitted",
                "admissions.enrolled",
                "admissions.byGender.men.applied",
                "admissions.byGender.women.applied",
            ],
            pages=[page],
        )
        extraction, complete = extract_packet_native(packet)
        values = {observation.path: observation.value for observation in extraction.observations}
        self.assertTrue(complete)
        self.assertEqual(values["admissions.applied"], 12121)
        self.assertEqual(values["admissions.admitted"], 819)
        self.assertEqual(values["admissions.enrolled"], 408)
        self.assertEqual(values["admissions.byGender.men.applied"], 4985)
        self.assertEqual(values["admissions.byGender.women.applied"], 7133)

    def test_native_legacy_pomona_rows_avoid_model_fallback(self) -> None:
        packet = SectionPacket(
            school_name="Pomona College",
            school_slug="pomonacollege",
            academic_year="2017-2018",
            domain="admissions",
            metric_paths=[
                "admissions.applied",
                "admissions.admitted",
                "admissions.enrolled",
                "admissions.byGender.men.applied",
                "admissions.byGender.women.applied",
                "admissions.byGender.men.admitted",
                "admissions.byGender.women.admitted",
                "admissions.byGender.men.enrolled",
                "admissions.byGender.women.enrolled",
            ],
            pages=[
                PacketPage(
                    document_id="sha256:pomona-old",
                    source_path="pomona-old.pdf",
                    page=8,
                    question_ids=["C1"],
                    text=(
                        "C1 Total first-time, first-year (freshman) men who applied 3500\n"
                        "C1 Total first-time, first-year (freshman) women who applied 5545\n"
                        "C1 Total first-time, first-year (freshman) men who were admitted 357\n"
                        "C1 Total first-time, first-year (freshman) women who were admitted 399\n"
                        "C1 Total full-time, first-time, first-year (freshman) men who enrolled 192\n"
                        "C1 Total full-time, first-time, first-year (freshman) women who enrolled 220\n"
                    ),
                )
            ],
        )
        extraction, complete = extract_packet_native(packet)
        values = {observation.path: observation.value for observation in extraction.observations}
        self.assertTrue(complete)
        self.assertEqual(values["admissions.applied"], 9045)
        self.assertEqual(values["admissions.admitted"], 756)
        self.assertEqual(values["admissions.enrolled"], 412)

    def test_native_legacy_rows_accept_underscores_and_sum_part_time_enrollment(self) -> None:
        packet = SectionPacket(
            school_name="Bowdoin College",
            school_slug="bowdoincollege",
            academic_year="2018-2019",
            domain="admissions",
            metric_paths=[
                "admissions.applied",
                "admissions.admitted",
                "admissions.enrolled",
                "admissions.byGender.men.enrolled",
                "admissions.byGender.women.enrolled",
            ],
            pages=[
                PacketPage(
                    document_id="sha256:bowdoin-old",
                    source_path="bowdoin-old.pdf",
                    page=7,
                    question_ids=["C1"],
                    text=(
                        "Total first-time, first-year (freshman) men who applied _____3,741____\n"
                        "Total first-time, first-year (freshman) women who applied _____5,340____\n"
                        "Total first-time, first-year (freshman) men who were admitted ______433____\n"
                        "Total first-time, first-year (freshman) women who were admitted ______499____\n"
                        "Total full-time, first-time, first-year (freshman) men who enrolled ______244____\n"
                        "Total part-time, first-time, first-year (freshman) men who enrolled ________0____\n"
                        "Total full-time, first-time, first-year (freshman) women who enrolled ______266____\n"
                        "Total part-time, first-time, first-year (freshman) women who enrolled ________0____\n"
                    ),
                )
            ],
        )
        extraction, complete = extract_packet_native(packet)
        values = {observation.path: observation.value for observation in extraction.observations}
        self.assertTrue(complete)
        self.assertEqual(values["admissions.applied"], 9081)
        self.assertEqual(values["admissions.admitted"], 932)
        self.assertEqual(values["admissions.enrolled"], 510)
        self.assertEqual(values["admissions.byGender.men.enrolled"], 244)
        self.assertEqual(values["admissions.byGender.women.enrolled"], 266)

    def test_native_financial_aid_uses_lettered_h2_rows(self) -> None:
        packet = SectionPacket(
            school_name="Bowdoin College",
            school_slug="bowdoincollege",
            academic_year="2024-2025",
            domain="financial_aid",
            metric_paths=[
                "_source.financialAid.cohortSize",
                "_source.financialAid.aidRecipientCount",
                "_source.financialAid.financialNeedCount",
                "_source.financialAid.needFullyMetCount",
                "financialAid.averageAidPackage",
                "financialAid.averageNeedBasedGrant",
            ],
            pages=[
                PacketPage(
                    document_id="sha256:bowdoin-aid",
                    source_path="bowdoin-aid.pdf",
                    page=31,
                    question_ids=["H2"],
                    text="H2. Number of Enrolled Students Awarded Aid",
                    tables=[
                        TableArtifact(
                            rows=[
                                ["A", "Number of degree-seeking undergraduate students", "507"],
                                ["C", "Number of students determined to have financial need", "268"],
                                ["D", "Number of students awarded any financial aid", "268"],
                                ["H", "Number of students whose need was fully met", "268"],
                                ["J", "The average financial aid package", "$68055"],
                                ["K", "Average need-based scholarship or grant award", "$66151"],
                            ]
                        )
                    ],
                )
            ],
        )
        extraction, complete = extract_packet_native(packet)
        values = {observation.path: observation.value for observation in extraction.observations}
        self.assertTrue(complete)
        self.assertEqual(values["financialAid.averageAidPackage"], 68055)
        self.assertEqual(values["financialAid.averageNeedBasedGrant"], 66151)

    def test_native_score_extractor_normalizes_numeric_percent_cells(self) -> None:
        packet = SectionPacket(
            school_name="Bowdoin College",
            school_slug="bowdoincollege",
            academic_year="2024-2025",
            domain="test_scores",
            metric_paths=["testScores.sat.submissionRate", "testScores.act.submissionRate"],
            pages=[
                PacketPage(
                    document_id="sha256:bowdoin-c9",
                    source_path="bowdoin-c9.pdf",
                    page=17,
                    question_ids=["C9"],
                    text="Submitting SAT Scores 31.16 158\nSubmitting ACT Scores 16.77 85",
                )
            ],
        )
        extraction, complete = extract_packet_native(packet)
        values = {observation.path: observation.value for observation in extraction.observations}
        self.assertTrue(complete)
        self.assertEqual(values["testScores.sat.submissionRate"], 0.3116)
        self.assertEqual(values["testScores.act.submissionRate"], 0.1677)
        self.assertTrue(
            all(
                observation.notes == "Percent value normalized from CDS numeric percent cell."
                for observation in extraction.observations
            )
        )

    def test_native_legacy_score_table_uses_second_column_as_p75(self) -> None:
        packet = SectionPacket(
            school_name="Swarthmore College",
            school_slug="swarthmorecollege",
            academic_year="2019-2020",
            domain="test_scores",
            metric_paths=[
                "testScores.sat.composite.p25",
                "testScores.sat.composite.p75",
                "testScores.act.composite.p25",
                "testScores.act.composite.p75",
            ],
            pages=[
                PacketPage(
                    document_id="sha256:swarthmore-scores",
                    source_path="swarthmore.pdf",
                    page=12,
                    question_ids=["C9"],
                    text=(
                        "SAT Composite 1390 1530 1452 1470\n"
                        "ACT Composite 31 35 32.4 33\n"
                    ),
                    tables=[
                        TableArtifact(
                            rows=[
                                ["Assessment", "25th Percentile", "75th Percentile", "Average", "Median"],
                                ["SAT Composite", "1390", "1530", "1452", "1470"],
                                ["ACT Composite", "31", "35", "32.4", "33"],
                            ]
                        )
                    ],
                )
            ],
        )
        extraction, complete = extract_packet_native(packet)
        values = {observation.path: observation.value for observation in extraction.observations}
        self.assertTrue(complete)
        self.assertEqual(values["testScores.sat.composite.p75"], 1530)
        self.assertEqual(values["testScores.act.composite.p75"], 35)

    def test_extraction_cache_reuses_identical_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet_path = Path(tmp) / "packets" / "2024-2025" / "admissions.json"
            packet_path.parent.mkdir(parents=True)
            packet = SectionPacket(
                school_name="Sample University",
                school_slug="sample",
                academic_year="2024-2025",
                domain="admissions",
                metric_paths=["admissions.applied", "admissions.admitted", "admissions.enrolled"],
                pages=[
                    PacketPage(
                        document_id="sha256:sample",
                        source_path="sample.pdf",
                        page=1,
                        question_ids=["C1"],
                        text=(
                            "Total first-time, first-year students applied 60 40\n"
                            "Total first-time, first-year students admitted 20 10\n"
                            "Total first-time, first-year students enrolled 8 7\n"
                        ),
                    )
                ],
            )
            packet_path.write_text(packet.model_dump_json(), encoding="utf-8")
            paths, first_hits = _extract_packets(
                [str(packet_path)], extractor_name="local", model=None, jobs=1
            )
            cached_paths, second_hits = _extract_packets(
                [str(packet_path)], extractor_name="local", model=None, jobs=1
            )
            packet.pages[0].text = packet.pages[0].text.replace("60 40", "61 40")
            packet_path.write_text(packet.model_dump_json(), encoding="utf-8")
            _, changed_packet_hits = _extract_packets(
                [str(packet_path)], extractor_name="local", model=None, jobs=1
            )
        self.assertEqual(first_hits, 0)
        self.assertEqual(second_hits, 1)
        self.assertEqual(changed_packet_hits, 0)
        self.assertEqual(paths, cached_paths)

    def test_question_parser_does_not_treat_numeric_table_row_as_g1(self) -> None:
        self.assertEqual(extract_question_ids("G     1     2     0\nH2 Number of students"), ["H2"])

    def test_packet_builder_keeps_native_text_continuation_page(self) -> None:
        document = DocumentArtifact(
            document_id="sha256:continuation",
            source_path="continuation.pdf",
            filename="continuation.pdf",
            sha256="0" * 64,
            size_bytes=1,
            page_count=2,
            school_name="Sample University",
            school_slug="sample",
            academic_year="2024-2025",
            document_type="cds",
            pages=[
                PageArtifact(
                    page=1,
                    width=612,
                    height=792,
                    text="B2 Enrollment by Racial/Ethnic Category",
                    question_ids=["B2"],
                    domains=["enrollment"],
                ),
                PageArtifact(
                    page=2,
                    width=612,
                    height=792,
                    text="International 10 20 30",
                    domains=["enrollment"],
                ),
            ],
        )
        with tempfile.TemporaryDirectory() as tmp:
            paths = _build_packets(
                [document],
                workspace=Path(tmp),
                school_name="Sample University",
                school_slug="sample",
            )
            packet = SectionPacket.model_validate_json(Path(paths[0]).read_text(encoding="utf-8"))
        self.assertEqual([page.page for page in packet.pages], [1, 2])

    def test_packet_builder_keeps_table_prefix_before_next_question(self) -> None:
        document = DocumentArtifact(
            document_id="sha256:split-table",
            source_path="split-table.pdf",
            filename="split-table.pdf",
            sha256="0" * 64,
            size_bytes=1,
            page_count=2,
            school_name="Sample University",
            school_slug="sample",
            academic_year="2024-2025",
            document_type="cds",
            pages=[
                PageArtifact(
                    page=1,
                    width=612,
                    height=792,
                    text="B2. Enrollment by Racial/Ethnic Category",
                    question_ids=["B2"],
                    domains=["enrollment"],
                ),
                PageArtifact(
                    page=2,
                    width=612,
                    height=792,
                    text="Nonresidents 41 125 129\nB3. Persistence",
                    question_ids=["B3"],
                ),
            ],
        )
        with tempfile.TemporaryDirectory() as tmp:
            paths = _build_packets(
                [document],
                workspace=Path(tmp),
                school_name="Sample University",
                school_slug="sample",
            )
            packet = SectionPacket.model_validate_json(Path(paths[0]).read_text(encoding="utf-8"))
        self.assertEqual([page.page for page in packet.pages], [1, 2])
        self.assertEqual(packet.pages[1].question_ids, ["B2"])
        self.assertEqual(packet.pages[1].text, "Nonresidents 41 125 129")

    def test_codex_extractor_uses_saved_auth_and_read_only_schema_output(self) -> None:
        packet = self._sample_packet()
        captured: dict[str, object] = {}

        def fake_run(command, **kwargs):
            captured["command"] = command
            captured["environment"] = kwargs["env"]
            output_path = Path(command[command.index("--output-last-message") + 1])
            output_path.write_text(
                json.dumps(
                    {
                        "observations": [
                            {
                                "path": "admissions.applied",
                                "value": 1000,
                                "confidence": 0.99,
                                "evidence": [
                                    {
                                        "document_id": "sha256:sample",
                                        "page": 3,
                                        "question_id": "C1",
                                        "quote": "Applicants 1,000",
                                    }
                                ],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        with patch("cds_pipeline.extractor._codex_binary", return_value="codex"), patch(
            "cds_pipeline.extractor.subprocess.run", side_effect=fake_run
        ), patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "should-not-pass",
                "CODEX_API_KEY": "also-remove",
                "DATABASE_URL": "must-not-pass",
            },
        ):
            extraction = extract_packet_codex(packet)
        command = captured["command"]
        self.assertIn("read-only", command)
        self.assertIn("never", command)
        self.assertIn("--output-schema", command)
        self.assertIn("--skip-git-repo-check", command)
        self.assertNotIn("OPENAI_API_KEY", captured["environment"])
        self.assertNotIn("CODEX_API_KEY", captured["environment"])
        self.assertNotIn("DATABASE_URL", captured["environment"])
        self.assertEqual(extraction.observations[0].value, 1000)

    def test_auto_extractor_uses_signed_in_codex_by_default(self) -> None:
        with patch("cds_pipeline.extractor.ollama_model_available", return_value=False), patch(
            "cds_pipeline.extractor.codex_available", return_value=True
        ), patch.dict("os.environ", {}, clear=True):
            providers = [name for name, _ in extractor_chain("auto")]
        self.assertEqual(providers, ["codex"])

    def test_codex_output_schema_is_strict_at_every_object(self) -> None:
        schema = _strict_codex_schema(RescueDecision.model_json_schema())

        def assert_strict(node):
            if isinstance(node, dict):
                if "properties" in node:
                    self.assertFalse(node["additionalProperties"])
                    self.assertEqual(set(node["required"]), set(node["properties"]))
                for value in node.values():
                    assert_strict(value)
            elif isinstance(node, list):
                for value in node:
                    assert_strict(value)

        assert_strict(schema)

    def test_codex_rescue_is_read_only_secret_free_and_schema_constrained(self) -> None:
        captured: dict[str, object] = {}

        def fake_run(command, **kwargs):
            captured["command"] = command
            captured["environment"] = kwargs["env"]
            output_path = Path(command[command.index("--output-last-message") + 1])
            output_path.write_text(
                json.dumps(
                    {
                        "category": "source_discovery",
                        "diagnosis": "The normal crawler did not find the official archive.",
                        "retry_recommended": True,
                        "archive_url": "https://example.edu/institutional-research/cds",
                        "sources": [
                            {
                                "url": "https://example.edu/cds/CDS_2024-2025.pdf",
                                "label": "Common Data Set 2024-2025",
                                "academic_year": "2024-2025",
                                "discovery_url": "https://example.edu/institutional-research/cds",
                            }
                        ],
                        "operator_message": "Retry with the located official archive.",
                    }
                ),
                encoding="utf-8",
            )
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        with tempfile.TemporaryDirectory() as tmp, patch(
            "cds_pipeline.rescue.codex_available", return_value=True
        ), patch("cds_pipeline.rescue._codex_binary", return_value="codex"), patch(
            "cds_pipeline.rescue.subprocess.run", side_effect=fake_run
        ), patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "should-not-pass",
                "CODEX_API_KEY": "also-remove",
                "DATABASE_URL": "must-not-pass",
            },
        ):
            root = Path(tmp)
            decision = run_codex_rescue(
                school_name="Example College",
                school_slug="examplecollege",
                target="Example College",
                stage="add_school",
                error=RuntimeError("no PDFs found"),
                workspace_dir=root / "workspace",
                repository_root=root,
            )

            self.assertTrue((root / "workspace" / "examplecollege" / "codex_rescue.json").exists())

        command = captured["command"]
        self.assertIn("--search", command)
        self.assertIn("read-only", command)
        self.assertIn("never", command)
        self.assertIn("--output-schema", command)
        self.assertNotIn("OPENAI_API_KEY", captured["environment"])
        self.assertNotIn("CODEX_API_KEY", captured["environment"])
        self.assertNotIn("DATABASE_URL", captured["environment"])
        candidates = recovery_sources(decision)
        self.assertEqual(candidates[0].academic_year, "2024-2025")
        self.assertFalse(candidates[0].official)

    def test_codex_rescue_rejects_local_urls(self) -> None:
        decision = RescueDecision(
            category="source_discovery",
            diagnosis="A local URL was suggested.",
            retry_recommended=True,
            sources=[
                {
                    "url": "http://127.0.0.1/private.pdf",
                    "label": "CDS 2024-2025",
                    "academic_year": "2024-2025",
                }
            ],
            operator_message="Do not use it.",
        )
        self.assertEqual(recovery_sources(decision), [])

    def test_add_command_uses_only_one_codex_recovery_retry(self) -> None:
        args = build_parser().parse_args(
            ["add", "Example College", "--extractor", "auto"]
        )
        decision = RescueDecision(
            category="source_discovery",
            diagnosis="The crawler missed the archive.",
            retry_recommended=True,
            archive_url="https://example.edu/cds",
            sources=[],
            operator_message="Retry the official archive once.",
        )
        first_failure = _PipelineRunFailure(
            "add_school", RuntimeError("No verified PDFs were downloaded.")
        )
        second_failure = _PipelineRunFailure(
            "publication", RuntimeError("No complete years can be published.")
        )
        with patch(
            "cds_pipeline.cli._run_add_once",
            side_effect=[first_failure, second_failure],
        ) as run_once, patch(
            "cds_pipeline.cli.run_codex_rescue", return_value=decision
        ) as rescue:
            with self.assertRaisesRegex(RuntimeError, "one recovery retry"):
                _cmd_add(args)
        self.assertEqual(run_once.call_count, 2)
        self.assertEqual(rescue.call_count, 1)

    def test_compiler_derives_rates_and_requires_evidence(self) -> None:
        values = {
            "admissions.applied": 1000,
            "admissions.admitted": 250,
            "admissions.enrolled": 100,
            "demographics.enrollment.undergraduate": 2000,
            "demographics.enrollment.total": 2100,
            "demographics.byRace.international": 200,
            "demographics.byRace.hispanicLatino": 300,
            "demographics.byRace.blackAfricanAmerican": 200,
            "demographics.byRace.white": 600,
            "demographics.byRace.asian": 500,
            "demographics.byRace.americanIndianAlaskaNative": 10,
            "demographics.byRace.nativeHawaiianPacificIslander": 10,
            "demographics.byRace.twoOrMoreRaces": 150,
            "demographics.byRace.unknown": 30,
            "costs.tuition": 60000,
            "costs.fees": 1000,
            "costs.roomAndBoard": 18000,
        }
        self.assertEqual(set(values), set(PUBLISH_REQUIRED_PATHS))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            extraction_path = root / "extractions" / "2024-2025" / "all.json"
            extraction_path.parent.mkdir(parents=True)
            observations = [
                {
                    "path": path,
                    "value": value,
                    "confidence": 0.99,
                    "evidence": [
                        {
                            "document_id": "sha256:sample",
                            "page": 1,
                            "quote": f"{path} {value}",
                        }
                    ],
                }
                for path, value in values.items()
            ]
            extraction_path.write_text(
                json.dumps({"observations": observations}), encoding="utf-8"
            )
            manifest_path = root / "school_manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "school_name": "Sample University",
                        "school_slug": "sample",
                        "workspace": str(root),
                        "documents": [
                            {
                                "document_id": "sha256:sample",
                                "source_path": str(root / "sample.pdf"),
                                "filename": "sample.pdf",
                                "sha256": "0" * 64,
                                "size_bytes": 1,
                                "page_count": 1,
                                "school_name": "Sample University",
                                "school_slug": "sample",
                                "academic_year": "2024-2025",
                                "document_type": "cds",
                                "pages": [
                                    {
                                        "page": 1,
                                        "width": 612,
                                        "height": 792,
                                        "text": "\n".join(
                                            f"{path} {value}" for path, value in values.items()
                                        ),
                                    }
                                ],
                            }
                        ],
                        "extraction_paths": [str(extraction_path)],
                    }
                ),
                encoding="utf-8",
            )
            report = compile_school(str(manifest_path))
            compiled = json.loads(Path(report["compiled_path"]).read_text(encoding="utf-8"))
            year = compiled["years"]["2024-2025"]
            self.assertEqual(report["error_count"], 0)
            self.assertEqual(year["admissions"]["acceptanceRate"], 0.25)
            self.assertEqual(year["admissions"]["yield"], 0.4)
            self.assertEqual(year["costs"]["totalCOA"], 79000)

            incomplete_path = root / "extractions" / "2023-2024" / "admissions.json"
            incomplete_path.parent.mkdir(parents=True)
            incomplete_path.write_text(
                json.dumps(
                    {
                        "observations": [
                            {
                                "path": "admissions.applied",
                                "value": 900,
                                "confidence": 1,
                                "evidence": [
                                    {
                                        "document_id": "sha256:incomplete",
                                        "page": 1,
                                        "quote": "Applicants 900",
                                    }
                                ],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_payload["documents"].append(
                {
                    "document_id": "sha256:incomplete",
                    "source_path": str(root / "incomplete.pdf"),
                    "filename": "incomplete.pdf",
                    "sha256": "1" * 64,
                    "size_bytes": 1,
                    "page_count": 1,
                    "school_name": "Sample University",
                    "school_slug": "sample",
                    "academic_year": "2023-2024",
                    "year_verified": True,
                    "school_match_score": 1,
                    "document_type": "cds",
                    "pages": [
                        {
                            "page": 1,
                            "width": 612,
                            "height": 792,
                            "text": "Applicants 900",
                        }
                    ],
                }
            )
            manifest_payload["extraction_paths"].append(str(incomplete_path))
            manifest_path.write_text(json.dumps(manifest_payload), encoding="utf-8")
            partial_report = compile_school(str(manifest_path))
            self.assertEqual(partial_report["error_count"], 0)
            self.assertEqual(partial_report["compiled_years"], ["2023-2024", "2024-2025"])
            self.assertEqual(partial_report["partial_years"]["2023-2024"], list(values)[1:])
            compiled = json.loads(Path(partial_report["compiled_path"]).read_text(encoding="utf-8"))
            self.assertEqual(compiled["years"]["2023-2024"]["admissions"]["applied"], 900)

            observations[0]["evidence"][0]["page"] = 999
            extraction_path.write_text(
                json.dumps({"observations": observations}), encoding="utf-8"
            )
            invalid_report = compile_school(str(manifest_path))
            self.assertEqual(invalid_report["error_count"], 0)
            self.assertIn(
                "invalid_source_evidence",
                {issue["kind"] for issue in invalid_report["issues"]},
            )
            invalid_compiled = json.loads(
                Path(invalid_report["compiled_path"]).read_text(encoding="utf-8")
            )
            self.assertNotIn("applied", invalid_compiled["years"]["2024-2025"]["admissions"])

    def test_validator_rejects_string_metrics_and_slug_traversal(self) -> None:
        result = validate_section_extraction(
            {
                "observations": [
                    {
                        "path": "admissions.applied",
                        "value": "not-a-number",
                        "confidence": 0.99,
                        "evidence": [
                            {"document_id": "sha256:x", "page": 1, "quote": "not-a-number"}
                        ],
                    }
                ]
            }
        )
        self.assertIn("invalid_metric_type", {issue["kind"] for issue in result["issues"]})
        with self.assertRaises(ValueError):
            validate_slug("../../escape")

    def test_registry_generator_preserves_non_school_imports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            (data_dir / "alpha.json").write_text(
                json.dumps({"name": "Alpha University", "slug": "alpha", "years": {}}),
                encoding="utf-8",
            )
            (data_dir / "beta.json").write_text(
                json.dumps({"name": "Beta College", "slug": "beta", "years": {}}),
                encoding="utf-8",
            )
            (data_dir / "index.ts").write_text(
                'import { SchoolData } from "@/lib/types";\n'
                'import { getLatestYear } from "@/utils/dataHelpers";\n\n'
                'import alphaData from "./alpha.json";\n\n'
                "export interface SearchableSchool { name: string }\n\n"
                "export const allSchools: SchoolData[] = [\n"
                "  alphaData as SchoolData,\n"
                "];\n\n"
                "export const latest = getLatestYear(allSchools[0]);\n",
                encoding="utf-8",
            )
            result = generate_registry(data_dir=data_dir)
            generated = (data_dir / "index.ts").read_text(encoding="utf-8")
            self.assertTrue(result["changed"])
            self.assertIn('getLatestYear } from "@/utils/dataHelpers"', generated)
            self.assertIn('import betaData from "./beta.json";', generated)
            self.assertIn("betaData as SchoolData", generated)

    def _make_pdf(self, path: Path, pages: list[str], *, pad: bool = False) -> None:
        pdf = self.fitz.open()
        try:
            for text in pages:
                page = pdf.new_page()
                if pad:
                    text += "\n" + ("Supporting Common Data Set context. " * 8)
                page.insert_textbox(self.fitz.Rect(72, 72, 540, 720), text, fontsize=11)
            pdf.save(path)
        finally:
            pdf.close()

    def _sample_packet(self) -> SectionPacket:
        return SectionPacket(
            school_name="Sample University",
            school_slug="sample",
            academic_year="2024-2025",
            domain="admissions",
            metric_paths=["admissions.applied"],
            pages=[
                PacketPage(
                    document_id="sha256:sample",
                    source_path="sample.pdf",
                    page=3,
                    text="C1. Applicants 1,000; admitted 250; enrolled 100.",
                    question_ids=["C1"],
                )
            ],
        )


if __name__ == "__main__":
    unittest.main()
