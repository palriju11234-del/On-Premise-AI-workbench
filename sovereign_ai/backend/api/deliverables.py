"""
Deliverable generation endpoints — Phase 9 placeholder.

Future implementation will provide:
  - DOCX / PDF report generation
  - Template management
  - Download endpoints
"""

from fastapi import APIRouter

from backend.exceptions import NotImplementedError_

router = APIRouter(prefix="/deliverables", tags=["deliverables"])


@router.post(
    "/generate",
    summary="Generate deliverable document (not implemented)",
    description="Phase 9: Deliverables.",
)
async def generate_deliverable():
    raise NotImplementedError_(
        "Deliverable generation is planned for Phase 9 — Deliverables."
    )
