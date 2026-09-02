"""
Health check endpoint.

GET /api/v1/health — returns component-level system status.
"""

from fastapi import APIRouter

from backend.schemas.common import ApiResponse
from backend.schemas.health import HealthResponse
from backend.services.health import HealthService

router = APIRouter(tags=["health"])

_health_service = HealthService()


@router.get(
    "/health",
    response_model=ApiResponse[HealthResponse],
    summary="System health check",
    description=(
        "Returns the health status of all infrastructure components: "
        "Ollama LLM, ChromaDB vector store, and disk space."
    ),
)
async def health_check():
    """Probe all infrastructure components and return aggregate status."""
    report = await _health_service.full_check()
    return ApiResponse(data=report)
