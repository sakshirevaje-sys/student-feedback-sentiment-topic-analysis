import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from nlp_engine import analyze_feedback, evaluate_results, load_feedback_csv


class TestStudentFeedbackNLP(unittest.TestCase):
    def test_spelling_correction_and_topic(self):
        result = analyze_feedback("The libary has good books.")
        self.assertIn("library", result["topics"])
        self.assertIn("library", result["normalized_feedback"])

    def test_multiple_topics(self):
        result = analyze_feedback("The teacher is helpful, but the exam paper is confusing.")
        self.assertIn("teaching", result["topics"])
        self.assertIn("examinations", result["topics"])
        self.assertEqual(result["sentiment"], "mixed")

    def test_negation(self):
        result = analyze_feedback("The teacher is not helpful.")
        self.assertEqual(result["sentiment"], "negative")

    def test_neutral(self):
        result = analyze_feedback("The library opens at 9 AM on weekdays.")
        self.assertEqual(result["sentiment"], "neutral")

    def test_sample_dataset_loads(self):
        rows = load_feedback_csv(PROJECT_ROOT / "data" / "sample_feedback.csv")
        self.assertEqual(len(rows), 30)
        metrics = evaluate_results(rows)
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics["records"], 30)


if __name__ == "__main__":
    unittest.main(verbosity=2)
