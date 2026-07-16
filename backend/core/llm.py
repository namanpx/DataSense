"""
Centralized LLM initialization.
"""

from langchain_groq import ChatGroq

from backend.core.config import (
    GROQ_API_KEY,
    MODEL_NAME,
    TEMPERATURE,
)


def get_llm():
    """
    Returns a configured ChatGroq LLM instance.
    """

    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=TEMPERATURE,
    )