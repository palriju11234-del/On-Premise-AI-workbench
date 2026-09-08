"""
Document processing API endpoints — Phase 3 Document Intelligence.

Provides:
  - POST /documents/upload    — Upload and process a document
  - GET  /documents           — List all processed documents
  - GET  /documents/{id}      — Get a specific document's metadata
"""

import logging

from fastapi import APIRouter, Depends, UploadFile, File

from backend.dependencies import get_current_user, require_permission
from backend.schemas.auth import UserResponse
from backend.schemas.common import ApiResponse
from backend.schemas.document import DocumentResult, DocumentListItem
from backend.services.document import DocumentService
from backend.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

# Lazily initialised singleton
_document_service: DocumentService | None = None


def _get_document_service() -> DocumentService:
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service


@router.post(
    "/upload",
    summary="Upload and process a document",
    description=(
        "Upload a PDF, scanned PDF, or image (PNG/JPG). "
        "The document is validated, text-extracted (with OCR fallback), "
        "security-classified, and stored locally."
    ),
    response_model=ApiResponse[DocumentResult],
)
async def upload_document(
    file: UploadFile = File(...),
    user: UserResponse = Depends(require_permission("upload_documents")),
):
    service = _get_document_service()
    content = await file.read()

    logger.info(
        "Document upload: user=%s filename=%s size=%d",
        user.username, file.filename, len(content),
    )

    result = await service.process_document(
        filename=file.filename or "unknown",
        file_content=content,
    )

    return ApiResponse(data=result)


@router.get(
    "",
    summary="List all processed documents",
    description="Returns metadata for all uploaded and processed documents.",
    response_model=ApiResponse[list[DocumentListItem]],
)
async def list_documents(
    user: UserResponse = Depends(get_current_user),
):
    service = _get_document_service()
    documents = service.list_documents()
    return ApiResponse(data=documents)


@router.get(
    "/{document_id}",
    summary="Get document by ID",
    description="Returns metadata for a specific document.",
    response_model=ApiResponse[DocumentListItem],
)
async def get_document(
    document_id: str,
    user: UserResponse = Depends(get_current_user),
):
    service = _get_document_service()
    document = service.get_document(document_id)

    if document is None:
        raise DocumentProcessingError(
            f"Document '{document_id}' not found."
        )

    return ApiResponse(data=document)
