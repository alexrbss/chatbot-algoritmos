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
        Este tutor segue a ementa de Algoritmos e Programação I. Por isso,
        acompanha a construção do raciocínio em Portugol e a transição dos
        mesmos fundamentos para a linguagem C.
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

        - Pergunte qual é a estrutura de um algoritmo em Portugol.
        - Peça uma comparação entre atribuição em Portugol e em C.
        - Confira quais fontes sustentam a resposta.
        """
    )
    if st.button("Abrir o Tutor", type="primary", use_container_width=True):
        st.switch_page("app_pages/tutor.py")
with right:
    st.markdown(
        """
        **Nos Exercícios**

        - Escolha uma das 20 questões da Lista 001.
        - Envie uma tentativa incompleta de propósito.
        - Observe a rubrica identificar o próximo passo.
        """
    )
    if st.button("Praticar exercícios", use_container_width=True):
        st.switch_page("app_pages/exercicios.py")

st.info(
    "A base atual acompanha os Materiais de Apoio 01, 02 e 03 e a Lista de "
    "Exercício 001. Nesta etapa da ementa, as respostas da lista são escritas em Portugol."
)

