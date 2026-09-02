from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AgentTaskRequest(BaseModel):
    task: str
    document_text: str
    filename: Optional[str] = "inspection_report.pdf"


class AgentTaskResponse(BaseModel):
    status: str
    answer: str
    security: Dict[str, Any]
    model: Dict[str, Any]
    verification: Dict[str, Any]
    human_required: bool
    events: List[str]
    retrieved_sources: int
    audit_record: Dict[str, Any]