import os
import sys
from sovereign_ai.core.config import APP_NAME, APP_VERSION, ENVIRONMENT, DATA_DIR, AUDIT_DIR
from sovereign_ai.schemas.health import HealthResponse

class HealthService:
    @staticmethod
    def get_health() -> HealthResponse:
        checks = {
            "python_runtime": sys.version.split()[0],
            "data_directory": "writable" if DATA_DIR.exists() and os.access(DATA_DIR, os.W_OK) else "unwritable",
            "audit_directory": "writable" if AUDIT_DIR.exists() and os.access(AUDIT_DIR, os.W_OK) else "unwritable"
        }
        return HealthResponse(
            status="healthy",
            app_name=APP_NAME,
            version=APP_VERSION,
            environment=ENVIRONMENT,
            checks=checks
        )
