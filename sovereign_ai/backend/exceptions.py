"""
Custom exception hierarchy and FastAPI exception handlers for the
Sovereign AI Workbench.

Every domain area gets its own exception subclass so that callers can
catch specific failures while the global handler guarantees a uniform
JSON error envelope for all unhandled cases.
"""

import logging
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# ── Base Exception ───────────────────────────────────────────────────

class SovereignError(Exception):
    """Base exception for all Sovereign AI Workbench errors."""

    def __init__(self, message: str = "An unexpected error occurred",
                 status_code: int = 500, detail: str | None = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


# ── Domain Exceptions ────────────────────────────────────────────────

class ConfigurationError(SovereignError):
    """Raised when a required configuration is missing or invalid."""

    def __init__(self, message: str = "Configuration error"):
        super().__init__(message, status_code=500)


class OllamaConnectionError(SovereignError):
    """Raised when the local Ollama instance is unreachable."""

    def __init__(self, message: str = "Ollama LLM is not reachable"):
        super().__init__(message, status_code=503)


class DocumentProcessingError(SovereignError):
    """Raised when document parsing/OCR fails."""

    def __init__(self, message: str = "Document processing failed"):
        super().__init__(message, status_code=422)


class VectorStoreError(SovereignError):
    """Raised when ChromaDB operations fail."""

    def __init__(self, message: str = "Vector store error"):
        super().__init__(message, status_code=500)


class AuthenticationError(SovereignError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401)


class AuthorisationError(SovereignError):
    """Raised when the user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403)


class NotImplementedError_(SovereignError):
    """Raised for endpoints that are planned but not yet built."""

    def __init__(self, message: str = "This feature is not yet implemented"):
        super().__init__(message, status_code=501)


# ── FastAPI Exception Handlers ───────────────────────────────────────

async def sovereign_error_handler(
    request: Request, exc: SovereignError
) -> JSONResponse:
    """
    Catch any ``SovereignError`` subclass and return a uniform JSON
    error envelope with a request-level correlation ID.
    """
    request_id = str(uuid.uuid4())
    logger.error(
        "SovereignError [%s] %s — %s",
        request_id, exc.__class__.__name__, exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "detail": exc.detail,
                "request_id": request_id,
            },
        },
    )


async def generic_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Catch-all for unexpected exceptions — logs the traceback and
    returns a safe 500 response without leaking internals.
    """
    request_id = str(uuid.uuid4())
    logger.exception(
        "Unhandled exception [%s]: %s", request_id, exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred",
                "detail": None,
                "request_id": request_id,
            },
        },
    )
