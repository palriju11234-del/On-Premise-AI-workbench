from fastapi import APIRouter, Depends, HTTPException, status
from sovereign_ai.core.security import get_current_user
from sovereign_ai.schemas.security import UserContext
from sovereign_ai.schemas.document import DocumentParseRequest, DocumentParseResponse
from sovereign_ai.services.document_service import DocumentService

router = APIRouter(prefix="/api/v1/documents", tags=["Document Intelligence"])


@router.post("/parse", response_model=DocumentParseResponse)
def parse_document(
    payload: DocumentParseRequest,
    user: UserContext = Depends(get_current_user)
):
    """
    Parses document text, creates hash for provenance,
    and runs security classification.
    """
    if not payload.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document content cannot be empty"
        )

    return DocumentService.process_text_document(
        filename=payload.filename,
        raw_text=payload.content
    )