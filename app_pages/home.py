"""Página inicial e narrativa do projeto."""

import streamlit as st

import ui

from services.bootstrap import get_exercises, get_llm_client, get_retriever


retriever = get_retriever()
exercises = get_exercises()
client = get_llm_client()

st.title("Algoritmos com pistas, não com atalhos")
ui.hero(
    [
        'algoritmo "tutor"',
        "inicio",
        '  escreval("Com pistas,")',
        '  escreval("sem atalhos.")',
        "fimalgoritmo",
    ],
    ["Com pistas,", "sem atalhos."],
)
st.markdown(
    '<p class="lead">Um tutor para Algoritmos e Programação I. Ele acompanha o '
    "raciocínio em Portugol e leva os mesmos fundamentos para a linguagem C, "
    "sempre apontando de onde veio a explicação.</p>",
    unsafe_allow_html=True,
)
material_count = len({chunk.source for chunk in retriever.chunks})
mode = "LLM conectado" if client.configured else "modo demonstração"
st.markdown(
    f'<p class="base">Base atual: <b>{material_count} materiais</b>, '
    f'<b>{len(retriever.chunks)} trechos</b> recuperáveis e '
    f'<b>{len(exercises)} exercícios</b>. Modelo em <b>{mode}</b>.</p>',
    unsafe_allow_html=True,
)

st.subheader("O caminho de uma pergunta")
ui.flow(
    [
        ("Você pergunta ou envia uma tentativa", "Em texto livre ou com seu código em Portugol."),
        ("O tutor busca nos materiais", "A recuperação local seleciona os trechos mais próximos da dúvida."),
        ("A resposta mostra as fontes", "O modelo recebe contexto controlado e uma rubrica explícita."),
        ("Você recebe feedback", "Acertos, lacunas e o próximo passo, sem entregar a solução automaticamente."),
        ("A base pode evoluir", "Novos PDFs passam por revisão e teste antes da indexação."),
    ]
)

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

st.markdown("### Automação da base de conhecimento")
automation_left, automation_right = st.columns([2, 1])
with automation_left:
    st.write(
        "Envie um novo material em PDF, revise o texto extraído, teste a recuperação "
        "e aprove a atualização do tutor — com histórico e bloqueio de duplicatas."
    )
with automation_right:
    if st.button("Gerenciar materiais", use_container_width=True):
        st.switch_page("app_pages/materiais.py")

st.info(
    "A base atual acompanha os Materiais de Apoio 01, 02 e 03 e a Lista de "
    "Exercício 001. Nesta etapa da ementa, as respostas da lista são escritas em Portugol."
)

