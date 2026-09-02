"""
Tests for Cryptographic Hashing and Provenance / Audit layer (Phase 8).
"""

import pytest
from pathlib import Path
from utils.hashing import hash_bytes, hash_text, hash_file, hash_dict, verify_integrity


class TestHashingUtils:
    """Unit tests for utils/hashing.py."""

    def test_same_input_same_hash(self):
        text = "Sovereign AI Workbench Test Input"
        hash1 = hash_text(text)
        hash2 = hash_text(text)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length

    def test_different_input_different_hash(self):
        hash1 = hash_text("Input A")
        hash2 = hash_text("Input B")
        assert hash1 != hash2

    def test_file_hashing(self, tmp_path):
        test_file = tmp_path / "test_artifact.txt"
        content = b"Cryptographic Provenance Artifact Data"
        test_file.write_bytes(content)

        expected_hash = hash_bytes(content)
        calculated_file_hash = hash_file(test_file)

        assert calculated_file_hash == expected_hash

    def test_text_hashing(self):
        text = "Confidential Maintenance Inspection Report"
        expected = hash_bytes(text.encode("utf-8"))
        assert hash_text(text) == expected

    def test_dict_hashing_deterministic(self):
        dict1 = {"b": 2, "a": 1}
        dict2 = {"a": 1, "b": 2}
        assert hash_dict(dict1) == hash_dict(dict2)

    def test_verify_integrity_valid(self):
        data = "Original output report content"
        h = hash_text(data)
        assert verify_integrity(h, h) is True

    def test_verify_integrity_modified(self):
        original = "Original content"
        modified = "Tampered content"
        h_orig = hash_text(original)
        h_mod = hash_text(modified)
        assert verify_integrity(h_mod, h_orig) is False


class TestProvenanceAPI:
    """Integration tests for /api/v1/audit API endpoints."""

    def test_calculate_hash_api(self, client, auth_headers):
        response = client.post(
            "/api/v1/audit/hash/calculate",
            headers=auth_headers,
            json={"text": "Test provenance content"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "sha256" in data["data"]
        assert len(data["data"]["sha256"]) == 64

    def test_verify_hash_valid_api(self, client, auth_headers):
        text = "Integrity check text"
        calculated_hash = hash_text(text)

        response = client.post(
            "/api/v1/audit/hash/verify",
            headers=auth_headers,
            json={
                "expected_hash": calculated_hash,
                "text_content": text,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["is_valid"] is True
        assert data["data"]["status"] == "VALID"

    def test_verify_hash_modified_api(self, client, auth_headers):
        original_text = "Original report"
        modified_text = "Modified report text"
        original_hash = hash_text(original_text)

        response = client.post(
            "/api/v1/audit/hash/verify",
            headers=auth_headers,
            json={
                "expected_hash": original_hash,
                "text_content": modified_text,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["is_valid"] is False
        assert data["data"]["status"] == "MODIFIED"

    def test_record_and_get_provenance(self, client, auth_headers):
        task_id = "task-prov-100"
        record_payload = {
            "task_id": task_id,
            "input_hash": hash_text("Input Document"),
            "knowledge_source_hashes": [hash_text("Knowledge Doc 1"), hash_text("Knowledge Doc 2")],
            "model_name": "qwen3:4b",
            "model_version": "1.0",
            "result_hash": hash_text("Intermediate Result"),
            "verification_status": "PASSED",
            "risk_level": "GENERAL",
            "approval_status": "AUTOMATIC",
            "output_hash": hash_text("Final Output File"),
        }

        # 1. Record provenance
        record_resp = client.post(
            "/api/v1/audit/provenance",
            headers=auth_headers,
            json=record_payload,
        )
        assert record_resp.status_code == 200
        assert record_resp.json()["success"] is True

        # 2. Get task provenance
        get_resp = client.get(
            f"/api/v1/audit/provenance/{task_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1

        record = data["data"][-1]
        assert record["task_id"] == task_id
        assert len(record["knowledge_source_hashes"]) == 2
        assert record["model_name"] == "qwen3:4b"
        assert record["verification_status"] == "PASSED"

    def test_unauthorized_user_audit_access_blocked(self, client):
        """Users without view_audit permission or unauthenticated requests should be blocked."""
        # Unauthenticated
        response = client.get("/api/v1/audit/events")
        assert response.status_code == 401
