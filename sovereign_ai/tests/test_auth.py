"""
Tests for authentication service and API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.auth import AuthService

client = TestClient(app)


def test_login_success():
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["role"] == "ADMIN"


def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["type"] == "AuthenticationError"


def test_unauthenticated_request_rejected():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False


def test_authenticated_profile_access():
    # Login
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    token = login_resp.json()["data"]["access_token"]

    # Access profile with token
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["username"] == "admin"
    assert data["data"]["role"] == "ADMIN"


def test_admin_user_registration():
    # Login as admin
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    token = login_resp.json()["data"]["access_token"]

    # Register new operator user
    response = client.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "test_operator",
            "password": "password123",
            "role": "OPERATOR",
        },
    )
    assert response.status_code in [200, 409]  # 409 if test run twice
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "test_operator"
        assert data["data"]["role"] == "OPERATOR"
