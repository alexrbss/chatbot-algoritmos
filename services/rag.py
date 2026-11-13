"""Recuperação local de materiais didáticos usando uma baseline BM25.

A implementação não depende de serviços externos e deixa a interface de busca
isolada para que um índice vetorial possa substituí-la futuramente.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


TOKEN_PATTERN = re.compile(r"[a-zA-ZÀ-ÿ0-9_]+")
HEADING_PATTERN = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
STOPWORDS = {
    "a",
    "ao",
    "aos",
    "as",
    "com",
    "como",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "essa",
    "esse",
    "esta",
    "este",
    "eu",
    "foi",
    "mais",
    "na",
    "nas",
    "no",
    "nos",
    "o",
    "os",
    "ou",
    "para",
    "por",
    "que",
    "se",
    "sem",
    "ser",
    "um",
    "uma",
}


def normalize_text(text: str) -> str:
    """Normaliza texto para comparações lexicais previsíveis."""

    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def tokenize(text: str) -> list[str]:
    """Tokeniza o texto removendo palavras funcionais pouco informativas."""

    normalized = normalize_text(text)
    return [
        token
        for token in TOKEN_PATTERN.findall(normalized)
        if len(token) > 1 and token not in STOPWORDS
    ]


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    title: str
    source: str
    content: str


@dataclass(frozen=True)
class RetrievalResult:
    chunk: DocumentChunk
    score: float


def _split_markdown(path: Path) -> list[DocumentChunk]:
    text = path.read_text(encoding="utf-8").strip()
    matches = list(HEADING_PATTERN.finditer(text))
    if not matches:
        return [
            DocumentChunk(
                id=f"{path.stem}-1",
                title=path.stem.replace("_", " ").title(),
                source=path.name,
                content=text,
            )
        ]

    chunks: list[DocumentChunk] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if not content:
            continue
        chunks.append(
            DocumentChunk(
                id=f"{path.stem}-{index + 1}",
                title=match.group(2).strip(),
                source=path.name,
                content=content,
            )
        )
    return chunks


def load_materials(directory: Path) -> list[DocumentChunk]:
    """Carrega arquivos Markdown ou texto em blocos identificáveis."""

    chunks: list[DocumentChunk] = []
    for path in sorted(directory.glob("*")):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        chunks.extend(_split_markdown(path))
    if not chunks:
        raise ValueError(f"Nenhum material .md ou .txt encontrado em {directory}")
    return chunks


class BM25Retriever:
    """Índice BM25 pequeno e suficiente para a demonstração local."""

    def __init__(self, chunks: list[DocumentChunk], k1: float = 1.5, b: float = 0.75):
        if not chunks:
            raise ValueError("O índice precisa de pelo menos um trecho.")
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self._tokens = [tokenize(f"{chunk.title} {chunk.content}") for chunk in chunks]
        self._frequencies = [Counter(tokens) for tokens in self._tokens]
        self._average_length = sum(map(len, self._tokens)) / len(self._tokens)
        self._document_frequency: Counter[str] = Counter()
        for tokens in self._tokens:
            self._document_frequency.update(set(tokens))

    @classmethod
    def from_directory(cls, directory: Path) -> "BM25Retriever":
        return cls(load_materials(directory))

    def _idf(self, term: str) -> float:
        document_count = len(self.chunks)
        frequency = self._document_frequency.get(term, 0)
        return math.log(1 + (document_count - frequency + 0.5) / (frequency + 0.5))

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        terms = tokenize(query)
        if not terms:
            return []

        scored: list[RetrievalResult] = []
        for chunk, frequencies, tokens in zip(
            self.chunks, self._frequencies, self._tokens, strict=True
        ):
            score = 0.0
            document_length = len(tokens) or 1
            for term in terms:
                term_frequency = frequencies.get(term, 0)
                if term_frequency == 0:
                    continue
                denominator = term_frequency + self.k1 * (
                    1 - self.b + self.b * document_length / self._average_length
                )
                score += self._idf(term) * (
                    term_frequency * (self.k1 + 1) / denominator
                )
            if score > 0:
                scored.append(RetrievalResult(chunk=chunk, score=score))

        scored.sort(key=lambda result: result.score, reverse=True)
        return scored[: max(1, top_k)]


def format_context(results: list[RetrievalResult]) -> str:
    """Formata evidências para inclusão controlada no prompt."""

    return "\n\n".join(
        f"[Fonte: {result.chunk.source} — {result.chunk.title}]\n{result.chunk.content}"
        for result in results
    )

