"""
backend/agent/load_csv.py
=========================
Generic CSV → DuckDB loader. Infers schema from the uploaded file.
"""
from __future__ import annotations

import re
from pathlib import Path

import duckdb
import pandas as pd

from backend.core.config import DB_PATH

_TABLE_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _sanitize_table_name(filename: str) -> str:
    """Derive a safe DuckDB table name from an uploaded filename."""
    base = Path(filename).stem.lower()
    sanitized = re.sub(r"[^a-z0-9_]", "_", base)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    if not sanitized or not sanitized[0].isalpha():
        sanitized = f"table_{sanitized}" if sanitized else "uploaded_table"
    return sanitized


def _unique_table_name(con: duckdb.DuckDBPyConnection, base_name: str) -> str:
    """Return base_name or base_name_N if the table already exists."""
    existing = {
        row[0]
        for row in con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
        ).fetchall()
    }
    if base_name not in existing:
        return base_name
    suffix = 2
    while f"{base_name}_{suffix}" in existing:
        suffix += 1
    return f"{base_name}_{suffix}"


def _read_csv_with_fallback(path: str) -> pd.DataFrame:
    """Try UTF-8 first, then fall back to latin-1 / cp1252 for Excel exports."""
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(
        "Could not decode CSV file. Supported encodings: utf-8, latin-1, cp1252."
    )


def load_csv_into_duckdb(csv_path: str, original_filename: str) -> dict:

    """
    Load a CSV file into DuckDB, inferring column types automatically.

    Returns:
        {table_name, row_count, columns: [{name, type}]}
    """
    table_base = _sanitize_table_name(original_filename)
    if not _TABLE_NAME_RE.match(table_base):
        raise ValueError(f"Invalid table name derived from filename: {table_base!r}")

    df = _read_csv_with_fallback(csv_path)

    con = duckdb.connect(DB_PATH)
    try:
        table_name = _unique_table_name(con, table_base)
        if not _TABLE_NAME_RE.match(table_name):
            raise ValueError(f"Invalid table name: {table_name!r}")

        con.register("df_upload", df)
        con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df_upload")
        con.unregister("df_upload")

        row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        columns_raw = con.execute(f"PRAGMA table_info('{table_name}')").fetchall()
        columns = [{"name": col[1], "type": col[2]} for col in columns_raw]
    finally:
        con.close()

    return {
        "table_name": table_name,
        "row_count": row_count,
        "columns": columns,
    }
