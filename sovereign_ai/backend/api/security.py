"""
Security classification and policy evaluation endpoints.

POST /security/classify  — classify text sensitivity
POST /security/evaluate  — evaluate a policy decision
"""

from fastapi import APIRouter, Depends

from backend.schemas.common import ApiResponse
from backend.schemas.security import (
    ClassifyRequest,
    EvaluatePolicyRequest,
    ClassificationResult,
    PolicyResult,
)
from backend.services.security import SecurityService
from backend.dependencies import get_current_user
from backend.schemas.auth import UserResponse

router = APIRouter(prefix="/security", tags=["security"])

_security_service: SecurityService | None = None


def _get_security() -> SecurityService:
    global _security_service
    if _security_service is None:
        _security_service = SecurityService()
    return _security_service


@router.post(
    "/classify",
    response_model=ApiResponse[ClassificationResult],
    summary="Classify text sensitivity",
    description=(
        "Analyze text for sensitive keywords and return a "
        "GENERAL / INTERNAL / CONFIDENTIAL classification."
    ),
)
async def classify_text(
    body: ClassifyRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """Classify text and return the sensitivity result."""
    svc = _get_security()
    result = svc.classify(body.text, body.filename)
    return ApiResponse(data=result)


@router.post(
    "/evaluate",
    response_model=ApiResponse[PolicyResult],
    summary="Evaluate policy decision",
    description=(
        "Given a classification level and an action, return the "
        "policy decision (ALLOW / MASK / TOKENIZE / RESTRICT)."
    ),
)
async def evaluate_policy(
    body: EvaluatePolicyRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """Evaluate a policy decision for a classification + action pair."""
    svc = _get_security()
    result = svc.evaluate_policy(body.classification, body.action)
    return ApiResponse(data=result)
