import hashlib
import json
from datetime import datetime
from pathlib import Path
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
    ) -> dict:
        record = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "model": model,
            "verification": verification,
            "human_approval": approval,
            "input_sha256": input_hash,
            "output_sha256": output_hash,
        }

        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        audit_file = AUDIT_DIR / "events.jsonl"

        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

        return record