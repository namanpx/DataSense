"""
Node: validate_sql  (Week 2 — real implementation)
====================================================
Validates the generated SQL using DuckDB's EXPLAIN statement.
On failure, sets state["error"] to trigger the retry loop back to generate_sql.
"""
from __future__ import annotations

import logging

from backend.agent.state import AgentState
from backend.agent.db import validate_query

logger = logging.getLogger(__name__)


def validate_sql(state: AgentState) -> AgentState:
    """Validate SQL using EXPLAIN. Sets state['error'] on failure."""
    sql_query   = state.get("sql_query", "")
    retry_count = state.get("retry_count", 0)

    logger.info("[validate_sql] Validating (attempt %d):\n%s", retry_count, sql_query)

    if not sql_query.strip():
        error_msg = "SQL query is empty — cannot validate."
        logger.error("[validate_sql] FAIL — %s", error_msg)
        return {**state, "error": error_msg}

    try:
        validate_query(sql_query)
        logger.info("[validate_sql] PASS ✓")
        return {**state, "error": None}

    except Exception as exc:
        error_msg = str(exc)
        logger.warning("[validate_sql] FAIL ✗ — %s", error_msg)
        return {**state, "error": error_msg}
