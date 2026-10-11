"""
CareerOS Model Context Protocol (MCP) Server
============================================
Exposes CareerOS autonomous capabilities as standard MCP tools for
AI clients (Claude Desktop, Cursor, Antigravity, cline, etc.).

Tools exposed:
- gap_analysis: Strategic candidate gap analysis against a JD
- tailor_resume: Tailor resume and compile A4 PDF
- evaluate_mandate: Dialectic debate (Prosecutor vs Advocate vs Arbiter)
- pipeline_status: Recruitment pipeline CRM state and metrics
- ingest_cv: Parse and index candidate CV into Talent Lake
- radar_scan: Autonomous job radar scraping and evaluation
- list_commands: Self-describing schema of available CareerOS commands
"""

import sys
import json
import logging
from typing import Optional, Dict, Any, List
from mcp.server.mcpserver import MCPServer
from engine.commands.registry import execute_command

logger = logging.getLogger("careeros.mcp")

# Initialize CareerOS MCP Server
mcp_server = MCPServer("CareerOS")


@mcp_server.tool(name="gap_analysis", description="Analyze candidate gaps against a target JD or mandate, returning fit scores, dealbreakers, and proof metrics.")
def gap_analysis(
    jd_id: str,
    cv_text: Optional[str] = None,
    profile_id: Optional[str] = None,
    use_cache: bool = True
) -> str:
    """Runs strategic gap analysis of candidate resume against a target job description."""
    res = execute_command(
        "gap_analysis",
        jd_id=jd_id,
        cv_text=cv_text,
        profile_id=profile_id,
        use_cache=use_cache
    )
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp_server.tool(name="tailor_resume", description="Synthesizes a tailored markdown resume and compiles it to pixel-perfect A4 PDF for a target job.")
def tailor_resume(
    jd_id: str,
    profile_id: Optional[str] = None,
    fast: bool = True,
    llm: bool = False
) -> str:
    """Synthesizes a tailored markdown resume and compiles it to PDF."""
    res = execute_command(
        "tailor_resume",
        jd_id=jd_id,
        profile_id=profile_id,
        fast=fast,
        llm=llm
    )
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp_server.tool(name="evaluate_mandate", description="Executes a dialectic multi-agent debate (Prosecutor vs Advocate vs Arbiter) on an opportunity.")
def evaluate_mandate(
    jd_id: str,
    profile_id: Optional[str] = None,
    llm: bool = False,
    career_mode: str = "freelance"
) -> str:
    """Executes a dialectic multi-agent debate on an opportunity."""
    res = execute_command(
        "evaluate_mandate",
        jd_id=jd_id,
        profile_id=profile_id,
        llm=llm,
        career_mode=career_mode
    )
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp_server.tool(name="pipeline_status", description="Retrieves recruitment pipeline CRM status, stages, metrics, and active opportunity cards.")
def pipeline_status(
    stage: Optional[str] = None,
    limit: int = 20
) -> str:
    """Retrieves recruitment pipeline status and active opportunity cards."""
    res = execute_command(
        "pipeline_status",
        stage=stage,
        limit=limit
    )
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp_server.tool(name="ingest_cv", description="Parses candidate CV text or file into structured profile, extracts telemetry metrics, and indexes into Talent Lake.")
def ingest_cv(
    cv_text: Optional[str] = None,
    file_path: Optional[str] = None,
    career_mode: str = "freelance"
) -> str:
    """Parses candidate CV text or file into structured profile."""
    res = execute_command(
        "ingest_cv",
        cv_text=cv_text,
        file_path=file_path,
        career_mode=career_mode
    )
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp_server.tool(name="radar_scan", description="Executes autonomous job radar scraping & scoring across job boards with candidate matching.")
def radar_scan(
    query: Optional[str] = None,
    location: str = "Worldwide",
    remote: bool = True,
    limit: int = 5
) -> str:
    """Executes autonomous job radar scraping & scoring across job boards."""
    res = execute_command(
        "radar_scan",
        query=query,
        location=location,
        remote=remote,
        limit=limit
    )
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp_server.tool(name="list_commands", description="Returns JSON metadata and schemas for all available CareerOS commands.")
def list_commands() -> str:
    """Returns metadata and JSON schemas for all available CareerOS commands."""
    res = execute_command("list_commands")
    return json.dumps(res, indent=2, ensure_ascii=False)


def run_stdio():
    """Runs the CareerOS MCP server over standard I/O (stdio)."""
    mcp_server.run(transport="stdio")


if __name__ == "__main__":
    run_stdio()
