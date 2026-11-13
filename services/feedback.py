"""Avaliação formativa baseada em rubrica e evidências recuperadas."""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path

from services.llm import LLMResult, OpenAICompatibleClient
from services.rag import RetrievalResult, format_context, normalize_text


@dataclass(frozen=True)
class CriterionCheck:
    criterion: str
    met: bool
    hint: str


@dataclass(frozen=True)
class FeedbackReport:
    checks: list[CriterionCheck]
    syntax_ok: bool | None
    syntax_message: str | None
    strengths: list[str]
    improvements: list[str]
    next_step: str
    narrative: LLMResult

    @property
    def progress(self) -> float:
        if not self.checks:
            return 0.0
        return sum(check.met for check in self.checks) / len(self.checks)


def load_exercises(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as file:
        exercises = json.load(file)
    if not isinstance(exercises, list) or not exercises:
        raise ValueError("O arquivo de exercícios deve conter uma lista não vazia.")
    return exercises


def _check_submission_syntax(
    submission: str, answer_type: str
) -> tuple[bool | None, str | None]:
    if answer_type == "python":
        try:
            ast.parse(submission)
            return True, "A estrutura enviada possui sintaxe Python válida."
        except SyntaxError as exc:
            location = f"linha {exc.lineno}" if exc.lineno else "posição desconhecida"
            return False, f"Há um erro de sintaxe na {location}: {exc.msg}."

    if answer_type == "portugol":
        normalized = normalize_text(submission)
        required = ["algoritmo", "var", "inicio", "fimalgoritmo"]
        missing = [item for item in required if item not in normalized]
        if missing:
            return (
                False,
                "A estrutura de Portugol está incompleta. Faltam: " + ", ".join(missing) + ".",
            )
        positions = [normalized.find(item) for item in required]
        if positions != sorted(positions):
            return False, "Revise a ordem: algoritmo, var, inicio e fimalgoritmo."
        return True, "A tentativa contém a estrutura básica de um algoritmo em Portugol."

    return None, None


def _demo_narrative(
    checks: list[CriterionCheck],
    syntax_ok: bool | None,
    results: list[RetrievalResult],
) -> str:
    met = [check.criterion for check in checks if check.met]
    missing = [check for check in checks if not check.met]
    parts = []
    if met:
        parts.append("Você já contemplou: " + "; ".join(met) + ".")
    if syntax_ok is False:
        parts.append("Antes de avaliar a lógica, corrija o erro de sintaxe indicado.")
    elif missing:
        parts.append("O próximo ponto a revisar é: " + missing[0].hint)
    else:
        parts.append("A tentativa cobre os critérios essenciais da rubrica.")
    if results:
        source = results[0].chunk
        parts.append(f"Revise [{source.source} — {source.title}] para conferir o conceito.")
    return "\n\n".join(parts)


def analyze_submission(
    exercise: dict,
    submission: str,
    results: list[RetrievalResult],
    client: OpenAICompatibleClient | None = None,
) -> FeedbackReport:
    normalized_submission = normalize_text(submission)
    compact_submission = "".join(normalized_submission.split())
    checks: list[CriterionCheck] = []
    for item in exercise["rubric"]:
        terms = [normalize_text(term) for term in item.get("terms", [])]
        term_matches = [
            term in normalized_submission or "".join(term.split()) in compact_submission
            for term in terms
        ]
        if item.get("match") == "all":
            met = all(term_matches) if terms else False
        else:
            met = any(term_matches) if terms else False
        for term, minimum in item.get("min_occurrences", {}).items():
            normalized_term = normalize_text(term)
            met = met and max(
                normalized_submission.count(normalized_term),
                compact_submission.count("".join(normalized_term.split())),
            ) >= minimum
        checks.append(
            CriterionCheck(
                criterion=item["criterion"],
                met=met,
                hint=item["hint"],
            )
        )

    syntax_ok, syntax_message = _check_submission_syntax(
        submission, exercise.get("answer_type", "text")
    )
    strengths = [check.criterion for check in checks if check.met]
    improvements = [check.hint for check in checks if not check.met]
    if syntax_ok is False and syntax_message:
        improvements.insert(0, syntax_message)

    if syntax_ok is False:
        next_step = "Corrija primeiro a sintaxe e envie a tentativa novamente."
    elif improvements:
        next_step = improvements[0]
    else:
        next_step = "Faça um teste de mesa com um caso limite antes de considerar a solução finalizada."

    client = client or OpenAICompatibleClient()
    prompt = f"""Exercício: {exercise['title']}
Enunciado: {exercise['statement']}

Tentativa do aluno:
{submission}

Critérios detectados:
{json.dumps([check.__dict__ for check in checks], ensure_ascii=False)}

Evidências da disciplina:
{format_context(results) or "Nenhuma evidência recuperada."}

Escreva um feedback formativo em português com: acerto principal, ponto de
melhoria e uma próxima ação. Não dê nota e não entregue a solução completa."""
    generated = client.complete(
        "Você é um tutor de Algoritmos. Baseie-se na rubrica e nas evidências; não invente critérios.",
        prompt,
    )
    if generated.mode != "llm":
        generated = LLMResult(
            text=_demo_narrative(checks, syntax_ok, results),
            mode="demo",
            error=generated.error,
        )

    return FeedbackReport(
        checks=checks,
        syntax_ok=syntax_ok,
        syntax_message=syntax_message,
        strengths=strengths,
        improvements=improvements,
        next_step=next_step,
        narrative=generated,
    )

