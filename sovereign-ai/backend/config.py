"""
Centralised configuration for the Sovereign AI Workbench backend.

All settings are loaded from environment variables (or a `.env` file)
with sensible defaults.  Paths are resolved relative to the project
root (`sovereign-ai/`) so the backend can be started from any working
directory.
"""

from pathlib import Path
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings
from pydantic import Field


def _project_root() -> Path:
    """Return the absolute path to the `sovereign-ai/` directory."""
    return Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application-wide settings backed by environment / .env file."""

    # ── General ──────────────────────────────────────────────────────
    app_name: str = "Sovereign AI Workbench"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    log_level: str = "INFO"

    # ── Server ───────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    api_prefix: str = "/api/v1"
    cors_origins: str = "*"  # comma-separated list or "*"

    # ── Paths (resolved relative to project root) ────────────────────
    project_root: Path = Field(default_factory=_project_root)
    data_dir: Path = Field(default_factory=lambda: _project_root() / "data")
    knowledge_dir: Path = Field(default_factory=lambda: _project_root() / "data" / "knowledge")
    vector_db_dir: Path = Field(default_factory=lambda: _project_root() / "data" / "vector_db")
    upload_dir: Path = Field(default_factory=lambda: _project_root() / "data" / "uploads")
    audit_dir: Path = Field(default_factory=lambda: _project_root() / "audit")
    config_dir: Path = Field(default_factory=lambda: _project_root() / "config")

    # ── Ollama ───────────────────────────────────────────────────────
    ollama_host: str = "http://localhost:11434"
    ollama_timeout: int = 30

    # ── Models config ────────────────────────────────────────────────
    models_config_file: str = "models.json"

    # ── Embeddings ───────────────────────────────────────────────────
    embedding_model: str = "all-MiniLM-L6-v2"

    # ── ChromaDB ─────────────────────────────────────────────────────
    chroma_collection: str = "enterprise_knowledge"

    # ── Authentication (Phase 2) ─────────────────────────────────────
    jwt_secret_key: str = "sovereign-dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 480  # 8 hours
    users_file: Path = Field(
        default_factory=lambda: _project_root() / "backend" / "data" / "users.json"
    )
    roles_file: Path = Field(
        default_factory=lambda: _project_root() / "backend" / "data" / "roles.json"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()

