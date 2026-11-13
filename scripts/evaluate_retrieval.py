"""Executa uma avaliação pequena e reproduzível da recuperação de contexto."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.rag import BM25Retriever  # noqa: E402


def main() -> int:
    retriever = BM25Retriever.from_directory(ROOT / "data" / "materiais")
    cases = json.loads((ROOT / "data" / "evals" / "retrieval.json").read_text(encoding="utf-8"))

    hits = 0
    reciprocal_rank = 0.0
    print("Avaliação de recuperação (top-3)\n")
    for index, case in enumerate(cases, start=1):
        results = retriever.search(case["question"], top_k=3)
        sources = [result.chunk.source for result in results]
        try:
            rank = sources.index(case["expected_source"]) + 1
        except ValueError:
            rank = None
        if rank:
            hits += 1
            reciprocal_rank += 1 / rank
        status = "OK" if rank else "FALHA"
        print(f"{index}. [{status}] {case['question']}")
        print(f"   esperado: {case['expected_source']} | retornado: {sources}")

    total = len(cases)
    print(f"\nHit@3: {hits / total:.1%}")
    print(f"MRR: {reciprocal_rank / total:.3f}")
    return 0 if hits == total else 1


if __name__ == "__main__":
    raise SystemExit(main())

