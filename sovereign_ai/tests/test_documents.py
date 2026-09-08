"""
Tests for Phase 3 — Document Intelligence.

Tests the document upload, processing pipeline, listing, and retrieval
through the FastAPI endpoints.
"""

import io
import pytest
from fastapi.testclient import TestClient

from backend.main import app


# ── Upload Tests ─────────────────────────────────────────────────────

class TestDocumentUpload:
    """Tests for POST /api/v1/documents/upload."""

    def test_upload_valid_pdf(self, client, auth_headers, sample_pdf_bytes):
        """Normal PDF with extractable text should succeed."""
        response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("test_report.pdf", sample_pdf_bytes, "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        result = data["data"]

        # Metadata checks
        meta = result["metadata"]
        assert meta["filename"] == "test_report.pdf"
        assert meta["document_type"] == "PDF"
        assert meta["page_count"] >= 1
        assert meta["ocr_used"] is False
        assert meta["document_id"]  # UUID should be present
        assert meta["classification"] in ["GENERAL", "INTERNAL", "CONFIDENTIAL"]
        assert meta["file_size_bytes"] > 0

        # Text should be extracted
        assert len(result["extracted_text"]) > 0
        assert len(result["pages"]) >= 1
        assert result["pages"][0]["page"] == 1

    def test_upload_valid_image(self, client, auth_headers, sample_image_bytes):
        """PNG image upload should succeed (OCR attempted if available)."""
        response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("photo.png", sample_image_bytes, "image/png")},
        )
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        meta = data["data"]["metadata"]
        assert meta["filename"] == "photo.png"
        assert meta["document_type"] == "IMAGE"
        assert meta["page_count"] == 1

    def test_upload_scanned_pdf(self, client, auth_headers, sample_empty_pdf_bytes):
        """PDF with no extractable text should be detected as scanned."""
        response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("scan.pdf", sample_empty_pdf_bytes, "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        meta = data["data"]["metadata"]
        assert meta["document_type"] == "SCANNED_PDF"

    def test_upload_invalid_extension(self, client, auth_headers):
        """File with unsupported extension should be rejected."""
        fake_content = b"not a real file"
        response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("malware.exe", fake_content, "application/octet-stream")},
        )
        assert response.status_code == 422

    def test_upload_empty_file(self, client, auth_headers):
        """Empty file should be rejected."""
        response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )
        assert response.status_code == 422

    def test_upload_unauthenticated(self, client, sample_pdf_bytes):
        """Upload without auth token should be rejected."""
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.pdf", sample_pdf_bytes, "application/pdf")},
        )
        assert response.status_code == 401


# ── List Tests ───────────────────────────────────────────────────────

class TestDocumentList:
    """Tests for GET /api/v1/documents."""

    def test_list_documents(self, client, auth_headers, sample_pdf_bytes):
        """After uploading, document should appear in the list."""
        # Upload first
        client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("list_test.pdf", sample_pdf_bytes, "application/pdf")},
        )

        # List
        response = client.get(
            "/api/v1/documents",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

        # Check our uploaded file is in the list
        filenames = [doc["filename"] for doc in data["data"]]
        assert "list_test.pdf" in filenames

    def test_list_documents_unauthenticated(self, client):
        """List without auth should be rejected."""
        response = client.get("/api/v1/documents")
        assert response.status_code == 401


# ── Get By ID Tests ──────────────────────────────────────────────────

class TestDocumentGetById:
    """Tests for GET /api/v1/documents/{document_id}."""

    def test_get_document_by_id(self, client, auth_headers, sample_pdf_bytes):
        """Uploaded document should be retrievable by ID."""
        # Upload
        upload_resp = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("byid_test.pdf", sample_pdf_bytes, "application/pdf")},
        )
        doc_id = upload_resp.json()["data"]["metadata"]["document_id"]

        # Get by ID
        response = client.get(
            f"/api/v1/documents/{doc_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["document_id"] == doc_id
        assert data["data"]["filename"] == "byid_test.pdf"

    def test_get_nonexistent_document(self, client, auth_headers):
        """Getting a non-existent ID should return 422."""
        response = client.get(
            "/api/v1/documents/nonexistent-id-12345",
            headers=auth_headers,
        )
        assert response.status_code == 422
