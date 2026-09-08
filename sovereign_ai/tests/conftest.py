"""
Shared pytest fixtures for Sovereign AI Workbench tests.

Provides:
  - Authenticated test client helpers
  - Synthetic file generators (PDF, PNG)
"""

import io
import pytest
from fastapi.testclient import TestClient

from backend.main import app

# ── Test Client ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def client():
    """Session-scoped FastAPI test client."""
    return TestClient(app)


@pytest.fixture(scope="session")
def admin_token(client):
    """Obtain a JWT token for the seeded admin user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json()["data"]["access_token"]


@pytest.fixture(scope="session")
def auth_headers(admin_token):
    """Authorization headers with admin JWT."""
    return {"Authorization": f"Bearer {admin_token}"}


# ── Synthetic File Generators ────────────────────────────────────────

@pytest.fixture
def sample_pdf_bytes():
    """
    Generate a minimal valid PDF with extractable text using PyMuPDF.
    Returns raw bytes.
    """
    import fitz

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4
    page.insert_text(
        (72, 72),
        "This is a test document for the Sovereign AI Workbench. "
        "It contains sample text for extraction testing. "
        "The document processing pipeline should extract this text "
        "and classify it appropriately.",
        fontsize=12,
    )
    page.insert_text(
        (72, 120),
        "Section: Equipment Inspection Report. "
        "Confidential maintenance records for internal review.",
        fontsize=12,
    )
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture
def sample_image_bytes():
    """
    Generate a minimal valid PNG image using Pillow.
    Returns raw bytes.
    """
    from PIL import Image

    img = Image.new("RGB", (200, 100), color=(255, 255, 255))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def sample_empty_pdf_bytes():
    """
    Generate a minimal valid PDF with NO text (simulates scanned doc).
    Returns raw bytes.
    """
    import fitz

    doc = fitz.open()
    doc.new_page(width=595, height=842)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes
