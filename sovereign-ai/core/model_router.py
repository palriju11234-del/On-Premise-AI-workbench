import json
from pathlib import Path


class ModelRouter:

    def __init__(self):

        config_path = Path("config/models.json")

        with open(config_path, "r", encoding="utf-8") as f:
            self.models = json.load(f)["models"]

    def route(self, task_type):

        if task_type in [
            "image",
            "scanned_document",
            "multimodal"
        ]:
            return self.models["vision"]

        elif task_type in [
            "coding",
            "code_generation",
            "code_review",
            "debugging"
        ]:
            return self.models["coding"]

        else:
            return self.models["reasoning"]