"""
Authentication endpoints.

POST /auth/login    — issue a JWT token
POST /auth/register — create a new user (requires ADMIN)
GET  /auth/me       — return current user profile
"""

import logging

from fastapi import APIRouter, Depends

from backend.schemas.auth import (
    UserCreate,
    UserLogin,
    TokenResponse,
    UserResponse,
)
from backend.schemas.common import ApiResponse
from backend.services.auth import AuthService
from backend.dependencies import get_current_user, require_permission
from backend.exceptions import AuthenticationError, SovereignError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

_auth_service: AuthService | None = None


def _get_auth() -> AuthService:
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    summary="User login",
    description="Authenticate with username/password and receive a JWT token.",
)
async def login(body: UserLogin):
    """Validate credentials and issue a JWT."""
    auth = _get_auth()
    user = auth.authenticate(body.username, body.password)
    if user is None:
        raise AuthenticationError("Invalid username or password")

    token = auth.create_token(user.username, user.role)
    logger.info("Login successful: %s [%s]", user.username, user.role.value)

    return ApiResponse(
        data=TokenResponse(
            access_token=token,
            expires_in_minutes=auth.settings.jwt_expiry_minutes,
            role=user.role,
        )
    )


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    summary="Register new user",
    description="Create a new user account. Requires ADMIN role.",
)
async def register(
    body: UserCreate,
    current_user: UserResponse = Depends(require_permission("manage_users")),
):
    """Create a new user (admin only)."""
    auth = _get_auth()
    try:
        user = auth.create_user(body)
    except ValueError as exc:
        raise SovereignError(str(exc), status_code=409)

    return ApiResponse(
        data=UserResponse(
            username=user.username,
            role=user.role,
            is_active=user.is_active,
        )
    )


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    summary="Current user profile",
    description="Return the profile of the authenticated user.",
)
async def me(current_user: UserResponse = Depends(get_current_user)):
    """Return current user's profile."""
    return ApiResponse(data=current_user)
