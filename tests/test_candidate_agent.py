"""
CareerOS Candidate Autonomous Agent Test Suite
==============================================
Verifies dynamic tool-calling, ReAct execution, self-correction,
and streaming event generation for CandidateAutonomousAgent.
"""

import pytest
import asyncio
from engine.agents.candidate_agent import CandidateAutonomousAgent, CandidateAgentTools
from engine.billing.token_ledger import TokenLedgerManager

@pytest.fixture(autouse=True)
def ensure_credits():
    ledger = TokenLedgerManager.get_ledger("alaa_roucadi")
    ledger.balance_credits = 100

def test_candidate_agent_tools_direct():
    # Test semantic search tool
    res = CandidateAgentTools.semantic_search_mandates("AI Delivery Manager Banking", top_k=2)
    assert res["status"] == "SUCCESS"
    assert "matches" in res

    # Test pipeline status tool
    p_res = CandidateAgentTools.pipeline_status()
    assert p_res["status"] == "SUCCESS"
    assert "by_stage" in p_res

    # Test memory query tool
    m_res = CandidateAgentTools.query_market_memory("Salt")
    assert m_res["status"] == "SUCCESS"

@pytest.mark.asyncio
async def test_candidate_agent_react_loop_stream():
    agent = CandidateAutonomousAgent(profile_id="alaa_roucadi")
    chunks = []
    async for chunk in agent.execute_goal_stream("Evaluate JD_30 and check for dealbreakers"):
        chunks.append(chunk)

    body = "".join(chunks)
    # Check that it executed autonomous planning and tool calls
    assert "Autonomous Agent Activated" in body
    assert "dialectic_debate" in body
    assert any("9:{" in c for c in chunks) # Vercel AI SDK Tool Call
    assert any("a:{" in c for c in chunks) # Tool Result
    assert any("d:{" in c for c in chunks) # Finish Message
