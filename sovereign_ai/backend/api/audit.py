"""
Audit & Cryptographic Provenance Endpoints — Phase 8 Implementation.

Provides:
  - POST /audit/hash/calculate  — Calculate SHA-256 hash for text
  - POST /audit/hash/verify     — Verify content against an expected SHA-256 hash
  - POST /audit/provenance      — Record a new task-linked provenance record
  - GET  /audit/events          — Retrieve audit events log
  - GET  /audit/provenance/{id} — Retrieve provenance history for a specific task
"""

import logging
from typing import Optional, List

from fastapi import APIRouter, Depends

from backend.dependencies import get_current_user, require_permission
from backend.schemas.auth import UserResponse
from backend.schemas.common import ApiResponse
from backend.schemas.provenance import (
    ProvenanceRecord,
    HashCalculateTextRequest,
    HashCalculateResponse,
    HashVerifyRequest,
    HashVerifyResponse,
)
from backend.services.provenance import ProvenanceService
from backend.exceptions import SovereignError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["audit"])

_provenance_service: Optional[ProvenanceService] = None


def _get_provenance_service() -> ProvenanceService:
    global _provenance_service
    if _provenance_service is None:
        _provenance_service = ProvenanceService()
    return _provenance_service


@router.post(
    "/hash/calculate",
    summary="Calculate SHA-256 hash",
    description="Calculate deterministic hexadecimal SHA-256 hash for raw text content.",
    response_model=ApiResponse[HashCalculateResponse],
)
async def calculate_hash(
    req: HashCalculateTextRequest,
    user: UserResponse = Depends(get_current_user),
):
    service = _get_provenance_service()
    sha256 = service.calculate_text_hash(req.text)
    size_bytes = len(req.text.encode("utf-8"))

    return ApiResponse(
        data=HashCalculateResponse(
            sha256=sha256,
            size_bytes=size_bytes,
        )
    )


@router.post(
    "/hash/verify",
    summary="Verify artifact hash integrity",
    description="Recompute SHA-256 hash of provided content and compare against expected hash.",
    response_model=ApiResponse[HashVerifyResponse],
)
async def verify_hash(
    req: HashVerifyRequest,
    user: UserResponse = Depends(get_current_user),
):
    service = _get_provenance_service()
    if req.text_content is not None:
        actual_hash = service.calculate_text_hash(req.text_content)
    else:
        raise SovereignError("text_content must be provided for hash verification", status_code=400)

    result = service.verify_integrity(
        expected_hash=req.expected_hash,
        actual_hash=actual_hash,
    )
    return ApiResponse(data=result)


@router.post(
    "/provenance",
    summary="Record task provenance",
    description="Create and persist a task-linked cryptographic provenance record.",
    response_model=ApiResponse[ProvenanceRecord],
)
async def record_provenance(
    record: ProvenanceRecord,
    user: UserResponse = Depends(require_permission("view_audit")),
):
    service = _get_provenance_service()
    saved = service.record_provenance(record)
    return ApiResponse(data=saved)


@router.get(
    "/events",
    summary="List audit events",
    description="Retrieve all provenance and audit events (requires view_audit permission).",
    response_model=ApiResponse[List[dict]],
)
async def list_events(
    task_id: Optional[str] = None,
    user: UserResponse = Depends(require_permission("view_audit")),
):
    service = _get_provenance_service()
    events = service.get_events(task_id=task_id)
    return ApiResponse(data=events)


@router.get(
    "/provenance/{task_id}",
    summary="Get task provenance lineage",
    description="Retrieve task-linked provenance history for a specific task ID.",
    response_model=ApiResponse[List[dict]],
)
async def get_task_provenance(
    task_id: str,
    user: UserResponse = Depends(require_permission("view_audit")),
):
    service = _get_provenance_service()
    records = service.get_provenance_by_task_id(task_id)
    return ApiResponse(data=records)
