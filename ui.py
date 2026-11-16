"""Sistema visual do Tutor de Algoritmos. Chame ui.setup() no início do app."""

from __future__ import annotations

import html

import streamlit as st


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
:root{--ink:#14213D;--mute:#5B6475;--line:#E3E6EB;--code:#F4F5F7;--red:#EA1D2C;}
.stApp{font-family:'Instrument Sans',sans-serif}
h1,h2,h3{font-family:'Bricolage Grotesque',sans-serif!important;letter-spacing:-.03em;color:var(--ink)}
.block-container{max-width:1040px;padding-top:3.5rem;padding-bottom:3rem}
[data-testid=stSidebar]{border-right:1px solid var(--line)}
[data-testid=stSidebarNavLink]{border-radius:0 6px 6px 0}
[data-testid=stSidebarNavLink][aria-current=page]{background:#fff;box-shadow:inset 3px 0 0 var(--red);font-weight:600}
.wordmark{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:1.25rem;line-height:1.1;letter-spacing:-.03em}
.wordmark span{color:var(--red)}
.side-note{color:var(--mute);font-size:.85rem;margin-top:.4rem}
.stButton>button{border-radius:6px;font-weight:600}
textarea,code,pre{font-family:'JetBrains Mono',monospace!important}
textarea{font-size:.88rem!important;line-height:1.65!important;border-radius:0!important}
[data-testid=stChatMessageAvatarUser],[data-testid=stChatMessageAvatarAssistant]{display:none}
[data-testid=stChatMessage]{background:transparent;border-top:1px solid var(--line);border-radius:0;padding:1rem 0}
.mode-pill{display:inline-block;padding:.3rem .65rem;border:1px solid var(--line);border-radius:999px;color:var(--mute);font-size:.78rem;font-weight:600}

/* hero: um programa e a sua saída */
.hero{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--line);margin:1.5rem 0 1rem}
.hero .src{background:var(--code);padding:1.3rem;font:400 .78rem/1.75 'JetBrains Mono',monospace;white-space:pre;overflow:auto}
.hero .out{padding:1.5rem 2rem;display:flex;flex-direction:column;justify-content:center}
.hero .out small{font:400 .75rem 'JetBrains Mono',monospace;color:var(--mute)}
.hero .out p{font:700 clamp(1.9rem,4.4vw,2.9rem)/1.05 'Bricolage Grotesque',sans-serif;letter-spacing:-.035em;margin:.7rem 0 0}
.lead{max-width:60ch;color:var(--mute);font-size:1.05rem;line-height:1.55}
.base{border-top:1px solid var(--line);padding-top:.9rem;color:var(--mute)}
.base b{color:var(--ink)}
@media(max-width:700px){.hero{grid-template-columns:1fr}.block-container{padding-top:2rem}}

/* etapas reais do fluxo RAG */
.flow{border-left:2px solid var(--line);margin:1rem 0 0 .4rem;padding:0}
.flow li{list-style:none;position:relative;padding:0 0 1.3rem 1.6rem;line-height:1.45}
.flow li::before{content:"";position:absolute;left:-7px;top:.3rem;width:12px;height:12px;border-radius:50%;background:#fff;border:2px solid var(--ink)}
.flow li b{display:block}.flow li span{color:var(--mute)}

/* escada de pistas */
.rung{display:flex;gap:1rem;padding:.9rem 0;border-top:1px solid var(--line);line-height:1.5}
.rung i{flex:none;font-style:normal;width:1.8rem;height:1.8rem;border-radius:50%;display:grid;place-items:center;font-weight:600;font-size:.85rem;border:2px solid #C9CED8;color:var(--mute)}
.rung.open i{background:var(--red);border-color:var(--red);color:#fff}
.rung.lock{opacity:.5}

/* critérios */
.crit{display:flex;justify-content:space-between;gap:1rem;padding:.7rem 0;border-top:1px solid var(--line)}
.crit em{font-style:normal;font-weight:600;white-space:nowrap}
.ok{color:#2E7D5B}.part{color:#B7791F}.miss{color:#B3261E}
</style>
"""


def setup() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def wordmark() -> None:
    st.markdown(
        '<div class="wordmark">Tutor de<br>Algoritmos<span>.</span></div>'
        '<div class="side-note">Projeto de portfólio: busca nos materiais e feedback formativo.</div>',
        unsafe_allow_html=True,
    )


def hero(code_lines: list[str], out_lines: list[str]) -> None:
    source = "\n".join(html.escape(line) for line in code_lines)
    output = "<br>".join(html.escape(line) for line in out_lines)
    st.markdown(
        f'<div class="hero"><div class="src">{source}</div>'
        f'<div class="out"><small>saída</small><p>{output}</p></div></div>',
        unsafe_allow_html=True,
    )


def flow(steps: list[tuple[str, str]]) -> None:
    items = "".join(
        f"<li><b>{html.escape(title)}</b><span>{html.escape(description)}</span></li>"
        for title, description in steps
    )
    st.markdown(f'<ul class="flow">{items}</ul>', unsafe_allow_html=True)


def ladder(hints: list[str], shown: int) -> None:
    rows = ""
    for number, hint in enumerate(hints, start=1):
        is_open = number <= shown
        css_class = "open" if is_open else "lock"
        text = hint if is_open else "Bloqueada. Tente mais um pouco antes de abrir."
        rows += (
            f'<div class="rung {css_class}"><i>{number}</i>'
            f"<div>{html.escape(text)}</div></div>"
        )
    st.markdown(rows, unsafe_allow_html=True)


def criteria(rows: list[tuple[str, str]]) -> None:
    labels = {"ok": "Atende", "part": "Parcial", "miss": "Falta"}
    output = "".join(
        f'<div class="crit"><span>{html.escape(title)}</span>'
        f'<em class="{status}">{labels[status]}</em></div>'
        for title, status in rows
        if status in labels
    )
    st.markdown(output, unsafe_allow_html=True)
