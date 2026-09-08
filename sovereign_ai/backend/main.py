"""
Sovereign AI Workbench — FastAPI application entry point.

Start the server with::

    uvicorn backend.main:app --reload

The application registers all API routers, exception handlers,
CORS middleware, and lifecycle events.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.logging_config import setup_logging
from backend.exceptions import (
    SovereignError,
    sovereign_error_handler,
    generic_error_handler,
)

from backend.api.health import router as health_router
from backend.api.documents import router as documents_router
from backend.api.models import router as models_router
from backend.api.agents import router as agents_router
from backend.api.auth import router as auth_router
from backend.api.security import router as security_router
from backend.api.governance import router as governance_router
from backend.api.audit import router as audit_router
from backend.api.deliverables import router as deliverables_router

logger = logging.getLogger(__name__)


# ── Lifecycle ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup / shutdown lifecycle."""
    settings = get_settings()
    setup_logging(
        log_level=settings.log_level,
        json_output=(settings.environment == "production"),
    )
    logger.info(
        "Starting %s v%s [%s]",
        settings.app_name, settings.app_version, settings.environment,
    )
    logger.info("Project root: %s", settings.project_root)

    # Ensure critical directories exist
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.audit_dir.mkdir(parents=True, exist_ok=True)

    yield  # ← application is running

    logger.info("Shutting down %s", settings.app_name)


# ── Application Factory ─────────────────────────────────────────────

def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "On-Premise Agentic AI Workbench — "
            "Zero External Egress, Controlled AI Processing."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── Exception handlers ───────────────────────────────────────
    application.add_exception_handler(SovereignError, sovereign_error_handler)
    application.add_exception_handler(Exception, generic_error_handler)

    # ── CORS ─────────────────────────────────────────────────────
    origins = [
        o.strip()
        for o in settings.cors_origins.split(",")
        if o.strip()
    ]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ──────────────────────────────────────────────────
    prefix = settings.api_prefix

    # Functional
    application.include_router(health_router, prefix=prefix)
    application.include_router(auth_router, prefix=prefix)
    application.include_router(security_router, prefix=prefix)

    # Placeholder (future phases)
    application.include_router(documents_router, prefix=prefix)
    application.include_router(models_router, prefix=prefix)
    application.include_router(agents_router, prefix=prefix)
    application.include_router(governance_router, prefix=prefix)
    application.include_router(audit_router, prefix=prefix)
    application.include_router(deliverables_router, prefix=prefix)

    return application


# Module-level app instance used by ``uvicorn backend.main:app``
app = create_app()
