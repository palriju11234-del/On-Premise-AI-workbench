import hashlib
import json
from datetime import datetime
from pathlib import Path


class Provenance:

    def hash_file(self, filepath):

        data = Path(filepath).read_bytes()

        return hashlib.sha256(data).hexdigest()

    def create_record(
        self,
        task,
        model,
        verification,
        approval,
        input_hash=None,
        output_hash=None
    ):

        record = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "model": model,
            "verification": verification,
            "human_approval": approval,
            "input_sha256": input_hash,
            "output_sha256": output_hash
        }

        Path("audit").mkdir(exist_ok=True)

        with open(
            "audit/events.jsonl",
            "a",
            encoding="utf-8"
        ) as f:

            f.write(
                json.dumps(record) + "\n"
            )

        return record