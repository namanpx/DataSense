"""
Toy LangGraph — Week 1 smoke-test
==================================
A minimal 3-node graph:
  START → echo_node → llm_call_node → END

Run directly:
    python -m backend.agent.toy_graph
or (from project root):
    PYTHONPATH=. python backend/agent/toy_graph.py
"""
from __future__ import annotations

import logging
import os
import sys
from typing import TypedDict

from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Toy state
# ---------------------------------------------------------------------------

class ToyState(TypedDict):
    question: str
    answer: str


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def echo_node(state: ToyState) -> ToyState:
    """Pass the question through unchanged — just log that we're alive."""
    logger.info("[TOY NODE] echo_node — question: %r", state["question"])
    return state


def llm_call_node(state: ToyState) -> ToyState:
    """Call the Groq API (Llama 3.3) and store the response in state['answer']."""
    logger.info("[TOY NODE] llm_call_node — calling Groq (Llama 3.3)…")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Get a free key at https://console.groq.com (no credit card needed).\n"
            "Then add GROQ_API_KEY=gsk_... to your .env file."
        )

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        max_tokens=256,
    )
    response = llm.invoke(state["question"])
    answer = response.content
    logger.info("[TOY NODE] llm_call_node — received %d chars", len(answer))
    return {**state, "answer": answer}


# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def build_toy_graph():
    builder = StateGraph(ToyState)
    builder.add_node("echo_node", echo_node)
    builder.add_node("llm_call_node", llm_call_node)
    builder.add_edge(START, "echo_node")
    builder.add_edge("echo_node", "llm_call_node")
    builder.add_edge("llm_call_node", END)
    return builder.compile()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Load .env if present (requires python-dotenv)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv optional at this stage

    toy_graph = build_toy_graph()

    test_question = (
        "What is 7 multiplied by 6? "
        "Give me just the number and a one-sentence explanation."
    )

    print("\n" + "=" * 60)
    print("TOY GRAPH — Week 1 smoke-test")
    print("=" * 60)
    print(f"Question : {test_question}\n")

    final_state = toy_graph.invoke({"question": test_question, "answer": ""})

    print("\n--- FINAL STATE ---")
    for k, v in final_state.items():
        print(f"  {k}: {v}")
    print("=" * 60 + "\n")
