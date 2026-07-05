"""
Node: retrieve_docs  (Week 2 — real implementation)
====================================================
Embeds the user question and queries ChromaDB for the top-k most similar
document chunks. Stores results in state["doc_chunks"].
"""
from __future__ import annotations

import logging

from backend.agent.state import AgentState
from backend.agent.ingest import embed_texts, get_chroma_collection

logger = logging.getLogger(__name__)

TOP_K = 4


def retrieve_docs(state: AgentState) -> AgentState:
    """Retrieve the top-k most relevant document chunks for the question."""
    question = state.get("question", "")
    logger.info("[retrieve_docs] Question: %r", question)

    # Embed the question (same model as ingestion — critical for quality)
    q_embedding = embed_texts([question])[0]

    # Query ChromaDB
    collection = get_chroma_collection()
    total_docs = collection.count()
    logger.info("[retrieve_docs] ChromaDB collection has %d chunks total", total_docs)

    if total_docs == 0:
        logger.warning(
            "[retrieve_docs] Collection is empty! "
            "Run: python backend/agent/ingest.py data/sample_report.txt"
        )
        return {**state, "doc_chunks": []}

    n_results = min(TOP_K, total_docs)
    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    docs       = results["documents"][0]
    metadatas  = results["metadatas"][0]
    distances  = results["distances"][0]

    for doc, meta, dist in zip(docs, metadatas, distances):
        # ChromaDB cosine distance: 0 = identical, 2 = opposite
        # Convert to similarity score: 1 - (dist/2), range [0, 1]
        similarity = round(1.0 - dist / 2.0, 4)

        chunk = {
            "text": doc,
            "source": meta.get("source", "unknown"),
            "chunk_index": meta.get("chunk_index", -1),
            "similarity": similarity,
        }
        chunks.append(chunk)

        logger.info(
            "[retrieve_docs] Chunk %d | score=%.4f | source=%s | preview: %r…",
            meta.get("chunk_index", -1),
            similarity,
            meta.get("source", "?"),
            doc[:80],
        )

    logger.info("[retrieve_docs] Retrieved %d chunks", len(chunks))
    return {**state, "doc_chunks": chunks}
