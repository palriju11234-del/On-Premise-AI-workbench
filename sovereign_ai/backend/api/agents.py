"""
Agent runtime endpoints — Phase 6 placeholder.

Future implementation will provide:
  - Task submission
  - Agent execution status
  - Multi-step agent orchestration
"""

from fastapi import APIRouter

from backend.exceptions import NotImplementedError_

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post(
    "/execute",
    summary="Execute agent task (not implemented)",
    description="Phase 6: Agent Runtime.",
)
async def execute_task():
    raise NotImplementedError_(
        "Agent execution is planned for Phase 6 — Agent Runtime."
    )


@router.get(
    "/status/{task_id}",
    summary="Get task status (not implemented)",
    description="Phase 6: Agent Runtime.",
)
async def get_task_status(task_id: str):
    raise NotImplementedError_(
        "Agent status tracking is planned for Phase 6 — Agent Runtime."
    )
