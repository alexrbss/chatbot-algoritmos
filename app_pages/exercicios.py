"""Exercícios com análise por rubrica e chat contextual."""

import streamlit as st

from services.bootstrap import get_exercises, get_llm_client, get_retriever
from services.feedback import analyze_submission
from services.llm import answer_question


exercises = get_exercises()
retriever = get_retriever()
client = get_llm_client()

st.title("Laboratório de exercícios")
st.caption("Envie uma tentativa e receba feedback formativo — sem nota e sem solução automática.")

labels = {exercise["id"]: f"{exercise['title']} · {exercise['difficulty']}" for exercise in exercises}
selected_id = st.selectbox(
    "Escolha um exercício",
    options=list(labels),
    format_func=labels.get,
)
exercise = next(item for item in exercises if item["id"] == selected_id)

meta_1, meta_2, meta_3 = st.columns(3)
meta_1.metric("Tópico", exercise["topic"])
meta_2.metric("Nível", exercise["difficulty"])
meta_3.metric("Critérios", len(exercise["rubric"]))

st.markdown("### Enunciado")
st.write(exercise["statement"])

with st.expander("Ver os critérios de feedback"):
    for item in exercise["rubric"]:
        st.markdown(f"- {item['criterion']}")

submission_key = f"submission_{selected_id}"
if submission_key not in st.session_state:
    st.session_state[submission_key] = exercise["starter_code"]

submission = st.text_area(
    "Sua tentativa",
    key=submission_key,
    height=250,
    help="A análise é estática: o código não é executado nesta versão do MVP.",
)

if st.button("Analisar tentativa", type="primary", use_container_width=True):
    if not submission.strip():
        st.warning("Escreva uma tentativa antes de solicitar feedback.")
    else:
        with st.spinner("Comparando a tentativa com a rubrica e os materiais..."):
            results = retriever.search(
                f"{exercise['reference_query']} {submission[:500]}", top_k=3
            )
            report = analyze_submission(exercise, submission, results, client)
            st.session_state[f"report_{selected_id}"] = (report, results)

stored = st.session_state.get(f"report_{selected_id}")
if stored:
    report, results = stored
    st.markdown("### Feedback")
    st.progress(report.progress, text=f"{report.progress:.0%} dos critérios identificados")

    if report.syntax_ok is True:
        st.success(report.syntax_message)
    elif report.syntax_ok is False:
        st.error(report.syntax_message)

    st.markdown(report.narrative.text)

    strength_col, improve_col = st.columns(2)
    with strength_col:
        st.markdown("#### Já aparece na tentativa")
        if report.strengths:
            for strength in report.strengths:
                st.markdown(f"- ✅ {strength}")
        else:
            st.caption("Nenhum critério foi identificado ainda — isso faz parte da primeira tentativa.")
    with improve_col:
        st.markdown("#### Próximos ajustes")
        if report.improvements:
            for improvement in report.improvements[:3]:
                st.markdown(f"- 🔎 {improvement}")
        else:
            st.markdown("- Faça testes de mesa e considere casos limite.")

    st.info(f"**Próximo passo:** {report.next_step}")
    with st.expander("Materiais usados no feedback"):
        for result in results:
            st.markdown(
                f"**{result.chunk.title}** · `{result.chunk.source}` · relevância {result.score:.2f}"
            )
            st.caption(" ".join(result.chunk.content.split())[:320] + "…")
    if report.narrative.error:
        st.warning(report.narrative.error)

st.divider()
st.markdown("### Tire uma dúvida sobre esta questão")
chat_key = f"exercise_chat_{selected_id}"
st.session_state.setdefault(chat_key, [])
for message in st.session_state[chat_key]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Peça uma dica sem solicitar a solução completa"):
    st.session_state[chat_key].append({"role": "user", "content": question})
    results = retriever.search(f"{exercise['reference_query']} {question}", top_k=3)
    extra_context = (
        f"Exercício atual: {exercise['statement']}\n"
        f"Tentativa atual do aluno:\n{submission[:1200]}"
    )
    response = answer_question(question, results, client, extra_context=extra_context)
    st.session_state[chat_key].append({"role": "assistant", "content": response.text})
    st.rerun()

