"""
Pydantic models for security classification and policy decisions.
"""

from pydantic import BaseModel
from enum import Enum


class SecurityClassification(str, Enum):
    """Data sensitivity levels."""
    GENERAL = "GENERAL"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"


class PolicyDecision(str, Enum):
    """Actions the policy engine can take on data."""
    ALLOW = "ALLOW"
    MASK = "MASK"
    TOKENIZE = "TOKENIZE"
    RESTRICT = "RESTRICT"


class ClassificationResult(BaseModel):
    """Result of classifying a piece of text."""
    classification: SecurityClassification
    score: int
    keywords_matched: list[str] = []


class PolicyRule(BaseModel):
    """Policy constraints for a given classification level."""
    allow_local_processing: bool
    allow_external_ai: bool
    require_human_approval: bool
    decision: PolicyDecision


class PolicyResult(BaseModel):
    """Full policy evaluation result combining classification + action context."""
    classification: SecurityClassification
    decision: PolicyDecision
    allow_local_processing: bool
    allow_external_ai: bool
    require_human_approval: bool
    reason: str


class ClassifyRequest(BaseModel):
    """Request body for the /security/classify endpoint."""
    text: str
    filename: str = "unknown"


class EvaluatePolicyRequest(BaseModel):
    """Request body for the /security/evaluate endpoint."""
    classification: SecurityClassification
    action: str
