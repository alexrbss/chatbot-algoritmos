"""Página inicial e narrativa do projeto."""

import streamlit as st

from services.bootstrap import get_exercises, get_llm_client, get_retriever


retriever = get_retriever()
exercises = get_exercises()
client = get_llm_client()

st.markdown(
    """
    <section class="hero">
      <div class="eyebrow">IA generativa aplicada à educação</div>
      <h1>Aprenda Algoritmos<br/>com pistas, não atalhos.</h1>
      <p>
        Um tutor que recupera o material da disciplina, responde com fontes e
        transforma tentativas de exercícios em feedback formativo.
      </p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="metric-grid">
      <div class="metric-card"><div class="metric-label">Materiais indexados</div><div class="metric-value">{len({chunk.source for chunk in retriever.chunks})}</div></div>
      <div class="metric-card"><div class="metric-label">Trechos recuperáveis</div><div class="metric-value">{len(retriever.chunks)}</div></div>
      <div class="metric-card"><div class="metric-label">Exercícios</div><div class="metric-value">{len(exercises)}</div></div>
      <div class="metric-card"><div class="metric-label">Modo do modelo</div><div class="metric-value">{"LLM" if client.configured else "Demo"}</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## Como funciona")
cards = [
    ("01 · Pergunta", "O aluno pergunta ou envia uma tentativa de solução."),
    ("02 · Recuperação", "A busca local encontra os trechos mais relevantes da disciplina."),
    ("03 · Evidências", "O modelo recebe contexto controlado e uma rubrica explícita."),
    ("04 · Feedback", "A resposta destaca acertos, lacunas e o próximo passo."),
]
cards_html = "".join(
    f'<div class="feature-card"><div class="eyebrow">{title}</div><p>{description}</p></div>'
    for title, description in cards
)
st.markdown(f'<div class="feature-grid">{cards_html}</div>', unsafe_allow_html=True)

st.markdown("## O que experimentar")
left, right = st.columns([1.1, 1])
with left:
    st.markdown(
        """
        **No Tutor**

        - Pergunte por que um `while` pode entrar em laço infinito.
        - Compare busca linear e acesso por índice.
        - Confira quais fontes sustentam a resposta.
        """
    )
    if st.button("Abrir o Tutor", type="primary", use_container_width=True):
        st.switch_page("app_pages/tutor.py")
with right:
    st.markdown(
        """
        **Nos Exercícios**

        - Escolha uma das cinco questões.
        - Envie uma tentativa incompleta de propósito.
        - Observe a rubrica identificar o próximo passo.
        """
    )
    if st.button("Praticar exercícios", use_container_width=True):
        st.switch_page("app_pages/exercicios.py")

st.info(
    "A base incluída é demonstrativa. Os materiais reais do semestre podem ser "
    "adicionados em `data/materiais` sem alterar a interface."
)

