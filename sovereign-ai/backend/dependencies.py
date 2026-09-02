"""
FastAPI dependency injection for authentication and authorization.

Usage in any router::

    from backend.dependencies import get_current_user, require_permission

    @router.get("/protected")
    async def protected(user = Depends(get_current_user)):
        ...

    @router.post("/admin-only")
    async def admin_only(user = Depends(require_permission("manage_users"))):
        ...
"""

import logging
from typing import Callable

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.schemas.auth import UserResponse, UserRole
from backend.services.auth import AuthService
from backend.services.rbac import RBACService
from backend.exceptions import AuthenticationError, AuthorisationError

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)

# Lazily initialised singletons
_auth_service: AuthService | None = None
_rbac_service: RBACService | None = None


def _get_auth_service() -> AuthService:
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


def _get_rbac_service() -> RBACService:
    global _rbac_service
    if _rbac_service is None:
        _rbac_service = RBACService()
    return _rbac_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> UserResponse:
    """
    Extract and validate the JWT from the Authorization header.

    Returns the authenticated user or raises ``AuthenticationError``.
    """
    if credentials is None:
        raise AuthenticationError("Authorization header missing")

    token = credentials.credentials
    auth = _get_auth_service()

    try:
        payload = auth.decode_token(token)
    except Exception:
        raise AuthenticationError("Invalid or expired token")

    username: str | None = payload.get("sub")
    role_str: str | None = payload.get("role")

    if username is None or role_str is None:
        raise AuthenticationError("Malformed token payload")

    # Verify user still exists and is active
    user = auth.get_user(username)
    if user is None or not user.is_active:
        raise AuthenticationError("User not found or deactivated")

    return UserResponse(
        username=user.username,
        role=user.role,
        is_active=user.is_active,
    )


def require_permission(permission: str) -> Callable:
    """
    Return a FastAPI dependency that checks the current user has
    the given permission.

    Usage::

        @router.post("/upload")
        async def upload(user = Depends(require_permission("upload_documents"))):
            ...
    """

    async def _check(
        user: UserResponse = Depends(get_current_user),
    ) -> UserResponse:
        rbac = _get_rbac_service()
        if not rbac.has_permission(user.role, permission):
            logger.warning(
                "RBAC denied: user=%s role=%s permission=%s",
                user.username, user.role.value, permission,
            )
            raise AuthorisationError(
                f"Role '{user.role.value}' does not have "
                f"permission '{permission}'"
            )
        return user

    return _check
