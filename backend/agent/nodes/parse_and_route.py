"""
Node: parse_and_route  (Week 2 — real implementation)
======================================================
Classifies the user question into "sql", "rag", or "hybrid" using
Groq (Llama 3.3 70B) with a few-shot system prompt.

Conditional edge functions (used by graph.py) are also defined here:
  - route_after_parse(state)    → "generate_sql" | "retrieve_docs"
  - route_after_validate(state) → "generate_sql" | "execute_sql"
"""
from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agent.state import AgentState

load_dotenv()
logger = logging.getLogger(__name__)

MAX_RETRIES = 3

# ---------------------------------------------------------------------------
# System prompt for routing
# ---------------------------------------------------------------------------

ROUTING_SYSTEM_PROMPT = """You are a routing classifier for a data analyst chatbot.
Your ONLY job is to classify the user's question into exactly one of these three categories:

  sql    — question about structured/numerical data: aggregations, filters, trends, rankings,
           counts, averages, totals, comparisons of numbers, top/bottom N, time series.
  rag    — question about documents, reports, summaries, qualitative analysis, narratives,
           strategic insights, or anything that needs reading a text document.
  hybrid — question that clearly needs BOTH: e.g. "compare the report's claim about North
           region with the actual sales figures".

Examples:
  Q: "What is the total revenue by category?"            → sql
  Q: "Which region had the most orders last month?"      → sql
  Q: "List the top 5 products by sales amount"           → sql
  Q: "Summarise the key market trends in the report"     → rag
  Q: "What does the report say about the West region?"   → rag
  Q: "What were the strategic recommendations?"          → rag
  Q: "Does the report's claim about Electronics match the actual revenue figures?" → hybrid
  Q: "Compare the analyst notes on Food category with the real sales data"        → hybrid

Respond with ONLY one word — exactly "sql", "rag", or "hybrid". No punctuation, no explanation.
"""


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------

def parse_and_route(state: AgentState) -> AgentState:
    """Classify the user question and set state['route']."""
    question = state.get("question", "")
    logger.info("[parse_and_route] Question: %r", question)

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.warning("[parse_and_route] GROQ_API_KEY not set — defaulting to 'sql'")
        return {**state, "route": "sql", "retry_count": 0}

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        max_tokens=5,          # we only need one word back
        temperature=0.0,
    )

    messages = [
        SystemMessage(content=ROUTING_SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    response = llm.invoke(messages)
    route_raw = response.content.strip().lower()

    # Sanitise — accept only valid values
    route = route_raw if route_raw in ("sql", "rag", "hybrid") else "sql"

    logger.info(
        "[parse_and_route] Classified → '%s'  (raw: %r)", route, route_raw
    )

    return {
        **state,
        "route": route,
        "retry_count": state.get("retry_count") or 0,
    }


# ---------------------------------------------------------------------------
# Conditional edge functions (imported by graph.py)
# ---------------------------------------------------------------------------

def route_after_parse(state: AgentState) -> str:
    """Decide which branch to take after routing."""
    route = state.get("route", "sql")
    if route in ("sql", "hybrid"):
        logger.info("[EDGE] route_after_parse → generate_sql  (route=%s)", route)
        return "generate_sql"
    logger.info("[EDGE] route_after_parse → retrieve_docs  (route=%s)", route)
    return "retrieve_docs"


def route_after_validate(state: AgentState) -> str:
    """Retry SQL generation on failure, or proceed to execute."""
    error       = state.get("error")
    retry_count = state.get("retry_count", 0)

    if error and retry_count < MAX_RETRIES:
        logger.info(
            "[EDGE] route_after_validate → generate_sql  (retry %d/%d, error: %s)",
            retry_count, MAX_RETRIES, error,
        )
        return "generate_sql"

    logger.info("[EDGE] route_after_validate → execute_sql")
    return "execute_sql"
