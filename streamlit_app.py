"""Ponto de entrada da aplicação Streamlit."""

import streamlit as st


st.set_page_config(
    page_title="Tutor de Algoritmos",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --tutor-accent: #e23b32;
        --tutor-ink: #17212b;
        --tutor-soft: #fff3ef;
    }
    .block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1180px;}
    .hero {
        padding: 2.4rem 2.6rem;
        border: 1px solid rgba(226, 59, 50, .18);
        border-radius: 24px;
        background: linear-gradient(135deg, #fff8f5 0%, #ffffff 55%, #f4f8ff 100%);
        box-shadow: 0 18px 50px rgba(23, 33, 43, .07);
        margin-bottom: 1.7rem;
    }
    .eyebrow {
        color: var(--tutor-accent);
        font-weight: 750;
        letter-spacing: .08em;
        text-transform: uppercase;
        font-size: .78rem;
    }
    .hero h1 {color: var(--tutor-ink); font-size: 3rem; line-height: 1.03; margin: .45rem 0 .8rem;}
    .hero p {color: #52606d; font-size: 1.08rem; max-width: 760px; margin: 0;}
    .feature-card {
        padding: 1.2rem 1.25rem;
        min-height: 152px;
        border: 1px solid rgba(23, 33, 43, .09);
        border-radius: 18px;
        background: rgba(255,255,255,.76);
    }
    .feature-card h3 {font-size: 1.02rem; margin: .2rem 0 .45rem;}
    .feature-card p {color: #607080; font-size: .93rem; margin: 0;}
    .feature-grid, .metric-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: .85rem;
        margin: 1rem 0 1.7rem;
    }
    .metric-card {
        padding: 1rem 1.1rem;
        border-radius: 16px;
        background: #ffffff;
        border: 1px solid rgba(23, 33, 43, .09);
    }
    .metric-label {color: #697887; font-size: .82rem; font-weight: 650;}
    .metric-value {color: var(--tutor-ink); font-size: 1.75rem; font-weight: 750; margin-top: .25rem;}
    .source-card {
        border-left: 4px solid var(--tutor-accent);
        padding: .8rem 1rem;
        border-radius: 8px;
        background: var(--tutor-soft);
        margin: .5rem 0;
    }
    .mode-pill {
        display: inline-block;
        padding: .28rem .62rem;
        border-radius: 999px;
        background: #f1f4f8;
        color: #435466;
        font-size: .78rem;
        font-weight: 650;
    }
    [data-testid="stSidebar"] {border-right: 1px solid rgba(23, 33, 43, .08);}
    @media (max-width: 700px) {
        .hero {padding: 1.7rem 1.4rem;}
        .hero h1 {font-size: 2.2rem;}
        .feature-grid, .metric-grid {grid-template-columns: 1fr;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

pages = [
    st.Page("app_pages/home.py", title="Visão geral", icon="🏠", default=True),
    st.Page("app_pages/tutor.py", title="Tutor", icon="💬"),
    st.Page("app_pages/exercicios.py", title="Exercícios", icon="🧩"),
    st.Page("app_pages/materiais.py", title="Gerenciar materiais", icon="⚙️"),
]

with st.sidebar:
    st.markdown("### 🧠 Tutor de Algoritmos")
    st.caption("MVP de portfólio · RAG + feedback formativo")
    st.divider()

navigation = st.navigation(pages)
navigation.run()

