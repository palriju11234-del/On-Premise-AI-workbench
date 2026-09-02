"""
Role-Based Access Control (RBAC) service.

Loads role-permission mappings from ``roles.json`` and provides a
centralized check used by the FastAPI dependency layer.
"""

import json
import logging

from backend.config import get_settings
from backend.schemas.auth import UserRole

logger = logging.getLogger(__name__)


class RBACService:
    """Centralized role → permission resolver."""

    def __init__(self):
        self.settings = get_settings()
        self._permissions: dict[str, list[str]] = self._load_roles()

    def _load_roles(self) -> dict[str, list[str]]:
        """Load role definitions from disk."""
        path = self.settings.roles_file
        if not path.exists():
            logger.warning("Roles file not found at %s — using empty roles", path)
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(
            "Loaded %d roles: %s",
            len(data), ", ".join(data.keys()),
        )
        return data

    def get_permissions(self, role: UserRole) -> list[str]:
        """Return the list of permissions for a given role."""
        return self._permissions.get(role.value, [])

    def has_permission(self, role: UserRole, permission: str) -> bool:
        """Check whether a role grants a specific permission."""
        return permission in self.get_permissions(role)

    def get_all_roles(self) -> dict[str, list[str]]:
        """Return the full role-permission map."""
        return dict(self._permissions)
