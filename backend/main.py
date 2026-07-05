"""
FastAPI entrypoint — AI Data Analyst Agent backend
===================================================
Run with:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import logging
import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from backend.agent.graph import agent_graph
from backend.agent.state import AgentState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Data Analyst Agent",
    description=(
        "A LangGraph-powered agent that answers natural-language questions "
        "by routing between SQL (DuckDB) and document retrieval (ChromaDB)."
    ),
    version="0.2.0-real-pipelines",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class AskRequest(BaseModel):
    question: str
    route: str = ""   # optional override; if empty the graph will classify


class AskResponse(BaseModel):
    question: str
    route: str
    sql_query: str
    sql_result: Any
    doc_chunks: list
    final_answer: str
    chart_data: Any
    error: Any


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "version": app.version}


@app.post("/ask", response_model=AskResponse, tags=["agent"])
def ask(request: AskRequest):
    """
    Run the agent graph on the given question and return the full final state.
    """
    logger.info("POST /ask — question: %r", request.question)

    initial_state: AgentState = {
        "question": request.question,
        "route": request.route,
        "retry_count": 0,
        "sql_query": "",
        "sql_result": None,
        "doc_chunks": [],
        "final_answer": "",
        "chart_data": None,
        "error": None,
    }

    try:
        final_state = agent_graph.invoke(initial_state)
    except Exception as exc:
        logger.exception("Graph execution failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AskResponse(**final_state)
