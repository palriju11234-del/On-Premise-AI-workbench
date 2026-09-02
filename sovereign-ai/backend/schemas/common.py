"""
Shared Pydantic models used across all API responses.
"""

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard envelope for every successful API response."""

    success: bool = True
    data: T
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ErrorDetail(BaseModel):
    """Structured error information."""

    type: str
    message: str
    detail: str | None = None
    request_id: str | None = None


class ErrorResponse(BaseModel):
    """Standard envelope for error responses."""

    success: bool = False
    error: ErrorDetail


class StatusMessage(BaseModel):
    """Simple status payload for placeholder endpoints."""

    status: str
    message: str
    phase: str | None = None
