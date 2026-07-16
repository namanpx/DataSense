"""
Custom exceptions for LuminAI Data Analyst.
"""


class DataSenseError(Exception):
    """Base exception for the project."""
    pass


class DatabaseConnectionError(DataSenseError):
    """Raised when database connection fails."""
    pass


class SQLExecutionError(DataSenseError):
    """Raised when SQL execution fails."""
    pass


class SQLValidationError(DataSenseError):
    """Raised when SQL validation fails."""
    pass


class VectorStoreError(DataSenseError):
    """Raised for ChromaDB errors."""
    pass


class EmbeddingError(DataSenseError):
    """Raised when embedding generation fails."""
    pass


class LLMError(DataSenseError):
    """Raised when LLM invocation fails."""
    pass


class ConfigurationError(DataSenseError):
    """Raised when configuration is invalid."""
    pass