"""
CareerOS API Test Suite
=======================
Verifies FastAPI endpoints, CORS headers, REST schemas, and Vercel AI SDK SSE data stream.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_pipeline_opportunities():
    response = client.get("/api/pipeline/opportunities")
    assert response.status_code == 200
    opps = response.json()
    assert isinstance(opps, list)
    if opps:
        assert "id" in opps[0]
        assert "stage" in opps[0]

def test_memory_records():
    response = client.get("/api/memory/records")
    assert response.status_code == 200
    records = response.json()
    assert isinstance(records, list)

def test_chat_stream_evaluate():
    payload = {
        "messages": [
            {"role": "user", "content": "Please evaluate JD_30 with debate"}
        ],
        "profile": "alaa_roucadi"
    }
    with client.stream("POST", "/api/chat", json=payload) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")
        
        chunks = []
        for line in response.iter_lines():
            if line:
                chunks.append(line)
        
        body = "\n".join(chunks)
        # Verify text delta lines (0:"...")
        assert any(l.startswith('0:"') for l in chunks), "Expected text delta streaming format"
        # Verify tool call invocations for Generative UI (9:{"toolCallId":...} or b:{"toolCallId":...})
        assert any(l.startswith('9:{') or l.startswith('b:{') for l in chunks), "Expected tool call invocations for Adaptive UI"
        # Verify finish line
        assert any(l.startswith('d:{') for l in chunks), "Expected finish message in stream"

def test_chat_stream_tailor():
    from engine.billing.token_ledger import TokenLedgerManager
    ledger = TokenLedgerManager.get_ledger("alaa_roucadi")
    ledger.balance_credits = 100

    payload = {
        "messages": [
            {"role": "user", "content": "Tailor resume for JD_30"}
        ],
        "profile": "alaa_roucadi"
    }
    with client.stream("POST", "/api/chat", json=payload) as response:
        assert response.status_code == 200
        chunks = [line for line in response.iter_lines() if line]
        body = "\n".join(chunks)
        assert "TailoredResumeViewer" in body or any("b:{" in l for l in chunks)
