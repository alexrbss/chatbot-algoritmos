"""Pipeline local e auditável para incorporar materiais em PDF ao RAG."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from services.rag import DocumentChunk


MAX_PDF_BYTES = 15 * 1024 * 1024
MAX_PDF_PAGES = 120
MIN_EXTRACTED_CHARACTERS = 80
MANIFEST_VERSION = 1


class IngestionError(ValueError):
    """Erro esperado e apresentável ao usuário durante a ingestão."""


@dataclass(frozen=True)
class ExtractedPage:
    number: int
    text: str


@dataclass(frozen=True)
class PdfAnalysis:
    source_filename: str
    sha256: str
    file_size: int
    page_count: int
    pages: tuple[ExtractedPage, ...]
    warnings: tuple[str, ...]

    @property
    def character_count(self) -> int:
        return sum(len(page.text) for page in self.pages)

    @property
    def nonempty_page_count(self) -> int:
        return sum(bool(page.text.strip()) for page in self.pages)


def clean_extracted_text(text: str) -> str:
    """Remove ruído de espaçamento sem reescrever o conteúdo do professor."""

    normalized = unicodedata.normalize("NFKC", text).replace("\u00a0", " ")
    lines = []
    previous_blank = False
    for raw_line in normalized.splitlines():
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if not line:
            if lines and not previous_blank:
                lines.append("")
            previous_blank = True
            continue
        lines.append(line)
        previous_blank = False
    return "\n".join(lines).strip()


def slugify(value: str) -> str:
    """Gera nomes de arquivo previsíveis e seguros."""

    normalized = unicodedata.normalize("NFKD", value.lower())
    ascii_value = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_value).strip("_")
    return slug[:72] or "material"


def clean_title(value: str) -> str:
    """Restringe o título a uma linha curta para Markdown e histórico."""

    title = re.sub(r"\s+", " ", value).strip()
    if not title:
        raise IngestionError("Informe um título para o material.")
    if len(title) > 120:
        raise IngestionError("O título deve ter no máximo 120 caracteres.")
    return title


def analyze_pdf(content: bytes, source_filename: str) -> PdfAnalysis:
    """Valida e extrai o texto de um PDF mantido somente em memória."""

    if not content:
        raise IngestionError("O arquivo enviado está vazio.")
    if len(content) > MAX_PDF_BYTES:
        raise IngestionError("O PDF ultrapassa o limite de 15 MB deste MVP.")
    if not content.startswith(b"%PDF-"):
        raise IngestionError("O arquivo não possui uma assinatura PDF válida.")

    try:
        reader = PdfReader(BytesIO(content))
        if reader.is_encrypted and reader.decrypt("") == 0:
            raise IngestionError("O PDF está protegido por senha.")
    except IngestionError:
        raise
    except Exception as error:
        raise IngestionError("Não foi possível abrir o PDF. Verifique se ele está íntegro.") from error

    page_count = len(reader.pages)
    if not page_count:
        raise IngestionError("O PDF não possui páginas.")
    if page_count > MAX_PDF_PAGES:
        raise IngestionError(
            f"O PDF possui {page_count} páginas; o limite deste MVP é {MAX_PDF_PAGES}."
        )

    pages: list[ExtractedPage] = []
    failed_pages: list[int] = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = clean_extracted_text(page.extract_text() or "")
        except Exception:
            text = ""
            failed_pages.append(page_number)
        pages.append(ExtractedPage(number=page_number, text=text))

    character_count = sum(len(page.text) for page in pages)
    if character_count < MIN_EXTRACTED_CHARACTERS:
        raise IngestionError(
            "Foi extraído pouco texto. O PDF pode ser composto por imagens e precisar de OCR."
        )

    warnings: list[str] = []
    empty_pages = [page.number for page in pages if not page.text]
    if empty_pages:
        warnings.append(
            f"{len(empty_pages)} página(s) não produziram texto: "
            + ", ".join(map(str, empty_pages[:8]))
            + ("…" if len(empty_pages) > 8 else "")
        )
    if failed_pages:
        warnings.append(
            "A extração apresentou erro nas páginas: "
            + ", ".join(map(str, failed_pages[:8]))
            + ("…" if len(failed_pages) > 8 else "")
        )

    return PdfAnalysis(
        source_filename=Path(source_filename).name,
        sha256=hashlib.sha256(content).hexdigest(),
        file_size=len(content),
        page_count=page_count,
        pages=tuple(pages),
        warnings=tuple(warnings),
    )


def build_material_markdown(analysis: PdfAnalysis, title: str) -> str:
    """Converte a extração aprovada em Markdown rastreável por página."""

    normalized_title = clean_title(title)

    sections = [
        f"# {normalized_title}",
        "",
        f"> Texto extraído de `{analysis.source_filename}` e aprovado antes da indexação.",
    ]
    for page in analysis.pages:
        if not page.text:
            continue
        sections.extend(["", f"## Página {page.number}", "", page.text])
    return "\n".join(sections).strip() + "\n"


def build_preview_chunks(analysis: PdfAnalysis, title: str) -> list[DocumentChunk]:
    """Cria trechos temporários para testar a recuperação antes de salvar."""

    normalized_title = clean_title(title)
    material_slug = slugify(normalized_title)
    return [
        DocumentChunk(
            id=f"preview-{material_slug}-{page.number}",
            title=f"{normalized_title} · Página {page.number}",
            source=analysis.source_filename,
            content=page.text,
        )
        for page in analysis.pages
        if page.text
    ]


def load_manifest(path: Path) -> dict[str, Any]:
    """Lê o histórico; um arquivo ausente representa uma base ainda sem importações."""

    if not path.exists():
        return {"version": MANIFEST_VERSION, "materials": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise IngestionError("O histórico de materiais está ilegível.") from error
    if data.get("version") != MANIFEST_VERSION or not isinstance(data.get("materials"), list):
        raise IngestionError("O histórico de materiais possui um formato incompatível.")
    return data


def find_duplicate(manifest: dict[str, Any], sha256: str) -> dict[str, Any] | None:
    """Localiza uma importação anterior pelo conteúdo, não apenas pelo nome."""

    return next(
        (record for record in manifest["materials"] if record.get("sha256") == sha256),
        None,
    )


def material_filename(title: str, material_number: int | None = None) -> str:
    prefix = f"ma{material_number:02d}_" if material_number else ""
    return f"{prefix}{slugify(title)}.md"


def save_material(
    analysis: PdfAnalysis,
    title: str,
    materials_dir: Path,
    manifest_path: Path,
    material_number: int | None = None,
) -> dict[str, Any]:
    """Persiste somente a versão textual aprovada e atualiza o histórico."""

    normalized_title = clean_title(title)
    manifest = load_manifest(manifest_path)
    duplicate = find_duplicate(manifest, analysis.sha256)
    if duplicate:
        raise IngestionError(
            f"Este PDF já foi incorporado como {duplicate.get('title', 'outro material')}."
        )

    markdown = build_material_markdown(analysis, normalized_title)
    filename = material_filename(normalized_title, material_number)
    materials_dir.mkdir(parents=True, exist_ok=True)
    target = materials_dir / filename
    if target.exists():
        raise IngestionError(
            f"Já existe um material chamado {filename}. Ajuste o título ou o número."
        )

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    record: dict[str, Any] = {
        "id": analysis.sha256[:12],
        "title": normalized_title,
        "material_number": material_number,
        "source_filename": analysis.source_filename,
        "content_file": filename,
        "sha256": analysis.sha256,
        "processed_at": timestamp,
        "page_count": analysis.page_count,
        "indexed_sections": analysis.nonempty_page_count,
        "character_count": analysis.character_count,
        "status": "indexed",
    }
    updated_manifest = {
        "version": MANIFEST_VERSION,
        "materials": [*manifest["materials"], record],
    }

    content_temp = target.with_suffix(".md.tmp")
    manifest_temp = manifest_path.with_suffix(".json.tmp")
    try:
        content_temp.write_text(markdown, encoding="utf-8")
        manifest_temp.write_text(
            json.dumps(updated_manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        content_temp.replace(target)
        manifest_temp.replace(manifest_path)
    except OSError as error:
        content_temp.unlink(missing_ok=True)
        manifest_temp.unlink(missing_ok=True)
        target.unlink(missing_ok=True)
        raise IngestionError("Não foi possível salvar o material na base local.") from error

    return record
