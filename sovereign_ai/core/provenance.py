import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from sovereign_ai.core.config import AUDIT_DIR


class Provenance:
    def hash_file(self, filepath: str) -> str:
        data = Path(filepath).read_bytes()
        return hashlib.sha256(data).hexdigest()

    def create_record(
        self,
        task: str,
        model: str,
        verification: dict,
        approval: bool,
        input_hash: str = None,
        output_hash: str = None,
        filename: Optional[str] = None,
        retrieved_evidence: Optional[Any] = None,
        risk_assessment: Optional[Dict[str, Any]] = None,
        human_gate: Optional[Dict[str, Any]] = None,
        delivery_status: Optional[str] = None,
        stages: Optional[List[Dict[str, Any]]] = None,
    ) -> dict:
        """
        Creates an immutable provenance record linking:
        task -> input_document -> input_sha256 -> retrieved_evidence -> model -> reasoning ->
        verification -> risk -> human_gate -> output -> output_sha256.
        """
        record: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "model": model,
            "verification": verification,
            "human_approval": approval,
            "input_sha256": input_hash,
            "output_sha256": output_hash,
        }

        # Optional lineage metadata
        if filename:
            record["filename"] = filename
        if retrieved_evidence is not None:
            record["retrieved_evidence"] = retrieved_evidence
        if risk_assessment is not None:
            record["risk_assessment"] = risk_assessment
        if human_gate is not None:
            record["human_gate"] = human_gate
        if delivery_status is not None:
            record["delivery_status"] = delivery_status
        if stages is not None:
            record["stages_count"] = len(stages)

        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        audit_file = AUDIT_DIR / "events.jsonl"

        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

        return record

    def log_stage_event(
        self,
        stage: str,
        status: str,
        task: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        """
        Logs a granular agent state transition to AUDIT_DIR/agent_events.jsonl.
        Avoids logging raw sensitive document contents.
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "AGENT_STAGE_TRANSITION",
            "stage": stage,
            "status": status,
            "task_preview": (task[:80] + "...") if task and len(task) > 80 else task,
            "details": details or {},
            "error": error,
        }

        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        event_file = AUDIT_DIR / "agent_events.jsonl"

        with open(event_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")