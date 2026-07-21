"""
Centralized configuration for LuminAI Data Analyst backend.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------------------------
# Project paths
# ----------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = str(DATA_DIR / "analytics.duckdb")

CHROMA_PATH = str(DATA_DIR / "chroma_db")
COLLECTION_NAME = "documents"

# ----------------------------------------------------------
# Embedding
# ----------------------------------------------------------

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "all-MiniLM-L6-v2"
)

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# ----------------------------------------------------------
# LLM
# ----------------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "llama-3.3-70b-versatile"
)

TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# ----------------------------------------------------------
# Logging
# ----------------------------------------------------------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")