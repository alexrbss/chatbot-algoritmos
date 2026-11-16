"""Ponto de entrada da aplicação Streamlit."""

import streamlit as st

import ui


st.set_page_config(
    page_title="Tutor de Algoritmos",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)
ui.setup()

pages = [
    st.Page("app_pages/home.py", title="Visão geral", icon=":material/home:", default=True),
    st.Page("app_pages/tutor.py", title="Tutor", icon=":material/forum:"),
    st.Page("app_pages/exercicios.py", title="Exercícios", icon=":material/edit_note:"),
    st.Page("app_pages/materiais.py", title="Materiais", icon=":material/folder_open:"),
]

with st.sidebar:
    ui.wordmark()

navigation = st.navigation(pages)
navigation.run()

