"""
CareerOS Recruiter Delegation & Double Opt-In End-to-End Test Suite
===================================================================
Verifies the complete B2B demand loop (SPEC-0042):
1. Requisition decomposition into Eliminators vs Multipliers.
2. Multi-candidate scoring and ranking across the Talent Intelligence Lake.
3. Strict Double Opt-In privacy gate (PII blurred until candidate approval).
4. Executive Dossier generation and paywall access control.
5. Fallback chat token metering (1 EC per unstructured turn).
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from engine.recruiter.models import OptInStatus, RequisitionSpec
from engine.recruiter.matcher import RequisitionMatcher
from engine.recruiter.dossier import ExecutiveDossierCompiler
from engine.talent_graph.store import TalentLakeStore
from engine.billing.token_ledger import TokenLedgerManager

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_talent_lake():
    """Ensures multi-persona talent pool is seeded."""
    TalentLakeStore.seed_default_talent_pool()

def test_requisition_decomposition():
    jd_sample = """
    # Head of AI Adoption & Platform Delivery
    Location: Paris (Hybrid, 2 days per week)
    Requirements:
    - Mandatory French fluent
    - Deep hands-on experience with EU AI Act & Responsible AI production gates
    - Proven multi-squad engineering governance across banking tribes
    """
    req = RequisitionMatcher.decompose_requisition(
        job_title="Head of AI Adoption & Platform Delivery",
        jd_text=jd_sample,
        company="Tier-1 Bank"
    )

    assert req.job_title == "Head of AI Adoption & Platform Delivery"
    assert any("French" in e for e in req.mandatory_eliminators)
    assert any("EU AI Act" in m for m in req.preferred_multipliers)
    assert any("Multi-Squad" in m for m in req.preferred_multipliers)

def test_talent_lake_candidate_matching():
    jd_sample = """
    # AI Delivery Lead & Operating Model Architect
    Client: Global Investment Banking Group
    Looking for a Senior Director to lead our AI Center of Excellence across 7 squads.
    Must ensure full EU AI Act compliance and agentic SDLC tooling rollouts.
    """
    slate = RequisitionMatcher.match_requisition(
        job_title="AI Delivery Lead",
        jd_text=jd_sample,
        company="Global Investment Banking Group",
        min_score=60.0
    )

    assert len(slate) >= 1
    top_candidate = slate[0]
    # Alaa should rank at the top for Banking AI CoE + EU AI Act
    assert top_candidate.overall_match_score >= 80.0
    assert any("Candidate #" in top_candidate.anonymized_alias for top_candidate in slate)
    # Ensure candidate PII is NOT in the public alias
    assert "Alaa" not in top_candidate.anonymized_alias
    assert "roucadi" not in top_candidate.anonymized_alias.lower()
    assert top_candidate.opt_in_status == OptInStatus.PENDING_CONSENT

def test_double_opt_in_privacy_lifecycle():
    # 1. Generate match
    slate = RequisitionMatcher.match_requisition(
        job_title="Director of Internal Audit & Risk",
        jd_text="Leading SOX 404 audit automation, ITGC controls, and committee reporting.",
        company="Fintech Scaleup"
    )
    assert len(slate) >= 1
    match = slate[0]

    # 2. Before consent: Dossier MUST BE LOCKED and PII stripped
    locked_dossier = ExecutiveDossierCompiler.compile_dossier(match)
    assert locked_dossier.access_status == "LOCKED"
    assert locked_dossier.unlocked_full_name is None
    assert locked_dossier.unlocked_email is None
    assert locked_dossier.unlocked_linkedin is None
    assert len(locked_dossier.custom_interview_cheatsheet) == 5

    # 3. Recruiter requests warm introduction
    res_req = client.post("/api/recruiter/request-intro", json={
        "match_id": match.match_id,
        "recruiter_notes": "We would love to interview this candidate this week."
    })
    assert res_req.status_code == 200
    assert res_req.json()["status"] == "INTRODUCTION_REQUESTED"

    # 4. Candidate Consents (APPROVE) -> Dossier & PII unlock
    res_consent = client.post("/api/candidates/opt-in", json={
        "match_id": match.match_id,
        "decision": "APPROVE"
    })
    assert res_consent.status_code == 200
    assert res_consent.json()["status"] == "APPROVED"
    unlocked_dossier = res_consent.json()["dossier"]
    assert unlocked_dossier["access_status"] == "UNLOCKED"
    assert unlocked_dossier["unlocked_full_name"] is not None
    assert unlocked_dossier["unlocked_email"] is not None
    assert "@" in unlocked_dossier["unlocked_email"]

def test_candidate_decline_keeps_pii_locked():
    slate = RequisitionMatcher.match_requisition(
        job_title="Fractional CTO",
        jd_text="Series A startup looking for a high-impact technical advisor.",
        company="Seed Ventures"
    )
    match = slate[0]

    # Candidate Declines
    res_decline = client.post("/api/candidates/opt-in", json={
        "match_id": match.match_id,
        "decision": "DECLINE"
    })
    assert res_decline.status_code == 200
    assert res_decline.json()["status"] == "DECLINED"

    # Verify dossier remains locked
    res_dossier = client.get(f"/api/recruiter/dossier/{match.match_id}")
    assert res_dossier.status_code == 200
    data = res_dossier.json()
    assert data["access_status"] == "LOCKED"
    assert data["unlocked_full_name"] is None
    assert data["unlocked_email"] is None

def test_recruiter_match_api_endpoint():
    payload = {
        "job_title": "Head of AI Adoption",
        "jd_text": "Enterprise AI operating model transformation and multi-squad CoE governance in banking.",
        "company": "Salt Middle East",
        "min_score": 65.0
    }
    response = client.post("/api/recruiter/match", json=payload)
    assert response.status_code == 200
    slate = response.json()
    assert isinstance(slate, list)
    assert len(slate) >= 1
    assert "overall_match_score" in slate[0]
    assert "rubric_subscores" in slate[0]

def test_general_chat_token_metering():
    # Verify deduction of 1 EC on unstructured turns
    uid = "test_chat_metering_user"
    ledger = TokenLedgerManager.get_ledger(uid)
    ledger.balance_credits = 100
    TokenLedgerManager._save()

    ok, bal, msg = TokenLedgerManager.consume(uid, "general_chat_turn", details="Testing 1 EC deduction")
    assert ok is True
    assert bal == 99

    # Set balance to 0 EC -> should reject
    ledger.balance_credits = 0
    TokenLedgerManager._save()
    ok_depleted, bal_depleted, msg_depleted = TokenLedgerManager.consume(uid, "general_chat_turn")
    assert ok_depleted is False
    assert bal_depleted == 0
    assert "Insufficient Energy Credits" in msg_depleted
