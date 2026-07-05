"""
Node: execute_sql  (Week 2 — real implementation)
==================================================
Runs the validated SQL against DuckDB and stores results as a list of dicts
in state["sql_result"].
"""
from __future__ import annotations

import logging

from backend.agent.state import AgentState
from backend.agent.db import run_query

logger = logging.getLogger(__name__)


def execute_sql(state: AgentState) -> AgentState:
    """Execute the validated SQL and store results in state['sql_result']."""
    sql_query = state.get("sql_query", "")
    logger.info("[execute_sql] Running:\n%s", sql_query)

    # If we've exhausted retries with an error, return a clean failure state
    if state.get("error") and state.get("retry_count", 0) >= 3:
        logger.error("[execute_sql] Max retries reached — skipping execution.")
        return {
            **state,
            "sql_result": {
                "rows": [],
                "error": state["error"],
                "note": "SQL validation failed after max retries.",
            },
        }

    try:
        rows = run_query(sql_query)

        if not rows:
            logger.info("[execute_sql] Query returned 0 rows.")
            result = {
                "rows": [],
                "row_count": 0,
                "note": "Query executed successfully but returned no rows.",
            }
        else:
            logger.info("[execute_sql] Got %d rows. First row: %s", len(rows), rows[0])
            result = {
                "rows": rows,
                "row_count": len(rows),
                "columns": list(rows[0].keys()),
            }

        return {**state, "sql_result": result, "error": None}

    except Exception as exc:
        error_msg = str(exc)
        logger.error("[execute_sql] Execution failed: %s", error_msg)
        return {
            **state,
            "sql_result": {"rows": [], "error": error_msg},
            "error": error_msg,
        }
