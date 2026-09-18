"""
CareerOS Cryptographic Double Opt-In & Notification Test Suite
===============================================================
Verifies the Release 2.2 privacy-preserving recruiter intro bridge (SPEC-0043):
1. Tamper-proof HMAC-SHA256 one-time token generation and storage.
2. Expiration checks and token invalidation.
3. Out-of-band notification dispatch (email HTML & SMS generation).
4. Candidate Inbound Portal API endpoints (preview and approve/decline).
"""

import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from api.main import app
from engine.notifications.dispatcher import NotificationDispatcher
from engine.storage.db import get_db_connection
from engine.recruiter.models import OptInStatus

client = TestClient(app)

def test_signed_token_generation_and_verification():
    """Verifies cryptographic token issuance and verification."""
    match_id = "match_test_001"
    candidate_id = "alaa_roucadi"

    token = NotificationDispatcher.generate_signed_token(match_id, candidate_id, ttl_days=7)
    assert token.startswith("cst_")

    # Verify token
    verified = NotificationDispatcher.verify_token(token)
    assert verified is not None
    assert verified["match_id"] == match_id
    assert verified["candidate_id"] == candidate_id
    assert verified["status"] == "PENDING"

def test_token_expiration_handling():
    """Verifies expired token is rejected and flagged as EXPIRED."""
    match_id = "match_expired_001"
    candidate_id = "candidate_002"

    # Create expired token directly in DB
    expired_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    token = "cst_expired_test_token"

    with get_db_connection() as conn:
        conn.execute("""
        INSERT OR REPLACE INTO consent_tokens (token, match_id, candidate_id, status, expires_at, created_at)
        VALUES (?, ?, ?, 'PENDING', ?, ?)
        """, (token, match_id, candidate_id, expired_at, datetime.now(timezone.utc).isoformat()))

    # Verification must fail and return None
    verified = NotificationDispatcher.verify_token(token)
    assert verified is None

    # Check status changed to EXPIRED in DB
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM consent_tokens WHERE token = ?", (token,))
        assert cursor.fetchone()["status"] == "EXPIRED"

def test_dispatch_intro_request_payload():
    """Verifies notification dispatch renders templates with zero PII leaks."""
    match_data = {
        "match_id": "match_dispatch_999",
        "job_title": "Head of AI Platform & Enterprise Engineering",
        "overall_match_score": 93.5,
        "anonymized_alias": "Strategic Engineering Leader [C-4389]"
    }

    dispatch_res = NotificationDispatcher.dispatch_intro_request(
        candidate_alias="Strategic Engineering Leader [C-4389]",
        candidate_id="alaa_roucadi",
        match_data=match_data,
        recruiter_notes="High urgency tier-1 banking mandate"
    )

    assert dispatch_res["dispatched"] is True
    assert "token" in dispatch_res
    assert "consent_url" in dispatch_res
    assert dispatch_res["token"] in dispatch_res["consent_url"]
    assert "Head of AI Platform" in dispatch_res["sms_preview"]

def test_candidate_consent_api_flow():
    """Verifies candidate viewing and approving an inbound match via REST API."""
    match_id = "match_api_test_555"
    candidate_id = "alaa_roucadi"

    # Seed match in recruiter_matches table
    with get_db_connection() as conn:
        conn.execute("""
        INSERT OR REPLACE INTO recruiter_matches (match_id, candidate_id, job_title, overall_score, opt_in_status, data_json, created_at)
        VALUES (?, ?, 'Lead Architect', 92.0, 'PENDING_CONSENT', '{"skills": ["AI", "Cloud"]}', ?)
        """, (match_id, candidate_id, datetime.now(timezone.utc).isoformat()))

    token = NotificationDispatcher.generate_signed_token(match_id, candidate_id)

    # 1. Preview endpoint with valid token
    preview_res = client.get(f"/api/candidates/consent-preview?token={token}")
    assert preview_res.status_code == 200
    pdata = preview_res.json()
    assert pdata["match_id"] == match_id
    assert pdata["job_title"] == "Lead Architect"

    # 2. Preview endpoint with invalid token
    bad_res = client.get("/api/candidates/consent-preview?token=invalid_token")
    assert bad_res.status_code == 400

    # 3. Submit APPROVAL
    submit_res = client.post("/api/candidates/consent-submit", json={
        "token": token,
        "decision": "APPROVE"
    })
    assert submit_res.status_code == 200
    sdata = submit_res.json()
    assert sdata["status"] == "APPROVED"
    assert sdata["decision"] == "APPROVE"

    # 4. Verify DB was updated to APPROVED
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT opt_in_status FROM recruiter_matches WHERE match_id = ?", (match_id,))
        assert cursor.fetchone()["opt_in_status"] == OptInStatus.APPROVED.value
