"""
FastAPI entrypoint — AI Data Analyst Agent backend
===================================================
Run with:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import logging
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from backend.agent.db import get_db_connection
from backend.agent.graph import agent_graph
from backend.agent.ingest import get_chroma_collection, ingest_file
from backend.agent.load_csv import load_csv_into_duckdb
from backend.agent.state import AgentState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 20 * 1024 * 1024

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
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_origin_regex=(
        r"http://(localhost|127\.0\.0\.1)(:[0-9]+)?"
        r"|https://.*\.vercel\.app"
        r"|https://datasense.*"
    ),
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


class ColumnInfo(BaseModel):
    name: str
    type: str


class UploadStructuredResponse(BaseModel):
    table_name: str
    row_count: int
    columns: list[ColumnInfo]


class UploadDocumentResponse(BaseModel):
    source: str
    chunks_ingested: int


class SourcesResponse(BaseModel):
    tables: list[str]
    documents: list[str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sanitize_filename(filename: str) -> str:
    """Strip path components and unsafe characters from an uploaded filename."""
    name = Path(filename).name
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    return name or "document.txt"


async def _read_upload_with_limit(file: UploadFile) -> bytes:
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {MAX_UPLOAD_BYTES // (1024 * 1024)}MB limit",
        )
    return content


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


@app.post(
    "/upload/structured",
    response_model=UploadStructuredResponse,
    tags=["upload"],
)
async def upload_structured(file: UploadFile = File(...)):
    """Upload a CSV file and load it as a new DuckDB table."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a .csv")

    content = await _read_upload_with_limit(file)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = load_csv_into_duckdb(tmp_path, file.filename)
    except Exception as exc:
        logger.exception("Failed to load CSV into DuckDB")
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    logger.info(
        "Loaded CSV %r → table %r (%d rows)",
        file.filename,
        result["table_name"],
        result["row_count"],
    )
    return UploadStructuredResponse(**result)


@app.post(
    "/upload/document",
    response_model=UploadDocumentResponse,
    tags=["upload"],
)
async def upload_document(file: UploadFile = File(...)):
    """Upload a text/markdown/PDF document and ingest it into ChromaDB."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".txt", ".md", ".pdf"):
        raise HTTPException(
            status_code=400,
            detail="File must be a .txt, .md, or .pdf",
        )

    content = await _read_upload_with_limit(file)
    safe_name = _sanitize_filename(file.filename)

    tmp_dir = tempfile.mkdtemp()
    doc_path = os.path.join(tmp_dir, safe_name)

    try:
        with open(doc_path, "wb") as f:
            f.write(content)
        chunks_ingested = ingest_file(doc_path)
    except Exception as exc:
        logger.exception("Failed to ingest document")
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    logger.info(
        "Ingested document %r → %d chunks",
        safe_name,
        chunks_ingested,
    )
    return UploadDocumentResponse(
        source=safe_name,
        chunks_ingested=chunks_ingested,
    )


@app.get("/sources", response_model=SourcesResponse, tags=["upload"])
def list_sources():
    """Return currently loaded DuckDB tables and ingested document sources."""
    con = get_db_connection()
    try:
        tables = [
            row[0]
            for row in con.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='main' ORDER BY table_name"
            ).fetchall()
        ]
    finally:
        con.close()

    collection = get_chroma_collection()
    all_data = collection.get(include=["metadatas"])
    documents = sorted(
        {
            meta["source"]
            for meta in (all_data.get("metadatas") or [])
            if meta and "source" in meta
        }
    )

    return SourcesResponse(tables=tables, documents=documents)
