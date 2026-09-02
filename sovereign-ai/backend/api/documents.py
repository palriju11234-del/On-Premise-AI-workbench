"""
Document processing endpoints — Phase 3 placeholder.

Future implementation will provide:
  - Document upload and parsing
  - OCR processing
  - Multi-format ingestion
"""

from fastapi import APIRouter

from backend.exceptions import NotImplementedError_

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get(
    "",
    summary="List documents (not implemented)",
    description="Phase 3: Document Intelligence.",
)
async def list_documents():
    raise NotImplementedError_(
        "Document management is planned for Phase 3 — Document Intelligence."
    )


@router.post(
    "/upload",
    summary="Upload document (not implemented)",
    description="Phase 3: Document Intelligence.",
)
async def upload_document():
    raise NotImplementedError_(
        "Document upload is planned for Phase 3 — Document Intelligence."
    )
