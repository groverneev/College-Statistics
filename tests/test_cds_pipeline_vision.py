from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from cds_pipeline import openai_client
from cds_pipeline.extractors.vision_llm import _expand_hint_pages
from cds_pipeline.normalizer import normalize_document
from cds_pipeline.review import build_review_payload


class VisionNormalizerTests(unittest.TestCase):
    def test_normalizer_prefers_vision_candidates(self) -> None:
        raw_payload = {
            "vision_field_candidates": [
                {
                    "field": "admissions.applied",
                    "value": "12345",
                    "confidence": 0.96,
                    "evidence_label": "Applicants",
                    "page": 7,
                    "section": "C1",
                },
                {
                    "field": "costs.tuition",
                    "value": "$55,100",
                    "confidence": 0.91,
                    "evidence_label": "Tuition",
                    "page": 20,
                    "section": "G1",
                },
            ]
        }
        data, field_meta = normalize_document(raw_payload, {"school_slug": "test"})
        self.assertEqual(data["admissions"]["applied"], 12345)
        self.assertEqual(data["costs"]["tuition"], 55100)
        self.assertEqual(field_meta["admissions.applied"]["source"], "vision_llm")
        self.assertEqual(field_meta["admissions.applied"]["source_ref"], "C1 p.7: Applicants")

    def test_normalizer_derives_residency_from_vision_percentage(self) -> None:
        raw_payload = {
            "vision_field_candidates": [
                {
                    "field": "demographics.enrollment.undergraduate",
                    "value": "1000",
                    "confidence": 0.95,
                    "evidence_label": "Undergraduate total",
                    "page": 3,
                    "section": "B1",
                },
                {
                    "field": "demographics.byRace.international",
                    "value": "100",
                    "confidence": 0.92,
                    "evidence_label": "Nonresident aliens",
                    "page": 4,
                    "section": "B2",
                },
                {
                    "field": "computed.demographics.outOfStatePercent",
                    "value": "40%",
                    "confidence": 0.88,
                    "evidence_label": "Percent from out of state",
                    "page": 10,
                    "section": "F1",
                },
            ]
        }
        data, field_meta = normalize_document(raw_payload, {"school_slug": "test"})
        self.assertEqual(data["demographics"]["byResidency"]["outOfState"], 360)
        self.assertEqual(data["demographics"]["byResidency"]["inState"], 540)
        self.assertEqual(field_meta["demographics.byResidency.outOfState"]["status"], "derived")
        self.assertNotIn("computed", data)

    def test_review_payload_carries_vision_summary(self) -> None:
        review = build_review_payload(
            {
                "school_slug": "sample",
                "school_name": "Sample",
                "documents": [
                    {
                        "year": "2024-2025",
                        "source_path": "sample.pdf",
                        "classification": {"document_type": "scanned"},
                        "extractors_used": ["VisionLLMExtractor"],
                        "raw_payload_summary": {
                            "vision_sections": {"C1": {"pages": [7], "confidence": 0.95}},
                            "vision_missing_sections": ["H2"],
                            "vision_notes": ["Missing totals on one page."],
                            "vision_rendered_page_count": 32,
                        },
                        "validation": {"issue_count": 0, "issues": [], "low_confidence_fields": []},
                    }
                ],
            }
        )
        document = review["documents"][0]
        self.assertEqual(document["vision_rendered_page_count"], 32)
        self.assertEqual(document["vision_missing_sections"], ["H2"])
        self.assertEqual(document["vision_sections"]["C1"]["pages"], [7])


class VisionHelperTests(unittest.TestCase):
    def test_expand_hint_pages(self) -> None:
        self.assertEqual(_expand_hint_pages([3, 5], 10), [3, 4, 5])
        self.assertEqual(_expand_hint_pages(4, 10), [4])
        self.assertEqual(_expand_hint_pages([2, 4, 12], 10), [2, 4])

    def test_load_local_env_reads_dotenv_local(self) -> None:
        env_path = Path(openai_client.__file__).resolve().parent.parent / ".env.local"
        original = env_path.read_text(encoding="utf-8") if env_path.exists() else None
        try:
            env_path.write_text("OPENAI_API_KEY=test-from-env-local\nOPENAI_MODEL=test-model\n", encoding="utf-8")
            with patch.dict("os.environ", {}, clear=True):
                openai_client._ENV_LOADED = False
                openai_client._load_local_env()
                import os

                self.assertEqual(os.getenv("OPENAI_API_KEY"), "test-from-env-local")
                self.assertEqual(os.getenv("OPENAI_MODEL"), "test-model")
        finally:
            openai_client._ENV_LOADED = False
            if original is None:
                env_path.unlink(missing_ok=True)
            else:
                env_path.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
