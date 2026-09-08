"""
Health-check service that probes infrastructure dependencies.

This is the only fully-functional service delivered in Phase 1.
Future phases will add document, RAG, agent, and governance services.
"""

import logging
import shutil

import httpx

from backend.config import get_settings
from backend.schemas.health import ComponentStatus, HealthResponse

logger = logging.getLogger(__name__)


class HealthService:
    """Probes Ollama, ChromaDB, and disk to build a health report."""

    async def check_ollama(self) -> ComponentStatus:
        """Ping the Ollama API root."""
        settings = get_settings()
        try:
            async with httpx.AsyncClient(timeout=settings.ollama_timeout) as client:
                resp = await client.get(settings.ollama_host)
                if resp.status_code == 200:
                    return ComponentStatus(
                        name="ollama",
                        status="healthy",
                        detail=f"Reachable at {settings.ollama_host}",
                    )
                return ComponentStatus(
                    name="ollama",
                    status="unhealthy",
                    detail=f"HTTP {resp.status_code}",
                )
        except Exception as exc:
            logger.warning("Ollama health check failed: %s", exc)
            return ComponentStatus(
                name="ollama",
                status="unhealthy",
                detail=str(exc),
            )

    async def check_chromadb(self) -> ComponentStatus:
        """Verify the ChromaDB persistence directory exists."""
        settings = get_settings()
        db_path = settings.vector_db_dir
        try:
            if db_path.exists() and db_path.is_dir():
                return ComponentStatus(
                    name="chromadb",
                    status="healthy",
                    detail=f"Persistence at {db_path}",
                )
            return ComponentStatus(
                name="chromadb",
                status="unhealthy",
                detail=f"Directory not found: {db_path}",
            )
        except Exception as exc:
            logger.warning("ChromaDB health check failed: %s", exc)
            return ComponentStatus(
                name="chromadb",
                status="unhealthy",
                detail=str(exc),
            )

    async def check_disk(self) -> ComponentStatus:
        """Report available disk space on the data partition."""
        settings = get_settings()
        try:
            usage = shutil.disk_usage(settings.data_dir)
            free_gb = usage.free / (1024 ** 3)
            status = "healthy" if free_gb > 1.0 else "unhealthy"
            return ComponentStatus(
                name="disk",
                status=status,
                detail=f"{free_gb:.1f} GB free",
            )
        except Exception as exc:
            logger.warning("Disk health check failed: %s", exc)
            return ComponentStatus(
                name="disk",
                status="unknown",
                detail=str(exc),
            )

    async def full_check(self) -> HealthResponse:
        """Run all component checks and return an aggregate report."""
        settings = get_settings()

        components = [
            await self.check_ollama(),
            await self.check_chromadb(),
            await self.check_disk(),
        ]

        # Aggregate: unhealthy if any component is unhealthy,
        # degraded if any is unknown, healthy otherwise.
        statuses = {c.status for c in components}
        if "unhealthy" in statuses:
            overall = "degraded"
        elif "unknown" in statuses:
            overall = "degraded"
        else:
            overall = "healthy"

        return HealthResponse(
            status=overall,
            version=settings.app_version,
            environment=settings.environment,
            components=components,
        )
