"""
backend/test_sql_pipeline.py
==============================
Tests the SQL half of the pipeline end-to-end:
  parse_and_route → generate_sql → validate_sql → execute_sql

Run from project root:
    PYTHONPATH=. .venv/bin/python backend/test_sql_pipeline.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.agent.db import load_sample_data, get_schema
from backend.agent.nodes.parse_and_route import parse_and_route
from backend.agent.nodes.generate_sql import generate_sql
from backend.agent.nodes.validate_sql import validate_sql
from backend.agent.nodes.execute_sql import execute_sql
from backend.agent.state import AgentState


# ---------------------------------------------------------------------------
# Test questions
# ---------------------------------------------------------------------------

TEST_QUESTIONS = [
    "What is the total revenue by category?",
    "Which region had the highest total sales in Q1 2024?",
    "List the top 3 products by revenue in the Electronics category",
    "Show the monthly revenue trend across all months",
    # Q5: deliberately references a non-existent column to force a retry
    "What is the total zxqpfoo_metric grouped by blarg_dimension?",
]

MAX_RETRIES = 3


# ---------------------------------------------------------------------------
# Helper: run through nodes with retry loop
# ---------------------------------------------------------------------------

def run_sql_pipeline(question: str) -> AgentState:
    """Run parse → generate → validate (with retries) → execute for one question."""
    state: AgentState = {
        "question": question,
        "route": "",
        "retry_count": 0,
        "sql_query": "",
        "sql_result": None,
        "doc_chunks": [],
        "final_answer": "",
        "chart_data": None,
        "error": None,
    }

    # Step 1 — Route
    state = parse_and_route(state)

    # Step 2 — SQL generation + validation loop
    retry_attempts = []
    for attempt in range(MAX_RETRIES + 1):
        state = generate_sql(state)
        state = validate_sql(state)

        if state.get("error"):
            retry_attempts.append({
                "attempt": attempt + 1,
                "sql": state.get("sql_query"),
                "error": state.get("error"),
            })
            if attempt < MAX_RETRIES:
                logger.info(
                    "[test] Validation failed — retrying (%d/%d)…",
                    attempt + 1, MAX_RETRIES,
                )
                continue
            else:
                logger.warning("[test] Max retries reached — proceeding to execute anyway.")
                break
        else:
            break   # validation passed

    # Step 3 — Execute
    state = execute_sql(state)
    state["_retry_history"] = retry_attempts   # attach for printing (not in AgentState schema, just for test)
    return state


# ---------------------------------------------------------------------------
# Main test runner
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 70)
    print("LOADING SAMPLE DATA INTO DUCKDB")
    print("=" * 70)
    load_sample_data()
    print("\n--- SCHEMA ---")
    print(get_schema())

    for i, question in enumerate(TEST_QUESTIONS, 1):
        print("\n" + "=" * 70)
        print(f"TEST {i}/5: {question}")
        print("=" * 70)

        state = run_sql_pipeline(question)

        print(f"\n  Route      : {state.get('route')}")
        print(f"  SQL Query  : {state.get('sql_query', '').strip()}")
        print(f"  Retries    : {state.get('retry_count', 0) - 1}")  # subtract the first successful attempt

        retry_history = state.get("_retry_history", [])
        if retry_history:
            print("\n  ── Retry History ──")
            for r in retry_history:
                print(f"    Attempt {r['attempt']}: {r['error'][:120]}")

        sql_result = state.get("sql_result")
        if sql_result:
            rows = sql_result.get("rows", [])
            if rows:
                print(f"\n  Result ({sql_result.get('row_count')} rows):")
                for row in rows[:5]:   # show max 5 rows
                    print(f"    {row}")
                if len(rows) > 5:
                    print(f"    … and {len(rows) - 5} more rows")
            else:
                print(f"\n  Result : {sql_result.get('note') or sql_result.get('error', 'empty')}")
        else:
            print("\n  Result : None")

        if state.get("error"):
            print(f"\n  ⚠ Final Error: {state['error']}")

    print("\n" + "=" * 70)
    print("SQL PIPELINE TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
