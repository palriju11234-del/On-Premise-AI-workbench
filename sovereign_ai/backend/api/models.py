"""
Model fabric / routing endpoints — Phase 5 placeholder.

Future implementation will provide:
  - List available models
  - Model health monitoring
  - Dynamic routing configuration
"""

from fastapi import APIRouter

from backend.exceptions import NotImplementedError_

router = APIRouter(prefix="/models", tags=["models"])


@router.get(
    "",
    summary="List available models (not implemented)",
    description="Phase 5: Model Fabric / Router.",
)
async def list_models():
    raise NotImplementedError_(
        "Model management is planned for Phase 5 — Model Fabric / Router."
    )
