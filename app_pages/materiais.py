"""Interface de ingestão assistida e atualização local da base RAG."""

from __future__ import annotations

import hashlib
from pathlib import Path

import streamlit as st

from services.bootstrap import MANIFEST_PATH, MATERIALS_DIR, get_retriever
from services.ingestion import (
    IngestionError,
    analyze_pdf,
    build_preview_chunks,
    find_duplicate,
    load_manifest,
    save_material,
)
from services.rag import BM25Retriever


def suggested_title(filename: str) -> str:
    return Path(filename).stem.replace("_", " ").replace("-", " ").strip().title()


st.title("Gerenciar materiais")
st.caption(
    "Automação local para transformar um PDF revisado em conteúdo recuperável pelo tutor."
)

st.info(
    "O PDF permanece somente em memória. Após sua aprovação, o sistema salva apenas o "
    "texto em Markdown e um registro de auditoria com hash, data e quantidade de páginas."
)

with st.expander("Como funciona esta automação"):
    st.markdown(
        """
        1. **Validar:** confere formato, tamanho, proteção e quantidade de páginas.
        2. **Extrair:** lê o texto e sinaliza páginas vazias ou possíveis PDFs escaneados.
        3. **Revisar:** mostra a prévia e os trechos antes de qualquer alteração na base.
        4. **Testar:** executa uma busca temporária para conferir a recuperação.
        5. **Aprovar:** grava o Markdown, registra o hash e recarrega o índice do tutor.
        """
    )

if added := st.session_state.pop("material_added", None):
    st.success(
        f"Material “{added['title']}” incorporado. O tutor já usa {added['indexed_sections']} "
        "novo(s) trecho(s)."
    )

st.markdown("### 1 · Envie e identifique")
uploaded = st.file_uploader(
    "Material em PDF",
    type=["pdf"],
    help="Limite do MVP: 15 MB e 120 páginas. PDFs escaneados ainda não passam por OCR.",
)

upload_identity = uploaded.name if uploaded else None
if upload_identity != st.session_state.get("material_upload_identity"):
    st.session_state.material_upload_identity = upload_identity
    st.session_state.material_title = suggested_title(uploaded.name) if uploaded else ""
    st.session_state.pop("pdf_analysis", None)

default_title = suggested_title(uploaded.name) if uploaded else ""
title = st.text_input(
    "Título do material",
    key="material_title",
    placeholder="Ex.: Estruturas condicionais",
)
number = st.number_input(
    "Número do material (opcional)",
    min_value=0,
    max_value=99,
    value=0,
    help="Use 0 quando o material não fizer parte da sequência MA01, MA02, …",
)

if st.button(
    "Analisar PDF",
    type="primary",
    disabled=uploaded is None,
    use_container_width=True,
):
    try:
        with st.spinner("Extraindo e validando o conteúdo…"):
            analysis = analyze_pdf(uploaded.getvalue(), uploaded.name)
        st.session_state.pdf_analysis = analysis
    except IngestionError as error:
        st.session_state.pop("pdf_analysis", None)
        st.error(str(error))

analysis = st.session_state.get("pdf_analysis")
current_hash = hashlib.sha256(uploaded.getvalue()).hexdigest() if uploaded else None
if analysis and (
    uploaded is None
    or analysis.source_filename != Path(uploaded.name).name
    or analysis.sha256 != current_hash
):
    st.session_state.pop("pdf_analysis", None)
    analysis = None

if analysis:
    manifest = load_manifest(MANIFEST_PATH)
    duplicate = find_duplicate(manifest, analysis.sha256)

    st.markdown("### 2 · Revise a extração")
    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Páginas", analysis.page_count)
    metric_2.metric("Com texto", analysis.nonempty_page_count)
    metric_3.metric("Caracteres", f"{analysis.character_count:,}".replace(",", "."))
    metric_4.metric("Tamanho", f"{analysis.file_size / 1024:.0f} KB")

    st.caption(f"SHA-256: `{analysis.sha256[:20]}…`")
    for warning in analysis.warnings:
        st.warning(warning)
    if duplicate:
        st.error(
            f"Conteúdo duplicado: este PDF já foi incorporado como “{duplicate['title']}” "
            f"em {duplicate['content_file']}."
        )

    preview_text = "\n\n".join(
        f"PÁGINA {page.number}\n{page.text}" for page in analysis.pages if page.text
    )
    st.text_area(
        "Prévia do texto extraído",
        value=preview_text[:12000],
        height=300,
        disabled=True,
        help="A prévia é limitada na tela; o arquivo aprovado preserva todo o texto extraído.",
    )

    with st.expander(f"Ver {analysis.nonempty_page_count} trecho(s) que serão indexados"):
        for page in analysis.pages:
            if page.text:
                st.markdown(f"**Página {page.number}**")
                st.caption(page.text[:500] + ("…" if len(page.text) > 500 else ""))
                st.divider()

    st.markdown("### 3 · Teste a recuperação")
    query = st.text_input(
        "Pergunta de teste",
        placeholder="Ex.: Como funciona uma estrutura condicional?",
        key="material_test_query",
    )
    if st.button("Testar busca antes de salvar", disabled=not query.strip()):
        preview_chunks = build_preview_chunks(analysis, title or default_title or "Novo material")
        preview_retriever = BM25Retriever(preview_chunks)
        results = preview_retriever.search(query, top_k=3)
        if results:
            for result in results:
                with st.container(border=True):
                    st.markdown(f"**{result.chunk.title}**")
                    st.caption(f"Relevância {result.score:.2f}")
                    excerpt = result.chunk.content[:420]
                    st.write(excerpt + ("…" if len(result.chunk.content) > 420 else ""))
        else:
            st.warning("A pergunta não encontrou termos correspondentes neste material.")

    st.markdown("### 4 · Aprove a atualização")
    approved = st.checkbox(
        "Revisei a prévia e autorizo a inclusão deste texto na base local.",
        disabled=bool(duplicate),
    )
    if st.button(
        "Adicionar à base de conhecimento",
        type="primary",
        use_container_width=True,
        disabled=not approved or bool(duplicate) or not title.strip(),
    ):
        try:
            record = save_material(
                analysis=analysis,
                title=title,
                materials_dir=MATERIALS_DIR,
                manifest_path=MANIFEST_PATH,
                material_number=int(number) or None,
            )
            get_retriever.clear()
            st.session_state.material_added = record
            st.session_state.pop("pdf_analysis", None)
            st.rerun()
        except IngestionError as error:
            st.error(str(error))

st.divider()
st.markdown("### Histórico da automação")
try:
    history = load_manifest(MANIFEST_PATH)["materials"]
except IngestionError as error:
    st.error(str(error))
    history = []

if history:
    rows = [
        {
            "Material": item["title"],
            "Arquivo indexado": item["content_file"],
            "Páginas": item["page_count"],
            "Trechos": item["indexed_sections"],
            "Processado em": item["processed_at"],
            "Status": item["status"],
        }
        for item in reversed(history)
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
else:
    st.caption(
        "Nenhum PDF foi incorporado pela automação ainda. Os materiais atuais foram "
        "preparados manualmente e continuam disponíveis no tutor."
    )
