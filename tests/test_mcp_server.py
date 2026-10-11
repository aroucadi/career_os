"""
CareerOS Model Context Protocol (MCP) Server Integration Tests
==============================================================
Verifies that CareerOS MCP Server initializes, registers all tools,
and executes tool calls cleanly via the MCP Server SDK.
"""

import json
import pytest
import anyio
from engine.mcp.server import mcp_server


@pytest.mark.anyio
async def test_mcp_server_tools_registered():
    """Verifies that all 7 core tools are properly registered on the MCPServer."""
    tools = await mcp_server.list_tools()
    tool_names = [t.name for t in tools]

    expected = [
        "gap_analysis",
        "tailor_resume",
        "evaluate_mandate",
        "pipeline_status",
        "ingest_cv",
        "radar_scan",
        "list_commands"
    ]
    for exp in expected:
        assert exp in tool_names, f"Expected MCP tool '{exp}' not found in registered tools: {tool_names}"


@pytest.mark.anyio
async def test_mcp_server_call_pipeline_status():
    """Verifies direct invocation of pipeline_status via mcp_server.call_tool."""
    res = await mcp_server.call_tool("pipeline_status", {"limit": 2})
    assert not res.is_error

    # Text content returned by MCPServer tool
    text_content = res.content[0].text
    parsed = json.loads(text_content)
    assert parsed["status"] == "success"
    assert parsed["command"] == "pipeline_status"
    assert parsed["data"]["returned_count"] <= 2


@pytest.mark.anyio
async def test_mcp_server_call_list_commands():
    """Verifies call_tool on list_commands."""
    res = await mcp_server.call_tool("list_commands", {})
    assert not res.is_error
    text_content = res.content[0].text
    parsed = json.loads(text_content)
    assert parsed["status"] == "success"
    assert parsed["data"]["count"] >= 7
