"""
Pydantic models for authentication and user management.
"""

from pydantic import BaseModel, Field
from enum import Enum


class UserRole(str, Enum):
    """Supported user roles."""
    ADMIN = "ADMIN"
    ENGINEER = "ENGINEER"
    REVIEWER = "REVIEWER"
    OPERATOR = "OPERATOR"


class UserCreate(BaseModel):
    """Request body for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.OPERATOR


class UserLogin(BaseModel):
    """Request body for user login."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token returned on successful login."""
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    role: UserRole


class UserResponse(BaseModel):
    """Public user profile (no password)."""
    username: str
    role: UserRole
    is_active: bool = True


class UserInDB(BaseModel):
    """Internal user record stored in users.json."""
    username: str
    hashed_password: str
    role: UserRole
    is_active: bool = True
