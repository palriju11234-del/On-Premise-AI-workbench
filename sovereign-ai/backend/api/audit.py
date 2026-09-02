"""
Audit / provenance endpoints — Phase 8 placeholder.

Future implementation will provide:
  - Audit trail queries
  - Provenance record retrieval
  - Cryptographic hash verification
"""

from fastapi import APIRouter

from backend.exceptions import NotImplementedError_

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get(
    "/events",
    summary="List audit events (not implemented)",
    description="Phase 8: Provenance / Audit / No-Egress.",
)
async def list_events():
    raise NotImplementedError_(
        "Audit trail queries are planned for Phase 8 — Provenance / Audit."
    )
