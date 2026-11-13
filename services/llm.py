"""Cliente de LLM desacoplado e fallback demonstrável sem credenciais."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from services.rag import RetrievalResult, format_context


SYSTEM_PROMPT = """Você é um tutor de Algoritmos e Programação I para estudantes iniciantes.
Responda em português brasileiro, com clareza e objetividade.
Use somente as evidências fornecidas quando falar sobre o conteúdo da disciplina.
Se as evidências forem insuficientes, diga isso explicitamente.
Ajude o aluno a raciocinar: dê pistas antes de entregar uma solução completa.
Siga a ementa: use Portugol como linguagem principal nos exercícios introdutórios
e C quando o aluno pedir a tradução dos conceitos para uma linguagem de programação.
Não substitua uma solução solicitada em Portugol por Python.
Ao usar um trecho, cite sua fonte no formato [arquivo — seção].
Não invente notas, regras ou referências."""


@dataclass(frozen=True)
class LLMResult:
    text: str
    mode: str
    error: str | None = None


class OpenAICompatibleClient:
    """Acessa qualquer endpoint compatível com Chat Completions."""

    def __init__(
        self,
        api_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.api_url = api_url or os.getenv("LLM_API_URL", "")
        self.model = model or os.getenv("LLM_MODEL", "")
        self.api_key = api_key if api_key is not None else os.getenv("LLM_API_KEY", "")

    @property
    def configured(self) -> bool:
        return bool(self.api_url and self.model)

    @property
    def label(self) -> str:
        return self.model if self.configured else "demonstração local"

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResult:
        if not self.configured:
            return LLMResult(text="", mode="demo")

        payload = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.2,
            }
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = urllib.request.Request(
            self.api_url,
            data=payload,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
            text = body["choices"][0]["message"]["content"].strip()
            return LLMResult(text=text, mode="llm")
        except (KeyError, IndexError, json.JSONDecodeError, urllib.error.URLError) as exc:
            return LLMResult(
                text="",
                mode="demo",
                error=f"O endpoint de LLM não respondeu como esperado: {exc}",
            )


def _demo_answer(question: str, results: list[RetrievalResult]) -> str:
    if not results:
        return (
            "Não encontrei uma seção suficientemente próxima dessa pergunta na base "
            "de demonstração. Tente mencionar o conceito principal ou adicione o "
            "material correspondente à pasta `data/materiais`."
        )

    primary = results[0].chunk
    excerpt = " ".join(primary.content.split())
    if len(excerpt) > 480:
        excerpt = excerpt[:477].rstrip() + "..."
    return (
        "**Ponto principal encontrado no material**\n\n"
        f"{excerpt}\n\n"
        f"Fonte: [{primary.source} — {primary.title}]\n\n"
        "**Para avançar no raciocínio**\n\n"
        f"Relacione esse conceito à sua pergunta — “{question.strip()}” — e tente "
        "identificar quais são as entradas, o processamento e a saída do algoritmo. "
        "Este é o modo demonstrativo; configure um endpoint de LLM para obter uma "
        "explicação generativa completa."
    )


def answer_question(
    question: str,
    results: list[RetrievalResult],
    client: OpenAICompatibleClient | None = None,
    extra_context: str = "",
) -> LLMResult:
    client = client or OpenAICompatibleClient()
    context = format_context(results)
    prompt = f"""Pergunta do aluno:
{question}

Contexto adicional:
{extra_context or "Nenhum."}

Evidências recuperadas:
{context or "Nenhuma evidência recuperada."}

Produza uma resposta didática e curta. Não revele uma solução completa se uma dica
for suficiente."""
    result = client.complete(SYSTEM_PROMPT, prompt)
    if result.mode == "llm":
        return result
    return LLMResult(
        text=_demo_answer(question, results),
        mode="demo",
        error=result.error,
    )

