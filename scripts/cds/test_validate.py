import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import Report, check_values


class NumericValidationTests(unittest.TestCase):
    def test_accepts_reported_fractional_score_percentiles(self):
        report = Report()
        check_values("2020-2021", {"testScores": {"sat": {"math": {"p25": 610, "p75": 702.5}}}}, report)
        self.assertEqual(report.errors, [])

    def test_rejects_fractional_student_counts(self):
        report = Report()
        check_values("2020-2021", {"admissions": {"applied": 100.5}}, report)
        self.assertEqual(report.errors, ["2020-2021: admissions.applied=100.5 should be a whole number"])


if __name__ == "__main__":
    unittest.main()
