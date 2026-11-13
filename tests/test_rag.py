from pathlib import Path
import unittest

from services.rag import BM25Retriever, load_materials


ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT / "data" / "materiais"


class RagTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.retriever = BM25Retriever.from_directory(MATERIALS)

    def test_materials_are_split_by_section(self) -> None:
        chunks = load_materials(MATERIALS)
        self.assertGreaterEqual(len(chunks), 12)
        self.assertTrue(all(chunk.title and chunk.source for chunk in chunks))

    def test_portugol_structure_query_retrieves_second_material(self) -> None:
        results = self.retriever.search("algoritmo var inicio fimalgoritmo", top_k=1)
        self.assertEqual(results[0].chunk.source, "ma02_portugol.md")
        self.assertEqual(results[0].chunk.title, "Estrutura de um algoritmo em Portugol")

    def test_input_output_query_retrieves_third_material(self) -> None:
        results = self.retriever.search("comandos leia escreva entrada saída", top_k=1)
        self.assertEqual(results[0].chunk.source, "ma03_sequencial.md")

    def test_empty_query_returns_no_results(self) -> None:
        self.assertEqual(self.retriever.search("   "), [])


if __name__ == "__main__":
    unittest.main()
