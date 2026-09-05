from fastapi import APIRouter, Depends
from sovereign_ai.core.security import get_current_user
from sovereign_ai.schemas.security import UserContext
from sovereign_ai.schemas.agent import AgentTaskRequest, AgentTaskResponse
from sovereign_ai.core.agent import SovereignAgent

router = APIRouter(prefix="/api/v1/agent", tags=["Agentic Workflows"])
agent = SovereignAgent()


@router.post("/execute", response_model=AgentTaskResponse)
def execute_agent_task(
    payload: AgentTaskRequest,
    user: UserContext = Depends(get_current_user),
):
    """Executes a sovereign multi-step agent reasoning workflow with audit trail."""
    result = agent.run(
        task=payload.task,
        document_text=payload.document_text,
        filename=payload.filename or "inspection_report.pdf",
        user_role=user.role,
        image=payload.image,
    )

    return AgentTaskResponse(
        status="completed",
        answer=result["answer"],
        security=result["security"],
        model=result["model"],
        verification=result["verification"],
        human_required=result["human_required"],
        events=result["events"],
        retrieved_sources=result["retrieved_sources"],
        audit_record=result["audit_record"],
    )