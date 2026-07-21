"""
backend/seed.py
===============
Run once at startup on Render to pre-load seed CSV files into DuckDB.
Called by the start command before uvicorn.

Usage (automatically invoked by start.sh):
    python -m backend.seed
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Each entry: (csv_file_relative_to_project_root, desired_table_name)
SEED_FILES = [
    ("data/raw/superstore.csv", "superstore"),
]


def seed():
    from backend.agent.load_csv import load_csv_into_duckdb
    from backend.agent.db import get_db_connection

    project_root = Path(__file__).resolve().parents[1]

    # Check which tables already exist
    con = get_db_connection()
    try:
        existing = {
            row[0]
            for row in con.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
            ).fetchall()
        }
    finally:
        con.close()

    for rel_path, table_name in SEED_FILES:
        csv_path = project_root / rel_path
        if not csv_path.exists():
            logger.warning("[seed] Skipping %s — file not found", rel_path)
            continue

        if table_name in existing:
            logger.info("[seed] Table '%s' already exists — skipping", table_name)
            continue

        try:
            result = load_csv_into_duckdb(str(csv_path), f"{table_name}.csv")
            logger.info(
                "[seed] Loaded '%s' → table '%s' (%d rows)",
                rel_path,
                result["table_name"],
                result["row_count"],
            )
        except Exception as exc:
            logger.error("[seed] Failed to load '%s': %s", rel_path, exc)


if __name__ == "__main__":
    seed()
