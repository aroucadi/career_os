"""
CareerOS Token Ledger & Anti-Burn Compute Governor Tests
========================================================
Verifies credit allocation, deterministic zero-cost policies,
deduction for heavy operations, and API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from engine.billing.token_ledger import TokenLedgerManager, ActionCost, TokenLedger

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_ledger():
    """Resets test candidate ledger before each test."""
    test_uid = "test_audit_user"
    ledger = TokenLedgerManager.get_ledger(test_uid)
    ledger.balance_credits = 100
    ledger.total_consumed = 0
    ledger.transactions = []
    TokenLedgerManager._save()
    return test_uid

def test_initial_allocation(setup_test_ledger):
    uid = setup_test_ledger
    ledger = TokenLedgerManager.get_ledger(uid)
    assert ledger.balance_credits == 100
    assert ledger.max_credits == 100
    assert ledger.total_consumed == 0

def test_deterministic_zero_cost(setup_test_ledger):
    uid = setup_test_ledger
    assert ActionCost.get_cost("deterministic_check") == 0
    ok, bal, msg = TokenLedgerManager.consume(uid, "deterministic_check")
    assert ok is True
    assert bal == 100

def test_heuristic_debate_deduction(setup_test_ledger):
    uid = setup_test_ledger
    assert ActionCost.get_cost("fast_heuristic_debate") == 5
    ok, bal, msg = TokenLedgerManager.consume(uid, "fast_heuristic_debate", details="Testing debate")
    assert ok is True
    assert bal == 95
    assert TokenLedgerManager.get_ledger(uid).total_consumed == 5

def test_tailor_resume_deduction(setup_test_ledger):
    uid = setup_test_ledger
    assert ActionCost.get_cost("tailor_resume") == 25
    ok, bal, msg = TokenLedgerManager.consume(uid, "tailor_resume", details="Testing resume compile")
    assert ok is True
    assert bal == 75
    assert TokenLedgerManager.get_ledger(uid).total_consumed == 25

def test_insufficient_credits_rejection(setup_test_ledger):
    uid = setup_test_ledger
    ledger = TokenLedgerManager.get_ledger(uid)
    ledger.balance_credits = 10  # Drop balance to 10 EC

    # Tailor resume requires 25 EC -> Should fail gracefully
    assert TokenLedgerManager.can_afford(uid, "tailor_resume") is False
    ok, bal, msg = TokenLedgerManager.consume(uid, "tailor_resume")
    assert ok is False
    assert bal == 10
    assert "Insufficient Energy Credits" in msg

    # But fast heuristic debate (5 EC) should still pass
    assert TokenLedgerManager.can_afford(uid, "fast_heuristic_debate") is True
    ok2, bal2, _ = TokenLedgerManager.consume(uid, "fast_heuristic_debate")
    assert ok2 is True
    assert bal2 == 5

def test_award_bonus_and_claim(setup_test_ledger):
    uid = setup_test_ledger
    new_bal = TokenLedgerManager.award_bonus(uid, 15, reason="Profile completion")
    assert new_bal == 115

def test_api_token_balance_endpoint(setup_test_ledger):
    uid = setup_test_ledger
    response = client.get(f"/api/tokens/balance?user_id={uid}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == uid
    assert "balance_credits" in data
    assert "cost_matrix" in data
    assert data["cost_matrix"]["fast_heuristic_debate"] == 5
    assert data["cost_matrix"]["tailor_resume"] == 25

def test_api_claim_daily_endpoint(setup_test_ledger):
    uid = setup_test_ledger
    response = client.post(f"/api/tokens/claim-daily?user_id={uid}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == uid
    assert data["new_balance"] == 110
    assert "Claimed" in data["message"]
