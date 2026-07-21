"""
backend/agent/ingest.py
========================
RAG ingestion pipeline:
  document file → text extraction → chunking → embeddings → ChromaDB

CLI usage:
    python backend/agent/ingest.py path/to/document.pdf
    python backend/agent/ingest.py path/to/document.txt

The sentence-transformers model (all-MiniLM-L6-v2) is downloaded on first run
and cached in ~/.cache/huggingface/. Subsequent runs use the cache.
"""
from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------

_PROJECT_ROOT  = Path(__file__).resolve().parents[2]
CHROMA_PATH    = str(_PROJECT_ROOT / "data" / "chroma_db")
COLLECTION_NAME = "documents"

CHUNK_SIZE    = 500    # characters (approx 100-125 tokens for English)
CHUNK_OVERLAP = 50
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# ---------------------------------------------------------------------------
# Singleton embedding model (loaded once per process)
# ---------------------------------------------------------------------------

_embedding_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> Any:
    """Return the sentence-transformers model (lazy-loaded, cached)."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("[ingest] Loading embedding model '%s'…", EMBEDDING_MODEL_NAME)
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info("[ingest] Embedding model loaded.")
    return _embedding_model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return embeddings for a list of text strings."""
    model = get_embedding_model()
    return model.encode(texts, show_progress_bar=False).tolist()


# ---------------------------------------------------------------------------
# ChromaDB collection
# ---------------------------------------------------------------------------

def get_chroma_collection() -> Any:
    """Return (or create) the persistent ChromaDB collection."""
    import chromadb
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},   # cosine similarity
    )


# ---------------------------------------------------------------------------
# Document loading
# ---------------------------------------------------------------------------

def load_document(file_path: str) -> str:
    """
    Load text from a .pdf or .txt file.
    Returns the full text as a single string.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(pages)
        logger.info("[ingest] Loaded PDF '%s' (%d pages)", path.name, len(pages))

    elif suffix in (".txt", ".md"):
        text = path.read_text(encoding="utf-8")
        logger.info("[ingest] Loaded text file '%s' (%d chars)", path.name, len(text))

    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use .pdf or .txt")

    return text


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, source_name: str) -> list[dict]:
    """
    Split text into overlapping chunks.
    Returns list of dicts: {"text": ..., "source": ..., "chunk_index": ...}
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    logger.info("[ingest] Split '%s' into %d chunks", source_name, len(chunks))

    return [
        {"text": chunk, "source": source_name, "chunk_index": i}
        for i, chunk in enumerate(chunks)
    ]


# ---------------------------------------------------------------------------
# Full ingestion pipeline
# ---------------------------------------------------------------------------

def ingest_file(file_path: str) -> int:
    """
    Full pipeline: load → chunk → embed → store in ChromaDB.
    Returns the number of chunks stored.
    Existing chunks from the same source are replaced.
    """
    path = Path(file_path)
    source_name = path.name

    # Step 1 — load
    text = load_document(file_path)

    # Step 2 — chunk
    chunk_dicts = chunk_text(text, source_name)
    if not chunk_dicts:
        logger.warning("[ingest] No chunks produced for '%s'", source_name)
        return 0

    texts    = [c["text"]        for c in chunk_dicts]
    sources  = [c["source"]      for c in chunk_dicts]
    indices  = [c["chunk_index"] for c in chunk_dicts]

    # Step 3 — embed
    logger.info("[ingest] Embedding %d chunks…", len(texts))
    embeddings = embed_texts(texts)

    # Step 4 — store in ChromaDB
    collection = get_chroma_collection()

    # Remove existing chunks from this source (idempotent re-ingestion)
    existing = collection.get(where={"source": source_name})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])
        logger.info(
            "[ingest] Removed %d existing chunks for '%s'",
            len(existing["ids"]), source_name,
        )

    ids       = [f"{source_name}__chunk_{i}" for i in indices]
    metadatas = [{"source": s, "chunk_index": idx} for s, idx in zip(sources, indices)]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )
    logger.info(
        "[ingest] Stored %d chunks from '%s' in ChromaDB at %s",
        len(texts), source_name, CHROMA_PATH,
    )
    return len(texts)


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description="Ingest a PDF or text file into the ChromaDB vector store."
    )
    parser.add_argument("file_path", help="Path to the .pdf or .txt file to ingest")
    args = parser.parse_args()

    count = ingest_file(args.file_path)
    print(f"\n✅ Ingested {count} chunks from '{args.file_path}'")
