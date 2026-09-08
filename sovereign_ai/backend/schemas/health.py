"""
Pydantic models for the ``/api/v1/health`` endpoint.
"""

from pydantic import BaseModel
from typing import Literal


class ComponentStatus(BaseModel):
    """Health status of a single infrastructure component."""

    name: str
    status: Literal["healthy", "unhealthy", "unknown"]
    detail: str | None = None


class HealthResponse(BaseModel):
    """Aggregate health report returned by the health endpoint."""

    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    environment: str
    components: list[ComponentStatus]
