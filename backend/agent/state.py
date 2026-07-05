"""
AgentState — the single shared state object that flows through every node
in the LangGraph pipeline.
"""
from __future__ import annotations

from typing import TypedDict


class AgentState(TypedDict):
    """Shared state passed between all LangGraph nodes."""

    # ---------- input ----------
    question: str                   # raw user question

    # ---------- routing ----------
    route: str                      # "sql" | "rag" | "hybrid"
    retry_count: int                # number of SQL-validation retries so far

    # ---------- SQL path ----------
    sql_query: str                  # generated SQL statement
    sql_result: dict | None         # rows returned by DuckDB (None until executed)

    # ---------- RAG path ----------
    doc_chunks: list                # retrieved document chunks

    # ---------- output ----------
    final_answer: str               # synthesised natural-language answer
    chart_data: dict | None         # Plotly-compatible dict for chart (None if no chart)

    # ---------- error handling ----------
    error: str | None               # last error message, if any
