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
        self.assertGreaterEqual(len(chunks), 9)
        self.assertTrue(all(chunk.title and chunk.source for chunk in chunks))

    def test_while_query_retrieves_repetition_material(self) -> None:
        results = self.retriever.search("while infinito atualização do contador", top_k=1)
        self.assertEqual(results[0].chunk.source, "02_decisao_repeticao.md")
        self.assertEqual(results[0].chunk.title, "Laço while")

    def test_linear_search_query_retrieves_search_section(self) -> None:
        results = self.retriever.search("busca linear complexidade pior caso", top_k=1)
        self.assertEqual(results[0].chunk.source, "03_vetores_busca.md")
        self.assertEqual(results[0].chunk.title, "Busca linear")

    def test_empty_query_returns_no_results(self) -> None:
        self.assertEqual(self.retriever.search("   "), [])


if __name__ == "__main__":
    unittest.main()

