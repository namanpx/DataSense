"""
backend/test_rag_pipeline.py
==============================
Tests the RAG half of the pipeline:
  ingest document → retrieve_docs node → print chunks + similarity scores

Run from project root:
    PYTHONPATH=. .venv/bin/python backend/test_rag_pipeline.py
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.agent.ingest import ingest_file, get_chroma_collection
from backend.agent.nodes.retrieve_docs import retrieve_docs
from backend.agent.state import AgentState

# ---------------------------------------------------------------------------
# Test questions
# ---------------------------------------------------------------------------

TEST_QUESTIONS = [
    "What were the top performing regions in the market?",             # should retrieve relevant chunks
    "Summarise the key market trends and strategic insights",           # broad, multiple relevant chunks
    "What products had declining sales or faced margin pressure?",      # specific, medium relevance
    "Which product category had the strongest customer retention?",     # specific — Food category
    "What is the weather forecast for Mumbai this weekend?",           # intentionally off-topic
]

REPORT_PATH = str(Path(__file__).resolve().parents[1] / "data" / "sample_report.txt")


# ---------------------------------------------------------------------------
# Main test runner
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 70)
    print("STEP 1: INGESTING DOCUMENT INTO CHROMADB")
    print("=" * 70)

    chunk_count = ingest_file(REPORT_PATH)
    print(f"\n  ✅ Ingested {chunk_count} chunks from sample_report.txt")

    collection = get_chroma_collection()
    print(f"  ChromaDB collection total: {collection.count()} chunks")

    for i, question in enumerate(TEST_QUESTIONS, 1):
        print("\n" + "=" * 70)
        print(f"TEST {i}/5: {question}")
        print("=" * 70)

        state: AgentState = {
            "question": question,
            "route": "rag",
            "retry_count": 0,
            "sql_query": "",
            "sql_result": None,
            "doc_chunks": [],
            "final_answer": "",
            "chart_data": None,
            "error": None,
        }

        state = retrieve_docs(state)

        chunks = state.get("doc_chunks", [])
        print(f"\n  Retrieved {len(chunks)} chunks:\n")

        for j, chunk in enumerate(chunks, 1):
            score = chunk.get("similarity", 0)
            relevance = (
                "🟢 HIGH" if score >= 0.5 else
                "🟡 MED"  if score >= 0.3 else
                "🔴 LOW"
            )
            print(f"  Chunk {j} | score={score:.4f} {relevance}")
            print(f"  Source: {chunk.get('source')} (chunk #{chunk.get('chunk_index')})")
            # Print first 200 chars of the chunk text
            preview = chunk.get("text", "")[:200].replace("\n", " ")
            print(f"  Preview: {preview}…")
            print()

        if not chunks:
            print("  ⚠ No chunks retrieved!")

    print("=" * 70)
    print("RAG PIPELINE TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
