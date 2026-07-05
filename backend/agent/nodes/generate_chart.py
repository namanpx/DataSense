"""
Node: generate_chart  (Week 3 — real implementation)
======================================================
Inspects state["sql_result"] and automatically selects + builds a Plotly figure.

Chart type selection logic:
- 2 columns, 2nd is numeric        → bar chart
- 1st col is date/month, 2nd numeric → line chart  (time series)
- Otherwise                         → bar chart fallback
- RAG-only results (no sql_result)  → no chart (chart_data = None)
"""
from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

from backend.agent.state import AgentState

logger = logging.getLogger(__name__)


def _is_numeric(val: Any) -> bool:
    return isinstance(val, (int, float)) and not isinstance(val, bool)


def _is_date_like(val: Any) -> bool:
    return isinstance(val, (date, datetime)) or (
        isinstance(val, str) and len(val) >= 7 and val[:4].isdigit()
    )


def generate_chart(state: AgentState) -> AgentState:
    """Build a Plotly-compatible figure dict from SQL results, or None if not applicable."""
    logger.info("[generate_chart] Deciding chart type…")

    sql_result = state.get("sql_result")

    # No SQL data → no chart (RAG-only path)
    if not sql_result or not sql_result.get("rows"):
        logger.info("[generate_chart] No SQL rows — skipping chart.")
        return {**state, "chart_data": None}

    rows    = sql_result["rows"]
    columns = list(rows[0].keys())

    if len(columns) < 2:
        logger.info("[generate_chart] Only 1 column — skipping chart.")
        return {**state, "chart_data": None}

    x_col = columns[0]
    y_col = columns[1]

    x_vals = [str(r[x_col]) for r in rows]
    y_vals = [r[y_col] for r in rows]

    # Check if y values are numeric
    if not all(_is_numeric(v) for v in y_vals if v is not None):
        logger.info("[generate_chart] Y column not numeric — skipping chart.")
        return {**state, "chart_data": None}

    # Decide chart type
    first_x = rows[0][x_col]
    chart_type = "line" if _is_date_like(first_x) else "bar"

    logger.info(
        "[generate_chart] Type=%s | x=%s | y=%s | %d points",
        chart_type, x_col, y_col, len(rows),
    )

    # Build Plotly figure dict
    if chart_type == "line":
        trace = {
            "type": "scatter",
            "mode": "lines+markers",
            "x": x_vals,
            "y": y_vals,
            "name": y_col,
            "line": {"color": "#6366f1", "width": 2},
            "marker": {"color": "#6366f1", "size": 6},
        }
    else:
        # Bar chart with gradient colours
        colors = [
            "#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd",
            "#818cf8", "#4f46e5", "#7c3aed", "#9333ea",
        ]
        bar_colors = [colors[i % len(colors)] for i in range(len(x_vals))]
        trace = {
            "type": "bar",
            "x": x_vals,
            "y": y_vals,
            "name": y_col,
            "marker": {"color": bar_colors},
        }

    figure = {
        "data": [trace],
        "layout": {
            "title": {
                "text": f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
                "font": {"size": 16},
            },
            "xaxis": {"title": x_col.replace("_", " ").title(), "tickangle": -30},
            "yaxis": {"title": y_col.replace("_", " ").title()},
            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "margin": {"l": 60, "r": 20, "t": 60, "b": 80},
        },
    }

    return {**state, "chart_data": figure}
