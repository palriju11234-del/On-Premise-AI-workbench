"""
Tests for Role-Based Access Control (RBAC).
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.rbac import RBACService
from backend.schemas.auth import UserRole

client = TestClient(app)


def test_rbac_service_permissions():
    rbac = RBACService()

    # ADMIN permissions
    assert rbac.has_permission(UserRole.ADMIN, "manage_users")
    assert rbac.has_permission(UserRole.ADMIN, "approve_actions")
    assert rbac.has_permission(UserRole.ADMIN, "view_audit")

    # ENGINEER permissions
    assert rbac.has_permission(UserRole.ENGINEER, "upload_documents")
    assert rbac.has_permission(UserRole.ENGINEER, "execute_agents")
    assert not rbac.has_permission(UserRole.ENGINEER, "view_audit")
    assert not rbac.has_permission(UserRole.ENGINEER, "manage_users")

    # REVIEWER permissions
    assert rbac.has_permission(UserRole.REVIEWER, "approve_actions")
    assert rbac.has_permission(UserRole.REVIEWER, "view_audit")
    assert not rbac.has_permission(UserRole.REVIEWER, "upload_documents")

    # OPERATOR permissions
    assert rbac.has_permission(UserRole.OPERATOR, "upload_documents")
    assert rbac.has_permission(UserRole.OPERATOR, "execute_agents")
    assert not rbac.has_permission(UserRole.OPERATOR, "approve_actions")
    assert not rbac.has_permission(UserRole.OPERATOR, "manage_users")


def test_unauthorized_action_blocked_via_api():
    # 1. Login as admin and create an operator user
    admin_login = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    admin_token = admin_login.json()["data"]["access_token"]

    client.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "op_user",
            "password": "op_password123",
            "role": "OPERATOR",
        },
    )

    # 2. Login as the operator user
    op_login = client.post(
        "/api/v1/auth/login",
        json={"username": "op_user", "password": "op_password123"},
    )
    op_token = op_login.json()["data"]["access_token"]

    # 3. Attempt admin-only action (user registration) as operator -> should return 403 Forbidden
    response = client.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {op_token}"},
        json={
            "username": "unauthorized_create",
            "password": "password123",
            "role": "OPERATOR",
        },
    )
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["type"] == "AuthorisationError"
