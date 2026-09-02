import json
from pathlib import Path
from typing import Dict, Any, Optional
from sovereign_ai.core.config import CONFIG_DIR, BASE_DIR
from sovereign_ai.schemas.security import DataClassification

DEFAULT_MODELS = {
    "vision": "llava:7b",
    "coding": "codellama:7b",
    "reasoning": "llama3:8b",
    "confidential_airgap": "llama3:8b-instruct-q4",
}


def _extract_model_name(raw_model: Any, fallback: str) -> str:
    """Extracts model name if config returns a dictionary or string."""
    if isinstance(raw_model, dict):
        return raw_model.get("name") or raw_model.get("model") or fallback
    elif isinstance(raw_model, str):
        return raw_model
    return fallback


class ModelRouter:
    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            target_path = Path(config_path)
        else:
            candidates = [
                CONFIG_DIR / "models.json",
                BASE_DIR / "config" / "models.json",
                Path("config/models.json"),
            ]
            target_path = next((p for p in candidates if p.exists()), None)

        if target_path and target_path.exists():
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    self.models = json.load(f).get("models", DEFAULT_MODELS)
            except Exception:
                self.models = DEFAULT_MODELS
        else:
            self.models = DEFAULT_MODELS

    def route(
        self,
        task_type: str,
        classification: DataClassification = DataClassification.GENERAL,
    ) -> Dict[str, Any]:
        """
        Dynamically routes task to the appropriate local model backend
        based on task nature and data classification.
        """
        # Strict Sovereign Air-gap enforcement for CONFIDENTIAL tasks
        if classification == DataClassification.CONFIDENTIAL:
            raw_confidential = self.models.get("confidential_airgap", self.models.get("reasoning"))
            model_name = _extract_model_name(raw_confidential, "llama3:8b-instruct-q4")
            return {
                "model": model_name,
                "tier": "air-gapped-secure",
                "temperature": 0.1,
                "external_api_allowed": False,
            }

        # Multimodal / Vision
        if task_type in ["image", "scanned_document", "multimodal"]:
            raw_model = self.models.get("vision")
            model_name = _extract_model_name(raw_model, "llava:7b")
            return {
                "model": model_name,
                "tier": "vision-multimodal",
                "temperature": 0.2,
                "external_api_allowed": False,
            }

        # Code / Developer tooling
        elif task_type in ["coding", "code_generation", "code_review", "debugging"]:
            raw_model = self.models.get("coding")
            model_name = _extract_model_name(raw_model, "qwen2.5-coder:3b")
            return {
                "model": model_name,
                "tier": "code-specialized",
                "temperature": 0.1,
                "external_api_allowed": False,
            }

        # General text / reasoning default
        else:
            raw_model = self.models.get("reasoning")
            model_name = _extract_model_name(raw_model, "llama3:8b")
            return {
                "model": model_name,
                "tier": "general-reasoning",
                "temperature": 0.7,
                "external_api_allowed": False,
            }