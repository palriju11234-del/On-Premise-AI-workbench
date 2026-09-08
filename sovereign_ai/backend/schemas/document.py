"""
Pydantic models for document processing and intelligence.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Detected document type."""
    PDF = "PDF"
    SCANNED_PDF = "SCANNED_PDF"
    IMAGE = "IMAGE"
    UNKNOWN = "UNKNOWN"


class PageContent(BaseModel):
    """Extracted content from a single page."""
    page: int
    text: str


class DocumentMetadata(BaseModel):
    """Summary metadata for a processed document."""
    document_id: str
    filename: str
    document_type: DocumentType
    page_count: int
    ocr_used: bool
    classification: str  # GENERAL / INTERNAL / CONFIDENTIAL
    file_size_bytes: int
    upload_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class DocumentResult(BaseModel):
    """Full result returned after document processing."""
    metadata: DocumentMetadata
    extracted_text: str
    pages: list[PageContent]
    classification_score: int = 0
    classification_keywords: list[str] = []


class DocumentListItem(BaseModel):
    """Compact item for the document list endpoint."""
    document_id: str
    filename: str
    document_type: DocumentType
    page_count: int
    ocr_used: bool
    classification: str
    file_size_bytes: int
    upload_timestamp: datetime
