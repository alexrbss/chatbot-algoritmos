from pathlib import Path
import unittest

from services.feedback import analyze_submission, load_exercises
from services.rag import BM25Retriever


ROOT = Path(__file__).resolve().parents[1]


class FeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.exercises = load_exercises(ROOT / "data" / "exercicios.json")
        cls.retriever = BM25Retriever.from_directory(ROOT / "data" / "materiais")

    def test_invalid_python_is_reported(self) -> None:
        exercise = self.exercises[1]
        results = self.retriever.search(exercise["reference_query"])
        report = analyze_submission(exercise, "if numero > 0 print('positivo')", results)
        self.assertFalse(report.syntax_ok)
        self.assertIn("sintaxe", report.next_step.lower())

    def test_complete_while_attempt_meets_rubric(self) -> None:
        exercise = next(item for item in self.exercises if item["id"] == "contagem-while")
        submission = """n = int(input())
contador = 1
while contador <= n:
    print(contador)
    contador += 1
"""
        results = self.retriever.search(exercise["reference_query"])
        report = analyze_submission(exercise, submission, results)
        self.assertTrue(report.syntax_ok)
        self.assertEqual(report.progress, 1.0)
        self.assertEqual(report.improvements, [])

    def test_partial_average_attempt_does_not_overclaim_progress(self) -> None:
        exercise = next(item for item in self.exercises if item["id"] == "media-tres-notas")
        submission = "nota1 = float(input())\nprint(nota1)"
        results = self.retriever.search(exercise["reference_query"])
        report = analyze_submission(exercise, submission, results)
        self.assertEqual(report.progress, 0.0)
        self.assertEqual(report.strengths, [])

    def test_exercise_catalog_has_five_items(self) -> None:
        self.assertEqual(len(self.exercises), 5)
        self.assertEqual(len({item["id"] for item in self.exercises}), 5)


if __name__ == "__main__":
    unittest.main()

