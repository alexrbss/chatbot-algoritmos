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

    def test_incomplete_portugol_structure_is_reported(self) -> None:
        exercise = self.exercises[0]
        results = self.retriever.search(exercise["reference_query"])
        report = analyze_submission(exercise, 'algoritmo "oi"\ninicio\nescreva("Oi")', results)
        self.assertFalse(report.syntax_ok)
        self.assertIn("incompleta", report.syntax_message.lower())

    def test_complete_score_attempt_meets_rubric(self) -> None:
        exercise = next(item for item in self.exercises if item["id"] == "pontuacao-total")
        submission = """algoritmo "pontuacao"
var
    primeira, segunda, total: inteiro
inicio
    leia(primeira)
    leia(segunda)
    total <- primeira + segunda
    escreva(total)
fimalgoritmo
"""
        results = self.retriever.search(exercise["reference_query"])
        report = analyze_submission(exercise, submission, results)
        self.assertTrue(report.syntax_ok)
        self.assertEqual(report.progress, 1.0)
        self.assertEqual(report.improvements, [])

    def test_compact_weighted_average_expression_is_detected(self) -> None:
        exercise = next(item for item in self.exercises if item["id"] == "media-ponderada")
        submission = """algoritmo "media"
var
    n1, n2, n3, media: real
inicio
    leia(n1)
    leia(n2)
    leia(n3)
    media<-(n1*2+n2*3+n3*5)/10
    escreva(media)
fimalgoritmo
"""
        results = self.retriever.search(exercise["reference_query"])
        report = analyze_submission(exercise, submission, results)
        self.assertEqual(report.progress, 1.0)

    def test_catalog_contains_the_twenty_list_questions(self) -> None:
        self.assertEqual(len(self.exercises), 20)
        self.assertEqual([item["number"] for item in self.exercises], list(range(1, 21)))
        self.assertTrue(all(item["answer_type"] == "portugol" for item in self.exercises))
        self.assertIn("mensagem de recepção", self.exercises[0]["statement"])
        self.assertIn("dividirá igualmente", self.exercises[-1]["statement"])


if __name__ == "__main__":
    unittest.main()
