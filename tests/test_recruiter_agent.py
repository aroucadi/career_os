"""
CareerOS Recruiter Autonomous Sourcing Agent Test Suite
======================================================
Verifies natural language brief decomposition, candidate slate ranking,
tactical interview question generation, cryptographic double opt-in dispatch,
and Vercel AI SDK streaming execution for RecruiterAutonomousAgent.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from engine.agents.recruiter_agent import RecruiterAutonomousAgent, RecruiterAgentTools
from engine.billing.recruiter_billing import RecruiterBillingManager
from engine.recruiter.models import OptInStatus
from api.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def ensure_recruiter_credits():
    from engine.storage.db import get_db_connection
    with get_db_connection() as conn:
        conn.execute("UPDATE recruiter_orgs SET credits_balance = 500 WHERE org_id = 'org_default_test'")

def test_recruiter_agent_brief_decomposition():
    brief = (
        "We are urgently looking for a Head of AI Adoption at Salt Middle East Abu Dhabi. "
        "Candidate must have deep expertise in EU AI Act governance and managing 5+ engineering squads."
    )
    res = RecruiterAgentTools.parse_and_decompose_brief(brief)
    assert res["status"] == "SUCCESS"
    assert "Head of AI Adoption" in res["job_title"]
    assert "Salt" in res["company"] or "Abu Dhabi" in res["company"]
    assert any("EU AI Act" in m for m in res["value_multipliers"])
    assert any("squad" in m.lower() for m in res["value_multipliers"])

def test_recruiter_agent_slate_and_interview_questions():
    # 1. Slate ranking
    slate = RecruiterAgentTools.rank_candidate_slate(
        job_title="Head of AI Adoption",
        jd_text="Enterprise AI transformation, multi-squad governance, bank CoE",
        company="Salt Middle East",
        min_score=50.0
    )
    assert slate["status"] == "SUCCESS"
    assert slate["total_matches"] > 0
    top = slate["candidates"][0]
    assert top["overall_match_score"] > 60.0
    assert len(top["verified_proof_citations"]) > 0

    # 2. Interview cheatsheet generation
    qa = RecruiterAgentTools.generate_interview_cheatsheet(
        candidate_alias=top["anonymized_alias"],
        headline=top["headline"],
        job_title="Head of AI Adoption",
        proofs=top["verified_proof_citations"]
    )
    assert qa["status"] == "SUCCESS"
    assert len(qa["tactical_questions"]) == 3
    assert any("Governance" in q["category"] for q in qa["tactical_questions"])

def test_recruiter_agent_double_opt_in_dispatch():
    slate = RecruiterAgentTools.rank_candidate_slate(
        job_title="AI Solutions Architect",
        jd_text="Enterprise cloud & AI governance",
        company="Fintech Corp"
    )
    assert slate["total_matches"] > 0
    match_id = slate["candidates"][0]["match_id"]

    dispatch_res = RecruiterAgentTools.dispatch_double_opt_in(
        match_id=match_id,
        recruiter_notes="Client interested in rapid interview loop."
    )
    assert dispatch_res["status"] == "SUCCESS"
    assert dispatch_res["opt_in_status"] == "PENDING_CONSENT"
    assert dispatch_res["token"].startswith("cst_")
    assert "consent_token=" in dispatch_res["consent_url"]

@pytest.mark.asyncio
async def test_recruiter_agent_sourcing_stream():
    agent = RecruiterAutonomousAgent(org_id="org_default_test", api_key="cr_live_test123")
    brief = "Looking for an Enterprise AI Delivery Manager to lead multi-squad banking deployment. Please reach out to top candidate."
    
    chunks = []
    async for chunk in agent.execute_sourcing_stream(brief=brief):
        chunks.append(chunk)

    body = "".join(chunks)
    assert "Recruiter Sourcing Agent Activated" in body
    assert "RecruiterBriefDecompositionCard" in body
    assert "CandidateMatchSlateViewer" in body
    assert "InterviewTacticalQuestionsCard" in body
    assert any("9:{" in c for c in chunks)  # Tool Call
    assert any("a:{" in c for c in chunks)  # Tool Result
    assert any("d:{" in c for c in chunks)  # Finish Message

def test_recruiter_agent_api_endpoint():
    payload = {
        "brief": "Seeking Head of AI Adoption for enterprise bank in Paris. Reach out to the top match.",
        "org_id": "org_default_test",
        "api_key": "cr_live_test123"
    }
    response = client.post("/api/recruiter/agent/source", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "Recruiter Sourcing Agent Activated" in response.text
