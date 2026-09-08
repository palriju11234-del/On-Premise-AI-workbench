"""
Pydantic schemas for Cryptographic Provenance and Audit trail.
"""

from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field


class ProvenanceRecord(BaseModel):
    """Structured record tracing task execution integrity and lineage."""

    task_id: str
    input_hash: Optional[str] = None
    knowledge_source_hashes: List[str] = Field(default_factory=list)
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    result_hash: Optional[str] = None
    verification_status: Optional[str] = None
    risk_level: Optional[str] = None
    approval_status: Optional[str] = None
    output_hash: Optional[str] = None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class HashCalculateTextRequest(BaseModel):
    """Payload to calculate hash for string content."""
    text: str


class HashCalculateResponse(BaseModel):
    """Calculated SHA-256 hash response."""
    sha256: str
    size_bytes: int


class HashVerifyRequest(BaseModel):
    """Payload to verify an artifact against an expected hash."""
    expected_hash: str
    text_content: Optional[str] = None
    file_id: Optional[str] = None


class HashVerifyResponse(BaseModel):
    """Verification result comparing calculated vs expected hash."""
    is_valid: bool
    expected_hash: str
    calculated_hash: str
    status: str  # "VALID" or "MODIFIED"
