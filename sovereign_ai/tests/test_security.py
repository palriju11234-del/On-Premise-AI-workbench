"""
Tests for security classification and policy decision engine.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.security import SecurityService
from backend.schemas.security import (
    SecurityClassification,
    PolicyDecision,
)

client = TestClient(app)


def test_security_classification_general():
    svc = SecurityService()
    text = "This is a public press release about corporate updates and community events."
    result = svc.classify(text)
    assert result.classification == SecurityClassification.GENERAL
    assert result.score == 0


def test_security_classification_confidential():
    svc = SecurityService()
    text = "CONFIDENTIAL: Internal inspection report for refinery plant equipment maintenance and vendor details."
    result = svc.classify(text)
    assert result.classification == SecurityClassification.CONFIDENTIAL
    assert result.score >= 2
    assert len(result.keywords_matched) >= 2


def test_policy_evaluation_confidential_restricts_external_ai():
    svc = SecurityService()

    # Evaluation for CONFIDENTIAL text
    policy = svc.evaluate_policy(
        classification=SecurityClassification.CONFIDENTIAL,
        action="execute_agents",
    )

    assert policy.classification == SecurityClassification.CONFIDENTIAL
    assert policy.decision == PolicyDecision.RESTRICT
    assert policy.allow_local_processing is True
    assert policy.allow_external_ai is False  # External AI blocked!
    assert policy.require_human_approval is True  # High-risk action requires human approval!


def test_policy_evaluation_sovereign_zero_egress_all_levels():
    svc = SecurityService()

    for classification in [
        SecurityClassification.GENERAL,
        SecurityClassification.INTERNAL,
        SecurityClassification.CONFIDENTIAL,
    ]:
        policy = svc.evaluate_policy(classification=classification, action="process")
        # In all sovereign configurations, external cloud AI calls are strictly forbidden
        assert policy.allow_external_ai is False


def test_security_api_classify_and_evaluate():
    # Login to get valid token
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test /security/classify
    classify_resp = client.post(
        "/api/v1/security/classify",
        headers=headers,
        json={"text": "Plant equipment maintenance inspection document", "filename": "report.pdf"},
    )
    assert classify_resp.status_code == 200
    c_data = classify_resp.json()["data"]
    assert c_data["classification"] in ["INTERNAL", "CONFIDENTIAL"]

    # Test /security/evaluate
    eval_resp = client.post(
        "/api/v1/security/evaluate",
        headers=headers,
        json={
            "classification": "CONFIDENTIAL",
            "action": "approve_actions",
        },
    )
    assert eval_resp.status_code == 200
    e_data = eval_resp.json()["data"]
    assert e_data["decision"] == "RESTRICT"
    assert e_data["allow_external_ai"] is False
    assert e_data["require_human_approval"] is True
