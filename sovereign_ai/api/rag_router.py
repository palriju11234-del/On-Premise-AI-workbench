from fastapi import APIRouter, Depends
from sovereign_ai.core.security import get_current_user
from sovereign_ai.schemas.security import UserContext
from sovereign_ai.schemas.rag import (
    IngestDocumentRequest,
    IngestDocumentResponse,
    QueryRequest,
    QueryResponse,
)
from sovereign_ai.services.rag_service import RAGService

router = APIRouter(prefix="/api/v1/rag", tags=["Sovereign RAG Engine"])


@router.post("/ingest", response_model=IngestDocumentResponse)
def ingest_document(
    payload: IngestDocumentRequest,
    user: UserContext = Depends(get_current_user),
):
    """Ingests and indexes document text with security classification tags."""
    return RAGService.ingest_document(payload)


@router.post("/query", response_model=QueryResponse)
def query_knowledge(
    payload: QueryRequest,
    user: UserContext = Depends(get_current_user),
):
    """Performs role-filtered semantic retrieval."""
    return RAGService.retrieve(
        query=payload.query,
        user_role=user.role,
        top_k=payload.top_k,
    )