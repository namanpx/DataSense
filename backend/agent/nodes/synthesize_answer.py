"""
Node: synthesize_answer  (Week 3 — real implementation)
=========================================================
Calls Groq (Llama 3.3 70B) to turn SQL results and/or retrieved doc chunks
into a clean, natural-language answer for the user.
"""
from __future__ import annotations

import json
import logging
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agent.state import AgentState

load_dotenv()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a data analyst assistant. Your job is to write a clear, 
concise, natural-language answer to the user's question based on the data provided.

Rules:
- Be direct and specific — cite actual numbers from the data.
- Use bullet points or short paragraphs for readability.
- Do NOT mention SQL, databases, or technical implementation details.
- If both SQL results and document chunks are provided, integrate both.
- Keep the answer under 200 words unless the question genuinely requires more.
- If the data is empty or an error occurred, say so clearly and helpfully.
"""


def synthesize_answer(state: AgentState) -> AgentState:
    """Generate a natural-language answer from SQL results and/or doc chunks."""
    logger.info("[synthesize_answer] Building answer…")

    question    = state.get("question", "")
    sql_result  = state.get("sql_result")
    doc_chunks  = state.get("doc_chunks", [])
    route       = state.get("route", "sql")

    # ── Build context string ────────────────────────────────────────────────
    context_parts = []

    if sql_result and sql_result.get("rows"):
        rows = sql_result["rows"]
        # Pretty-print up to 20 rows as JSON
        rows_str = json.dumps(rows[:20], indent=2, default=str)
        context_parts.append(f"SQL Query Results ({sql_result.get('row_count', len(rows))} rows):\n{rows_str}")
    elif sql_result and sql_result.get("note"):
        context_parts.append(f"SQL Result: {sql_result['note']}")
    elif sql_result and sql_result.get("error"):
        context_parts.append(f"SQL Error: {sql_result['error']}")

    if doc_chunks:
        chunks_text = "\n\n".join(
            f"[Source: {c.get('source','?')} | Score: {c.get('similarity', 0):.2f}]\n{c.get('text','')}"
            for c in doc_chunks[:4]
        )
        context_parts.append(f"Relevant Document Excerpts:\n{chunks_text}")

    if not context_parts:
        return {
            **state,
            "final_answer": "I couldn't find any relevant data to answer your question.",
        }

    context = "\n\n---\n\n".join(context_parts)
    user_message = f"Question: {question}\n\nData:\n{context}\n\nPlease write a clear answer."

    # ── Call Groq ───────────────────────────────────────────────────────────
    api_key = os.getenv("GROQ_API_KEY")
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        max_tokens=512,
        temperature=0.3,
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    response = llm.invoke(messages)
    answer = response.content.strip()

    logger.info("[synthesize_answer] Answer (%d chars): %s…", len(answer), answer[:100])
    return {**state, "final_answer": answer}
