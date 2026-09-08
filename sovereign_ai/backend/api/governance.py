"""
Governance / Human-in-the-Loop endpoints — Phase 7 placeholder.

Future implementation will provide:
  - Approval workflows
  - HITL review queues
  - Decision persistence
"""

from fastapi import APIRouter

from backend.exceptions import NotImplementedError_

router = APIRouter(prefix="/governance", tags=["governance"])


@router.get(
    "/pending",
    summary="List pending approvals (not implemented)",
    description="Phase 7: Verification / HITL.",
)
async def list_pending():
    raise NotImplementedError_(
        "Governance workflows are planned for Phase 7 — Verification / HITL."
    )


@router.post(
    "/approve/{task_id}",
    summary="Approve task output (not implemented)",
    description="Phase 7: Verification / HITL.",
)
async def approve_task(task_id: str):
    raise NotImplementedError_(
        "Approval persistence is planned for Phase 7 — Verification / HITL."
    )
