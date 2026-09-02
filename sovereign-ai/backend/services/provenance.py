"""
Provenance & Audit Service.

Manages task-linked provenance records, SHA-256 integrity verification,
and audit trail persistence. Integrates with existing core.provenance
and utils.hashing.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional, List

from backend.config import get_settings
from backend.schemas.provenance import (
    ProvenanceRecord,
    HashVerifyResponse,
)
from utils.hashing import hash_bytes, hash_text, hash_file, verify_integrity

logger = logging.getLogger(__name__)

# Import existing core/provenance.py without modifying its baseline
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from core.provenance import Provenance as LegacyProvenance  # noqa: E402


class ProvenanceService:
    """Service layer managing cryptographic provenance records and audit verification."""

    def __init__(self):
        settings = get_settings()
        self._audit_dir = settings.audit_dir
        self._audit_file = self._audit_dir / "events.jsonl"
        self._legacy = LegacyProvenance()

        self._audit_dir.mkdir(parents=True, exist_ok=True)
        if not self._audit_file.exists():
            self._audit_file.touch()

    def calculate_text_hash(self, text: str) -> str:
        """Return hex SHA-256 hash for text."""
        return hash_text(text)

    def calculate_file_hash(self, filepath: Path | str) -> str:
        """Return hex SHA-256 hash for a local file."""
        return hash_file(filepath)

    def record_provenance(self, record: ProvenanceRecord) -> ProvenanceRecord:
        """
        Persist a structured provenance record into audit/events.jsonl.
        """
        record_dict = record.model_dump(mode="json")
        
        # Append to audit trail safely
        needs_newline = False
        if self._audit_file.exists() and self._audit_file.stat().st_size > 0:
            with open(self._audit_file, "rb") as f:
                f.seek(-1, 2)
                if f.read(1) != b"\n":
                    needs_newline = True

        with open(self._audit_file, "a", encoding="utf-8") as f:
            if needs_newline:
                f.write("\n")
            f.write(json.dumps(record_dict) + "\n")

        logger.info(
            "Recorded provenance: task_id=%s input_hash=%s output_hash=%s",
            record.task_id, record.input_hash, record.output_hash
        )
        return record

    def get_events(self, task_id: Optional[str] = None) -> List[dict]:
        """
        Read audit events from events.jsonl. Handles malformed lines gracefully.
        """
        if not self._audit_file.exists():
            return []

        events = []
        with open(self._audit_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    data = json.loads(line_str)
                    if isinstance(data, dict):
                        if task_id is None or data.get("task_id") == task_id or data.get("task") == task_id:
                            events.append(data)
                except json.JSONDecodeError:
                    logger.warning("Skipping malformed audit log line %d in %s", line_num, self._audit_file)
                    continue

        return events

    def get_provenance_by_task_id(self, task_id: str) -> List[dict]:
        """Retrieve all provenance records associated with a specific task_id."""
        return self.get_events(task_id=task_id)

    def verify_integrity(
        self,
        expected_hash: str,
        actual_hash: str
    ) -> HashVerifyResponse:
        """
        Compare actual calculated hash with expected hash and return result.
        """
        is_valid = verify_integrity(actual_hash, expected_hash)
        status = "VALID" if is_valid else "MODIFIED"
        
        return HashVerifyResponse(
            is_valid=is_valid,
            expected_hash=expected_hash,
            calculated_hash=actual_hash,
            status=status,
        )
