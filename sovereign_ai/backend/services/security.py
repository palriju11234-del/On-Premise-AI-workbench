"""
Security classification and policy decision service.

Wraps the existing ``core.security.SecurityEngine`` with structured
Pydantic models and adds a policy decision engine supporting
ALLOW / MASK / TOKENIZE / RESTRICT actions.
"""

import logging
import sys
from pathlib import Path

from backend.schemas.security import (
    SecurityClassification,
    PolicyDecision,
    ClassificationResult,
    PolicyResult,
)

logger = logging.getLogger(__name__)

# ── Import the existing SecurityEngine from core/ ────────────────
# Add project root to sys.path so we can import the original module
# without modifying it.
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from core.security import SecurityEngine as _LegacySecurityEngine  # noqa: E402


class SecurityService:
    """Enhanced security classification and policy evaluation."""

    # Keywords used by the legacy engine (kept in sync for audit)
    SENSITIVE_KEYWORDS = [
        "confidential", "internal", "inspection", "maintenance",
        "equipment", "vendor", "plant", "refinery",
    ]

    # Actions that are considered high-risk regardless of classification
    HIGH_RISK_ACTIONS = {
        "approve_actions",
        "execute_agents",
        "manage_models",
    }

    def __init__(self):
        self._legacy = _LegacySecurityEngine()

    # ── Classification ───────────────────────────────────────────

    def classify(self, text: str, filename: str = "unknown") -> ClassificationResult:
        """
        Classify text using the existing ``SecurityEngine`` and
        return a structured result with matched keywords.
        """
        # Call the legacy engine (preserved as-is from core/security.py)
        raw = self._legacy.classify(filename, text)

        # Enrich with matched keyword list
        text_lower = text.lower()
        matched = [kw for kw in self.SENSITIVE_KEYWORDS if kw in text_lower]

        return ClassificationResult(
            classification=SecurityClassification(raw["classification"]),
            score=raw["score"],
            keywords_matched=matched,
        )

    # ── Policy Decisions ─────────────────────────────────────────

    def evaluate_policy(
        self,
        classification: SecurityClassification,
        action: str,
    ) -> PolicyResult:
        """
        Evaluate a policy decision given a classification level and
        the action being attempted.

        Rules:
        - CONFIDENTIAL data → RESTRICT external AI, require human
          approval for high-risk actions.
        - INTERNAL data → MASK sensitive fields for external use
          (but external AI is still blocked in sovereign mode).
        - GENERAL data → ALLOW, but external AI remains blocked
          (on-premise only).
        - All classifications block external AI (sovereign constraint).
        """
        if classification == SecurityClassification.CONFIDENTIAL:
            is_high_risk = action in self.HIGH_RISK_ACTIONS
            return PolicyResult(
                classification=classification,
                decision=PolicyDecision.RESTRICT,
                allow_local_processing=True,
                allow_external_ai=False,
                require_human_approval=is_high_risk,
                reason=(
                    "CONFIDENTIAL data — local processing only. "
                    + ("High-risk action requires human approval." if is_high_risk
                       else "Standard restrictions apply.")
                ),
            )

        elif classification == SecurityClassification.INTERNAL:
            return PolicyResult(
                classification=classification,
                decision=PolicyDecision.MASK,
                allow_local_processing=True,
                allow_external_ai=False,
                require_human_approval=False,
                reason="INTERNAL data — local processing, sensitive fields masked.",
            )

        else:  # GENERAL
            return PolicyResult(
                classification=classification,
                decision=PolicyDecision.ALLOW,
                allow_local_processing=True,
                allow_external_ai=False,  # Sovereign: always local
                require_human_approval=False,
                reason="GENERAL data — local processing permitted.",
            )
