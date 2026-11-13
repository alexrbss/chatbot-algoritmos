"""Recursos compartilhados e cacheados pelas páginas Streamlit."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from services.feedback import load_exercises
from services.llm import OpenAICompatibleClient
from services.rag import BM25Retriever


ROOT = Path(__file__).resolve().parents[1]
MATERIALS_DIR = ROOT / "data" / "materiais"
EXERCISES_PATH = ROOT / "data" / "exercicios.json"


@st.cache_resource(show_spinner="Indexando materiais da disciplina...")
def get_retriever() -> BM25Retriever:
    return BM25Retriever.from_directory(MATERIALS_DIR)


@st.cache_data(show_spinner=False)
def get_exercises() -> list[dict]:
    return load_exercises(EXERCISES_PATH)


def get_llm_client() -> OpenAICompatibleClient:
    return OpenAICompatibleClient()

