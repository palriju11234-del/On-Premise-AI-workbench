from fastapi import APIRouter, Depends
from sovereign_ai.core.security import get_current_user
from sovereign_ai.schemas.security import UserContext
from sovereign_ai.schemas.model import RouteRequest, RouteDecision, InferenceResponse
from sovereign_ai.core.model_router import ModelRouter

router = APIRouter(prefix="/api/v1/models", tags=["Model Routing & Inference"])
model_router = ModelRouter()


@router.post("/route", response_model=RouteDecision)
def get_model_routing(
    payload: RouteRequest,
    user: UserContext = Depends(get_current_user),
):
    """Determines the optimal on-premise model based on task type and classification."""
    routing_info = model_router.route(
        task_type=payload.task_type,
        classification=payload.classification,
    )
    return RouteDecision(
        selected_model=routing_info["model"],
        tier=routing_info["tier"],
        temperature=routing_info["temperature"],
        external_api_allowed=routing_info["external_api_allowed"],
        classification=payload.classification,
    )


@router.post("/generate", response_model=InferenceResponse)
def execute_inference(
    payload: RouteRequest,
    user: UserContext = Depends(get_current_user),
):
    """Executes sovereign inference orchestration via routed local engine."""
    routing_info = model_router.route(
        task_type=payload.task_type,
        classification=payload.classification,
    )

    simulated_output = (
        f"[Model: {routing_info['model']} | Security: {payload.classification.value}] "
        f"Processed prompt locally without outbound network egress: '{payload.prompt[:60]}...'"
    )

    return InferenceResponse(
        status="completed",
        routing=RouteDecision(
            selected_model=routing_info["model"],
            tier=routing_info["tier"],
            temperature=routing_info["temperature"],
            external_api_allowed=routing_info["external_api_allowed"],
            classification=payload.classification,
        ),
        output=simulated_output,
    )