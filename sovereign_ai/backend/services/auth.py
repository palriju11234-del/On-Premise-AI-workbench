"""
Authentication service — local JWT-based auth with JSON user store.

Handles password hashing, user CRUD, and JWT token creation/validation.
Uses a local ``users.json`` file as the prototype user store (no
external database required).
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from passlib.context import CryptContext

from backend.config import get_settings
from backend.schemas.auth import UserCreate, UserInDB, UserRole

logger = logging.getLogger(__name__)

_pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class AuthService:
    """Manages users and JWT tokens."""

    def __init__(self):
        self.settings = get_settings()
        self._ensure_user_store()

    # ── Password Hashing ─────────────────────────────────────────

    @staticmethod
    def hash_password(plain: str) -> str:
        return _pwd_context.hash(plain)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return _pwd_context.verify(plain, hashed)

    # ── User Store I/O ───────────────────────────────────────────

    def _load_users(self) -> dict:
        """Load the user store from disk."""
        path = self.settings.users_file
        if not path.exists():
            return {"users": {}}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_users(self, data: dict) -> None:
        """Persist the user store to disk."""
        path = self.settings.users_file
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _ensure_user_store(self) -> None:
        """Seed a default admin user if the store is empty or missing."""
        data = self._load_users()
        if not data.get("users"):
            logger.info("Seeding default admin user")
            data["users"] = {
                "admin": {
                    "username": "admin",
                    "hashed_password": self.hash_password("admin123"),
                    "role": "ADMIN",
                    "is_active": True,
                }
            }
            self._save_users(data)

    # ── User CRUD ────────────────────────────────────────────────

    def get_user(self, username: str) -> UserInDB | None:
        """Look up a user by username."""
        data = self._load_users()
        record = data.get("users", {}).get(username)
        if record is None:
            return None
        return UserInDB(**record)

    def create_user(self, user: UserCreate) -> UserInDB:
        """Create a new user. Raises ValueError if username exists."""
        data = self._load_users()
        if user.username in data.get("users", {}):
            raise ValueError(f"User '{user.username}' already exists")

        record = UserInDB(
            username=user.username,
            hashed_password=self.hash_password(user.password),
            role=user.role,
        )
        data.setdefault("users", {})[user.username] = record.model_dump()
        self._save_users(data)
        logger.info("Created user: %s [%s]", user.username, user.role.value)
        return record

    def authenticate(self, username: str, password: str) -> UserInDB | None:
        """Verify credentials. Returns user on success, None on failure."""
        user = self.get_user(username)
        if user is None:
            return None
        if not user.is_active:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    # ── JWT Tokens ───────────────────────────────────────────────

    def create_token(self, username: str, role: UserRole) -> str:
        """Issue a signed JWT."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": username,
            "role": role.value,
            "iat": now,
            "exp": now + timedelta(minutes=self.settings.jwt_expiry_minutes),
        }
        return jwt.encode(
            payload,
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
        )

    def decode_token(self, token: str) -> dict:
        """
        Decode and validate a JWT.

        Returns the payload dict on success.
        Raises ``jwt.InvalidTokenError`` on any failure.
        """
        return jwt.decode(
            token,
            self.settings.jwt_secret_key,
            algorithms=[self.settings.jwt_algorithm],
        )
