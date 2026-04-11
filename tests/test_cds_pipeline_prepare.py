from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from cds_pipeline.contracts import build_year_subagent_prompt
from cds_pipeline.prepare import prepare_documents
from cds_pipeline.validator import validate_school_data, validate_year_submission


class PreparePipelineTests(unittest.TestCase):
    def test_prepare_documents_renders_grouped_year_manifests(self) -> None:
        try:
            import fitz  # type: ignore
        except Exception as exc:  # pragma: no cover - dependency guard
            self.skipTest(f"PyMuPDF unavailable: {exc}")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf_2024 = root / "sample-2024.pdf"
            pdf_2025 = root / "sample-2025.pdf"
            self._make_pdf(fitz, pdf_2024, pages=2)
            self._make_pdf(fitz, pdf_2025, pages=3)

            result = prepare_documents(
                [
                    {"pdf_path": str(pdf_2024), "school_slug": "sample", "year": "2024-2025"},
                    {"pdf_path": str(pdf_2025), "school_slug": "sample", "year": "2025-2026"},
                ],
                workspace_dir=root / "workspace",
            )

            self.assertEqual(result["school_slug"], "sample")
            self.assertEqual(len(result["years"]), 2)

            manifest_2024 = Path(result["years"][0]["manifest_path"])
            payload_2024 = json.loads(manifest_2024.read_text(encoding="utf-8"))
            self.assertEqual(payload_2024["page_count"], 2)
            self.assertEqual(len(payload_2024["screenshot_paths"]), 2)
            self.assertEqual(payload_2024["year"], "2024-2025")

            manifest_2025 = Path(result["years"][1]["manifest_path"])
            payload_2025 = json.loads(manifest_2025.read_text(encoding="utf-8"))
            self.assertEqual(payload_2025["page_count"], 3)
            self.assertTrue(all(Path(path).exists() for path in payload_2025["screenshot_paths"]))

    def test_build_year_subagent_prompt_mentions_contract(self) -> None:
        prompt = build_year_subagent_prompt(school_name="Sample University", year="2024-2025")
        self.assertIn("YearData", prompt)
        self.assertIn('"year", "data", and "notes"', prompt)

    def test_validate_year_submission_flags_consistency_mismatches(self) -> None:
        validation = validate_year_submission(
            {
                "year": "2024-2025",
                "data": {
                    "admissions": {
                        "applied": 100,
                        "admitted": 50,
                        "enrolled": 25,
                        "acceptanceRate": 0.7,
                        "yield": 0.5,
                    },
                    "testScores": {},
                    "demographics": {
                        "enrollment": {"undergraduate": 100, "graduate": 20, "total": 120},
                        "byRace": {
                            "international": 10,
                            "hispanicLatino": 10,
                            "blackAfricanAmerican": 10,
                            "white": 10,
                            "asian": 10,
                            "americanIndianAlaskaNative": 10,
                            "nativeHawaiianPacificIslander": 10,
                            "twoOrMoreRaces": 10,
                            "unknown": 10,
                        },
                        "byResidency": {"inState": 30, "outOfState": 30, "international": 30},
                    },
                    "costs": {"tuition": 10000, "fees": 1000, "roomAndBoard": 5000, "totalCOA": 15000},
                    "financialAid": {},
                },
                "notes": [],
            }
        )
        self.assertGreaterEqual(validation["issue_count"], 2)

    def test_validate_school_data_summarizes_years(self) -> None:
        validation = validate_school_data(
            {
                "name": "Sample University",
                "slug": "sample",
                "years": {
                    "2024-2025": {
                        "admissions": {
                            "applied": 100,
                            "admitted": 50,
                            "enrolled": 25,
                            "acceptanceRate": 0.5,
                            "yield": 0.5,
                        },
                        "testScores": {},
                        "demographics": {
                            "enrollment": {"undergraduate": 100, "graduate": 20, "total": 120},
                            "byRace": {
                                "international": 10,
                                "hispanicLatino": 10,
                                "blackAfricanAmerican": 10,
                                "white": 10,
                                "asian": 10,
                                "americanIndianAlaskaNative": 10,
                                "nativeHawaiianPacificIslander": 10,
                                "twoOrMoreRaces": 10,
                                "unknown": 20,
                            },
                            "byResidency": {"inState": 30, "outOfState": 40, "international": 30},
                        },
                        "costs": {"tuition": 10000, "fees": 1000, "roomAndBoard": 5000, "totalCOA": 16000},
                        "financialAid": {},
                    }
                },
            }
        )
        self.assertEqual(validation["school_slug"], "sample")
        self.assertEqual(len(validation["years"]), 1)

    @staticmethod
    def _make_pdf(fitz: object, path: Path, *, pages: int) -> None:
        pdf = fitz.open()
        try:
            for index in range(pages):
                page = pdf.new_page()
                page.insert_text((72, 72), f"Sample page {index + 1}")
            pdf.save(path)
        finally:
            pdf.close()


if __name__ == "__main__":
    unittest.main()
