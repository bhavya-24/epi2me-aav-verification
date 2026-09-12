"""Test evidence grading; these do not substitute for actual upstream execution."""
from pathlib import Path
import tempfile
import unittest
from run_component import assess, parse_output


class EvidenceAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.output = Path(self.tmp.name) / "output.tsv"

    def output_text(self, rows):
        self.output.write_text("Reference\tNumber of alignments\tPercentage of alignments\tsample_id\n" + rows, encoding="utf-8")

    def test_nonzero_exit_without_expected_diagnostic_fails(self):
        spec = {"error_contains": "Usecols do not match columns"}
        self.assertEqual(assess(spec, {"exit_code": 1, "stderr": "ImportError"}, self.output)[0], "FAIL")

    def test_failed_case_with_output_is_not_passed(self):
        self.output.write_text("unexpected partial output")
        self.assertEqual(assess({"error_contains": "missing"}, {"exit_code": 1, "stderr": "missing"}, self.output)[0], "FAIL")

    def test_missing_output_cannot_pass_successful_exit(self):
        self.assertEqual(assess({"expected": {}}, {"exit_code": 0}, self.output)[0], "FAIL")

    def test_wrong_percentage_and_sample_are_detected(self):
        spec = {"expected": {"Mapped": [95, 95]}}
        for rows in ("Mapped\t95\t96\tSYNTHETIC_A\n", "Mapped\t95\t95\tWRONG_SAMPLE\n"):
            with self.subTest(rows=rows):
                self.output_text(rows)
                self.assertEqual(assess(spec, {"exit_code": 0}, self.output)[0], "FAIL")

    def test_duplicate_output_category_rejected(self):
        self.output_text("Mapped\t95\t95\tSYNTHETIC_A\n" * 2)
        with self.assertRaises(ValueError):
            parse_output(self.output)

    def test_nonfinite_output_rejected(self):
        self.output_text("Mapped\t95\tNaN\tSYNTHETIC_A\n")
        with self.assertRaises(ValueError):
            parse_output(self.output)

    def test_exploration_does_not_become_pass(self):
        self.assertEqual(assess({"explore": "Inspect zero reads"}, {"exit_code": 1}, self.output)[0], "OBSERVATION")

    def test_timeout_is_blocked_even_for_exploration(self):
        self.assertEqual(assess({"explore": "Inspect zero reads"}, {"execution_error": "timeout"}, self.output)[0], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
