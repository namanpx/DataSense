"""
Node: generate_sql  (Week 2 — real implementation)
====================================================
Calls Groq (Llama 3.3 70B) to generate a DuckDB SQL query from the user question.
On retries, the previous failed SQL and error message are included in the prompt
so the model can self-correct.
"""
from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agent.state import AgentState
from backend.agent.db import get_schema, load_sample_data

load_dotenv()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

GENERATE_SQL_SYSTEM_PROMPT = """You are a DuckDB SQL expert. Your ONLY job is to write a valid DuckDB SQL query.

Rules:
- Output ONLY the SQL query — no markdown fences, no explanation, no comments.
- Use only the tables and columns described in the schema provided.
- DuckDB supports standard SQL. Use strftime or date_trunc for date operations.
- Always alias aggregated columns for readability (e.g. SUM(amount) AS total_revenue).
- Limit results to a reasonable number of rows (LIMIT 20) unless the question asks for all.
- If asked for trends, use DATE_TRUNC('month', sale_date) to group by month.
"""


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------

def generate_sql(state: AgentState) -> AgentState:
    """Generate a SQL query from the user question (with retry context if applicable)."""
    retry_count = state.get("retry_count", 0)
    logger.info("[generate_sql] Attempt %d", retry_count + 1)

    # Ensure data is loaded
    try:
        load_sample_data()
    except Exception as e:
        logger.warning("[generate_sql] Could not load sample data: %s", e)

    schema = get_schema()
    question = state.get("question", "")
    prev_sql = state.get("sql_query", "")
    prev_error = state.get("error", "")

    # Build the user message — include retry context if this is a retry
    if retry_count > 0 and prev_sql and prev_error:
        user_content = f"""Question: {question}

Schema:
{schema}

Previous SQL attempt (FAILED):
{prev_sql}

Error message:
{prev_error}

Please fix the SQL query. Output ONLY the corrected SQL query."""
    else:
        user_content = f"""Question: {question}

Schema:
{schema}

Output ONLY the SQL query."""

    api_key = os.getenv("GROQ_API_KEY")
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        max_tokens=512,
        temperature=0.0,
    )

    messages = [
        SystemMessage(content=GENERATE_SQL_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)
    sql_query = response.content.strip()

    # Strip markdown fences if the model adds them despite instructions
    if sql_query.startswith("```"):
        lines = sql_query.split("\n")
        sql_query = "\n".join(
            line for line in lines
            if not line.startswith("```")
        ).strip()

    logger.info("[generate_sql] Generated SQL:\n%s", sql_query)

    return {
        **state,
        "sql_query": sql_query,
        "retry_count": retry_count + 1,
        "error": None,   # clear error before validation
    }
