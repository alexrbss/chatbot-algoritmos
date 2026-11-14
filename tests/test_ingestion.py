from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from services.ingestion import (
    IngestionError,
    analyze_pdf,
    build_material_markdown,
    clean_title,
    find_duplicate,
    load_manifest,
    material_filename,
    save_material,
    slugify,
)


class FakePage:
    def __init__(self, text: str) -> None:
        self.text = text

    def extract_text(self) -> str:
        return self.text


class FakeReader:
    is_encrypted = False

    def __init__(self) -> None:
        self.pages = [
            FakePage("Estruturas condicionais\n\nUse se e senao para tomar decisões."),
            FakePage("Exemplo\n\nLeia uma idade e verifique se ela é maior de idade."),
        ]


class IngestionTests(unittest.TestCase):
    def test_slug_and_material_filename_are_predictable(self) -> None:
        self.assertEqual(slugify("Repetição e Condição!"), "repeticao_e_condicao")
        self.assertEqual(
            material_filename("Estruturas Condicionais", 4),
            "ma04_estruturas_condicionais.md",
        )
        self.assertEqual(clean_title("  Estruturas\n condicionais  "), "Estruturas condicionais")

    @patch("services.ingestion.PdfReader", return_value=FakeReader())
    def test_pdf_is_extracted_and_split_by_page(self, _reader) -> None:
        analysis = analyze_pdf(b"%PDF-1.7 fake content", "ma04.pdf")
        self.assertEqual(analysis.page_count, 2)
        self.assertEqual(analysis.nonempty_page_count, 2)
        self.assertGreater(analysis.character_count, 80)
        markdown = build_material_markdown(analysis, "Estruturas condicionais")
        self.assertIn("## Página 1", markdown)
        self.assertIn("## Página 2", markdown)

    @patch("services.ingestion.PdfReader", return_value=FakeReader())
    def test_save_registers_hash_and_blocks_duplicate(self, _reader) -> None:
        analysis = analyze_pdf(b"%PDF-1.7 fake content", "ma04.pdf")
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            materials = root / "materiais"
            manifest_path = root / "materials_manifest.json"
            record = save_material(
                analysis,
                "Estruturas condicionais",
                materials,
                manifest_path,
                material_number=4,
            )

            self.assertTrue((materials / "ma04_estruturas_condicionais.md").exists())
            manifest = load_manifest(manifest_path)
            self.assertEqual(find_duplicate(manifest, analysis.sha256), record)
            with self.assertRaisesRegex(IngestionError, "já foi incorporado"):
                save_material(analysis, "Outro título", materials, manifest_path)

    def test_invalid_signature_is_rejected(self) -> None:
        with self.assertRaisesRegex(IngestionError, "assinatura PDF"):
            analyze_pdf(b"not a pdf", "material.pdf")


if __name__ == "__main__":
    unittest.main()
