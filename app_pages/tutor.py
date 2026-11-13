"""Chat educacional com recuperação de fontes."""

import streamlit as st

from services.bootstrap import get_llm_client, get_retriever
from services.llm import answer_question


retriever = get_retriever()
client = get_llm_client()

st.title("Tutor com fontes")
st.caption(
    "Faça perguntas sobre os materiais de Algoritmos. A resposta mostra os trechos recuperados."
)

top_bar_left, top_bar_right = st.columns([3, 1])
with top_bar_left:
    mode = f"Modelo: {client.label}"
    st.markdown(f'<span class="mode-pill">{mode}</span>', unsafe_allow_html=True)
with top_bar_right:
    if st.button("Limpar conversa", use_container_width=True):
        st.session_state.tutor_messages = []
        st.rerun()

st.session_state.setdefault(
    "tutor_messages",
    [
        {
            "role": "assistant",
            "content": "Olá! Posso explicar conceitos de Algoritmos usando os materiais da disciplina. O que você está estudando?",
            "sources": [],
            "mode": "system",
        }
    ],
)

for message in st.session_state.tutor_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        sources = message.get("sources", [])
        if sources:
            with st.expander(f"Fontes recuperadas ({len(sources)})"):
                for source in sources:
                    st.markdown(
                        f"**{source['title']}** · `{source['source']}` · relevância {source['score']:.2f}"
                    )
                    st.caption(source["excerpt"])

if question := st.chat_input("Ex.: Por que um while pode entrar em laço infinito?"):
    st.session_state.tutor_messages.append(
        {"role": "user", "content": question, "sources": [], "mode": "user"}
    )
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Consultando os materiais..."):
            results = retriever.search(question, top_k=3)
            response = answer_question(question, results, client)
        st.markdown(response.text)
        source_payload = [
            {
                "title": result.chunk.title,
                "source": result.chunk.source,
                "score": result.score,
                "excerpt": " ".join(result.chunk.content.split())[:300] + "…",
            }
            for result in results
        ]
        if source_payload:
            with st.expander(f"Fontes recuperadas ({len(source_payload)})"):
                for source in source_payload:
                    st.markdown(
                        f"**{source['title']}** · `{source['source']}` · relevância {source['score']:.2f}"
                    )
                    st.caption(source["excerpt"])
        if response.error:
            st.warning(response.error)

    st.session_state.tutor_messages.append(
        {
            "role": "assistant",
            "content": response.text,
            "sources": source_payload,
            "mode": response.mode,
        }
    )

if not client.configured:
    st.caption(
        "Modo demonstração ativo: a recuperação funciona localmente e a resposta é extrativa. "
        "Configure `LLM_API_URL` e `LLM_MODEL` para habilitar geração."
    )

