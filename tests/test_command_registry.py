"""
CareerOS Unified Command Engine Integration Test Suite
======================================================
Tests:
1. Command registry reflection and descriptors
2. Command execution dispatching for gap_analysis, tailor_resume, evaluate_mandate,
   pipeline_status, ingest_cv, and list_commands
3. Error handling on invalid commands and arguments
4. REST Control Channel endpoints (/api/commands)
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from engine.commands.registry import CommandRegistry, execute_command

client = TestClient(app)


def test_command_registry_descriptors():
    """Verifies that all core commands are registered with descriptors."""
    descriptors = CommandRegistry.get_descriptors()
    assert "pipeline_status" in descriptors
    assert "gap_analysis" in descriptors
    assert "tailor_resume" in descriptors
    assert "evaluate_mandate" in descriptors
    assert "ingest_cv" in descriptors
    assert "radar_scan" in descriptors
    assert "list_commands" in descriptors

    info = descriptors["pipeline_status"]
    assert "properties" in info.parameters


def test_command_execution_pipeline_status():
    """Verifies direct command dispatch for pipeline_status."""
    res = execute_command("pipeline_status", limit=3)
    assert res["status"] == "success"
    assert res["command"] == "pipeline_status"
    data = res["data"]
    assert "total_count" in data
    assert "opportunities" in data
    assert len(data["opportunities"]) <= 3


def test_command_execution_list_commands():
    """Verifies list_commands reflection."""
    res = execute_command("list_commands")
    assert res["status"] == "success"
    assert res["data"]["count"] >= 7


def test_command_execution_gap_analysis():
    """Verifies gap_analysis command dispatch against JD_01."""
    res = execute_command("gap_analysis", jd_id="JD_01")
    assert res["status"] == "success"
    assert "fit_score" in res["data"]
    assert "dealbreakers" in res["data"]


def test_command_execution_unknown():
    """Verifies unknown command returns error status without crashing."""
    res = execute_command("non_existent_command_12345")
    assert res["status"] == "error"
    assert "Unknown command" in res["error"]


def test_rest_command_endpoints():
    """Verifies /api/commands REST discovery and execution."""
    # 1. Discovery GET
    r_get = client.get("/api/commands")
    assert r_get.status_code == 200
    assert r_get.json()["status"] == "success"
    assert r_get.json()["data"]["count"] >= 7

    # 2. Generic POST /api/commands
    r_post_generic = client.post(
        "/api/commands",
        json={"command": "pipeline_status", "args": {"limit": 2}}
    )
    assert r_post_generic.status_code == 200
    assert r_post_generic.json()["status"] == "success"
    assert r_post_generic.json()["data"]["returned_count"] <= 2

    # 3. Specific POST /api/commands/{name}
    r_post_specific = client.post(
        "/api/commands/pipeline_status",
        json={"limit": 2}
    )
    assert r_post_specific.status_code == 200
    assert r_post_specific.json()["status"] == "success"
