"""
backend/agent/db.py
====================
DuckDB helper — connection, data loading, schema introspection, query execution.
All other modules import from here; this is the single source of truth for DB access.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import duckdb

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parents[2]   # …/data-analyst-agent/
DB_PATH       = str(_PROJECT_ROOT / "data" / "analytics.duckdb")
CSV_PATH      = str(_PROJECT_ROOT / "data" / "sample_orders.csv")


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def get_db_connection() -> duckdb.DuckDBPyConnection:
    """Return a persistent DuckDB connection to the local file database."""
    return duckdb.connect(DB_PATH)


# ---------------------------------------------------------------------------
# Data loading (idempotent)
# ---------------------------------------------------------------------------

def load_sample_data() -> None:
    """
    Load sample_orders.csv into DuckDB as the 'orders' table.
    Safe to call multiple times — drops and recreates the table.
    """
    if not Path(CSV_PATH).exists():
        raise FileNotFoundError(f"Sample CSV not found: {CSV_PATH}")

    con = get_db_connection()
    con.execute("DROP TABLE IF EXISTS orders")
    con.execute(f"""
        CREATE TABLE orders AS
        SELECT * FROM read_csv_auto('{CSV_PATH}', header=True)
    """)
    row_count = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    con.close()
    logger.info("[DB] Loaded %d rows into 'orders' table at %s", row_count, DB_PATH)


# ---------------------------------------------------------------------------
# Schema introspection
# ---------------------------------------------------------------------------

def get_schema() -> str:
    """
    Return a human-readable schema string for all tables in the database.
    This string is injected into LLM prompts so the model knows what to query.

    Example output:
        Table: orders
          - order_id    : INTEGER
          - product     : VARCHAR
          - category    : VARCHAR
          - region      : VARCHAR
          - sale_date   : DATE
          - amount      : DOUBLE
    """
    con = get_db_connection()
    tables = con.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
    ).fetchall()

    lines = []
    for (table_name,) in tables:
        lines.append(f"Table: {table_name}")
        columns = con.execute(f"PRAGMA table_info('{table_name}')").fetchall()
        for col in columns:
            # col: (cid, name, type, notnull, default_value, pk)
            lines.append(f"  - {col[1]:<20}: {col[2]}")
        lines.append("")  # blank line between tables

    con.close()
    return "\n".join(lines).strip()


# ---------------------------------------------------------------------------
# Query execution
# ---------------------------------------------------------------------------

def run_query(sql: str) -> list[dict[str, Any]]:
    """
    Execute a SQL query and return results as a list of dicts.
    Returns an empty list (with a note) if the query returns no rows.
    """
    con = get_db_connection()
    try:
        result = con.execute(sql)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        con.close()

        if not rows:
            return []

        return [dict(zip(columns, row)) for row in rows]

    except Exception:
        con.close()
        raise


def validate_query(sql: str) -> None:
    """
    Run EXPLAIN on the SQL to catch syntax/semantic errors without executing.
    Raises duckdb.Error on invalid SQL.
    """
    con = get_db_connection()
    try:
        con.execute(f"EXPLAIN {sql}")
    finally:
        con.close()


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    load_sample_data()
    print("\n=== DB SCHEMA ===")
    print(get_schema())
    print("\n=== SAMPLE QUERY ===")
    rows = run_query(
        "SELECT category, ROUND(SUM(amount),2) AS total "
        "FROM orders GROUP BY category ORDER BY total DESC"
    )
    for r in rows:
        print(r)
