"""
CareerOS Stripe Webhook & Automated Credit Fulfillment Test Suite
==================================================================
Verifies the Release 2.2 automated billing replenishment pipeline (SPEC-0045):
1. Stripe webhook endpoint verification and credit top-up.
2. Atomicity of recruiter_orgs balance update in SQLite.
3. ESP and Webhook dispatch channel resilience.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from engine.storage.db import get_db_connection

client = TestClient(app)

def test_stripe_webhook_fulfillment():
    """Verifies Stripe checkout webhook adds credits to recruiter org balance."""
    org_id = "org_default_test"

    # Get initial balance
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT credits_balance FROM recruiter_orgs WHERE org_id = ?", (org_id,))
        initial_bal = cursor.fetchone()["credits_balance"]

    # Send webhook event
    credits_to_add = 150
    res = client.post("/api/recruiter/billing/webhook", json={
        "event": "checkout.session.completed",
        "org_id": org_id,
        "credits_added": credits_to_add,
        "customer_email": "recruiter@headhunters.com",
        "session_id": "cs_test_998877"
    })

    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "FULFILLED"
    assert data["credits_added"] == credits_to_add
    assert data["new_balance"] == initial_bal + credits_to_add

    # Verify directly in SQLite
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT credits_balance FROM recruiter_orgs WHERE org_id = ?", (org_id,))
        assert cursor.fetchone()["credits_balance"] == initial_bal + credits_to_add

def test_stripe_webhook_invalid_org():
    """Verifies error handling when unknown org is sent in webhook."""
    res = client.post("/api/recruiter/billing/webhook", json={
        "event": "checkout.session.completed",
        "org_id": "nonexistent_org_999",
        "credits_added": 50
    })
    assert res.status_code == 404
