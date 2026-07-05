"""
Real agent graph — stub skeleton (Week 1)
==========================================
Full LangGraph wiring with all nodes as stubs.
Proves routing and retry-loop structure before any real logic is added.

Run directly (smoke-test):
    PYTHONPATH=. python backend/agent/graph.py
"""
from __future__ import annotations

import logging
import sys

from langgraph.graph import END, START, StateGraph

from backend.agent.state import AgentState
from backend.agent.nodes.parse_and_route import (
    parse_and_route,
    route_after_parse,
    route_after_validate,
)
from backend.agent.nodes.generate_sql import generate_sql
from backend.agent.nodes.validate_sql import validate_sql
from backend.agent.nodes.execute_sql import execute_sql
from backend.agent.nodes.retrieve_docs import retrieve_docs
from backend.agent.nodes.synthesize_answer import synthesize_answer
from backend.agent.nodes.generate_chart import generate_chart

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_graph():
    """Construct and compile the full agent graph."""
    builder = StateGraph(AgentState)

    # ── register nodes ──────────────────────────────────────────────────────
    builder.add_node("parse_and_route", parse_and_route)
    builder.add_node("generate_sql", generate_sql)
    builder.add_node("validate_sql", validate_sql)
    builder.add_node("execute_sql", execute_sql)
    builder.add_node("retrieve_docs", retrieve_docs)
    builder.add_node("synthesize_answer", synthesize_answer)
    builder.add_node("generate_chart", generate_chart)

    # ── entry point ─────────────────────────────────────────────────────────
    builder.add_edge(START, "parse_and_route")

    # ── conditional: route after classification ──────────────────────────────
    builder.add_conditional_edges(
        "parse_and_route",
        route_after_parse,
        {
            "generate_sql": "generate_sql",
            "retrieve_docs": "retrieve_docs",
        },
    )

    # ── SQL path ─────────────────────────────────────────────────────────────
    builder.add_edge("generate_sql", "validate_sql")

    # conditional: retry loop — validate_sql → generate_sql (retry) or execute_sql
    builder.add_conditional_edges(
        "validate_sql",
        route_after_validate,
        {
            "generate_sql": "generate_sql",   # retry
            "execute_sql": "execute_sql",     # success
        },
    )

    # ── convergence ──────────────────────────────────────────────────────────
    builder.add_edge("execute_sql", "synthesize_answer")
    builder.add_edge("retrieve_docs", "synthesize_answer")

    # ── output pipeline ──────────────────────────────────────────────────────
    builder.add_edge("synthesize_answer", "generate_chart")
    builder.add_edge("generate_chart", END)

    return builder.compile()


# Singleton compiled graph (imported by main.py)
agent_graph = build_graph()


# ---------------------------------------------------------------------------
# Smoke-test
# ---------------------------------------------------------------------------

def _run_smoke_tests():
    """Run a few test questions and print which nodes fired in what order."""
    test_cases = [
        {"question": "What are the top 5 products by revenue?", "route": "sql"},
        {"question": "Summarise the Q3 earnings report.",       "route": "rag"},
        {"question": "Compare sales data with analyst notes.",   "route": "hybrid"},
    ]

    for tc in test_cases:
        print("\n" + "=" * 60)
        print(f"Question : {tc['question']}")
        print(f"Route    : {tc['route']}")
        print("=" * 60)

        initial_state: AgentState = {
            "question": tc["question"],
            "route": tc["route"],
            "retry_count": 0,
            "sql_query": "",
            "sql_result": None,
            "doc_chunks": [],
            "final_answer": "",
            "chart_data": None,
            "error": None,
        }

        final = agent_graph.invoke(initial_state)

        print("\n--- FINAL STATE ---")
        for k, v in final.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    _run_smoke_tests()
