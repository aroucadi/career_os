"""
CareerOS Unified Command Registry
=================================
Central command dispatch engine unifying CLI, REST control channel,
MCP server, and Web UI/Agent chat interfaces into deterministic,
typed career operating system actions.

Supported Core Commands:
  - gap_analysis: Strategic gap assessment against target JDs with composite scoring
  - tailor_resume: Precision bullet tailoring and pixel-perfect PDF compilation
  - evaluate_mandate: Dialectic debate (Prosecutor vs Advocate vs Arbiter)
  - pipeline_status: Pipeline CRM status, transitions, and stage breakdowns
  - ingest_cv: Candidate self-serve parsing, telemetry extraction & database indexing
  - radar_scan: Autonomous market radar job search and scoring
  - list_commands: Self-describing schema of all registered capabilities
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from pydantic import BaseModel, Field

logger = logging.getLogger("careeros.commands")

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class CommandDescriptor(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    examples: List[Dict[str, Any]] = Field(default_factory=list)


class CommandRegistry:
    """Central registry and execution dispatcher for CareerOS commands."""

    _commands: Dict[str, Callable] = {}
    _descriptors: Dict[str, CommandDescriptor] = {}

    @classmethod
    def register(cls, name: str, description: str, parameters: Dict[str, Any], examples: Optional[List[Dict[str, Any]]] = None):
        """Decorator to register a command handler."""
        def decorator(func: Callable):
            cls._commands[name] = func
            cls._descriptors[name] = CommandDescriptor(
                name=name,
                description=description,
                parameters=parameters,
                examples=examples or []
            )
            return func
        return decorator

    @classmethod
    def get_descriptors(cls) -> Dict[str, CommandDescriptor]:
        """Returns all command descriptors for schema reflection and MCP tools."""
        return cls._descriptors

    @classmethod
    def dispatch(cls, command_name: str, **kwargs) -> Dict[str, Any]:
        """
        Dispatches a command deterministically and returns a structured dictionary result.
        Always returns a dict with status ("success" or "error"), command name, and data/error message.
        """
        if command_name not in cls._commands:
            available = list(cls._commands.keys())
            return {
                "status": "error",
                "command": command_name,
                "error": f"Unknown command '{command_name}'. Available commands: {available}"
            }

        handler = cls._commands[command_name]
        try:
            result = handler(**kwargs)
            return {
                "status": "success",
                "command": command_name,
                "data": result
            }
        except Exception as e:
            logger.exception(f"Error executing command '{command_name}': {e}")
            return {
                "status": "error",
                "command": command_name,
                "error": str(e)
            }


# ─────────────────────────────────────────────────────────────────────────────
# 1. Command: gap_analysis
# ─────────────────────────────────────────────────────────────────────────────
@CommandRegistry.register(
    name="gap_analysis",
    description="Runs strategic gap analysis of candidate resume against a target job description or directory.",
    parameters={
        "type": "object",
        "properties": {
            "jd_id": {"type": "string", "description": "Target JD identifier, filename (e.g. 01_Head_of_AI.md), or keyword"},
            "cv_text": {"type": "string", "description": "Optional raw CV text override"},
            "profile_id": {"type": "string", "description": "Candidate profile ID (defaults to active candidate)"},
            "use_cache": {"type": "boolean", "description": "Whether to use cached evaluations if available", "default": True}
        },
        "required": ["jd_id"]
    },
    examples=[{"jd_id": "01_Head_of_AI.md"}]
)
def cmd_gap_analysis(jd_id: str, cv_text: Optional[str] = None, profile_id: Optional[str] = None, use_cache: bool = True) -> Dict[str, Any]:
    from engine.profiles.manager import ProfileManager
    from engine.prompts.context_assembler import resolve_jd_file

    cand_prof = ProfileManager.load_profile(profile_id)
    jd_path = resolve_jd_file(jd_id)
    jd_content = jd_path.read_text(encoding="utf-8")
    jd_title = jd_path.stem.replace("_", " ").title()

    if not cv_text:
        cv_file = _ROOT_DIR / cand_prof.resume_file
        if not cv_file.exists():
            alt = _ROOT_DIR / "resumes" / cand_prof.resume_file
            if alt.exists():
                cv_file = alt
        if cv_file.exists():
            cv_text = cv_file.read_text(encoding="utf-8")
        else:
            cv_text = f"Candidate: {cand_prof.full_name}\nHeadline: {cand_prof.headline}\nSummary: {cand_prof.positioning_statement}"

    # Fast heuristic gap calculation + rubric mapping
    from engine.evaluators.debate.runner import DebateRunner
    runner = DebateRunner(profile=cand_prof)
    transcript = runner.run_fast_heuristic_debate(jd_id=jd_path.name, jd_title=jd_title, jd_text=jd_content)

    return {
        "jd_id": jd_path.name,
        "jd_title": jd_title,
        "candidate": cand_prof.full_name,
        "fit_score": transcript.arbitration.fit_score,
        "quality_gate_score": transcript.arbitration.critic_quality_score,
        "final_verdict": transcript.arbitration.final_verdict,
        "dealbreakers": [d.model_dump() for d in transcript.indictment.dealbreakers],
        "red_flags": transcript.indictment.unspoken_red_flags,
        "rebuttal_points": transcript.defense.rebuttal_points,
        "proof_metrics": transcript.defense.grounded_proof_citations,
        "negotiation_hook": transcript.defense.negotiation_hook,
        "rationale": transcript.arbitration.decision_rationale,
        "binding_conditions": transcript.arbitration.binding_conditions
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. Command: tailor_resume
# ─────────────────────────────────────────────────────────────────────────────
@CommandRegistry.register(
    name="tailor_resume",
    description="Synthesizes a tailored, ATS-optimized markdown resume and compiles it to pixel-perfect A4 PDF.",
    parameters={
        "type": "object",
        "properties": {
            "jd_id": {"type": "string", "description": "Target JD identifier (e.g. '01_Head_of_AI' or 'abu_dhabi')"},
            "profile_id": {"type": "string", "description": "Candidate profile ID (defaults to active candidate)"},
            "fast": {"type": "boolean", "description": "Use ultra-fast template synthesis mode (default True)", "default": True},
            "llm": {"type": "boolean", "description": "Use LLM model for deep contextual re-architecting", "default": False}
        },
        "required": ["jd_id"]
    },
    examples=[{"jd_id": "01_Head_of_AI.md", "fast": True}]
)
def cmd_tailor_resume(jd_id: str, profile_id: Optional[str] = None, fast: bool = True, llm: bool = False) -> Dict[str, Any]:
    from engine.compiler.tailor import ResumeTailor
    from engine.profiles.manager import ProfileManager
    from engine.prompts.context_assembler import resolve_jd_file

    cand_prof = ProfileManager.load_profile(profile_id)
    jd_path = resolve_jd_file(jd_id)
    jd_text = jd_path.read_text(encoding="utf-8")
    jd_title = jd_path.stem.replace("_", " ").title()

    tailor = ResumeTailor(profile=cand_prof)
    mode = "llm" if llm else "fast"
    result = tailor.tailor_and_compile(
        jd_id=jd_path.stem,
        jd_title=jd_title,
        jd_text=jd_text,
        mode=mode
    )
    return result


# ─────────────────────────────────────────────────────────────────────────────
# 3. Command: evaluate_mandate
# ─────────────────────────────────────────────────────────────────────────────
@CommandRegistry.register(
    name="evaluate_mandate",
    description="Executes a dialectic multi-agent debate (Prosecutor vs Advocate vs Arbiter) on an opportunity.",
    parameters={
        "type": "object",
        "properties": {
            "jd_id": {"type": "string", "description": "Target JD identifier or filename"},
            "profile_id": {"type": "string", "description": "Candidate profile ID"},
            "llm": {"type": "boolean", "description": "Whether to run multi-turn LLM agent debate or heuristic debate", "default": False},
            "career_mode": {"type": "string", "description": "Career track: freelance, employee, or fractional", "default": "freelance"}
        },
        "required": ["jd_id"]
    },
    examples=[{"jd_id": "01_Head_of_AI.md", "career_mode": "freelance"}]
)
def cmd_evaluate_mandate(jd_id: str, profile_id: Optional[str] = None, llm: bool = False, career_mode: str = "freelance") -> Dict[str, Any]:
    import asyncio
    from engine.evaluators.debate.runner import DebateRunner
    from engine.profiles.manager import ProfileManager
    from engine.prompts.context_assembler import resolve_jd_file

    cand_prof = ProfileManager.load_profile(profile_id)
    jd_path = resolve_jd_file(jd_id)
    jd_text = jd_path.read_text(encoding="utf-8")
    jd_title = jd_path.stem.replace("_", " ").title()

    runner = DebateRunner(profile=cand_prof)
    if llm:
        transcript = asyncio.run(runner.run_llm_debate(jd_id=jd_path.name, jd_title=jd_title, jd_text=jd_text, career_mode=career_mode))
    else:
        transcript = runner.run_fast_heuristic_debate(jd_id=jd_path.name, jd_title=jd_title, jd_text=jd_text, career_mode=career_mode)

    return transcript.model_dump()


# ─────────────────────────────────────────────────────────────────────────────
# 4. Command: pipeline_status
# ─────────────────────────────────────────────────────────────────────────────
@CommandRegistry.register(
    name="pipeline_status",
    description="Retrieves current recruitment pipeline status, stages, metrics, and active opportunity cards.",
    parameters={
        "type": "object",
        "properties": {
            "stage": {"type": "string", "description": "Filter by pipeline stage (e.g. INBOX, EVALUATED, APPLIED, INTERVIEW)"},
            "limit": {"type": "integer", "description": "Maximum records to return", "default": 20}
        }
    },
    examples=[{"stage": "EVALUATED"}]
)
def cmd_pipeline_status(stage: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    from engine.pipeline.repository import PipelineRepository

    repo = PipelineRepository()
    opportunities = repo.list_all(stage_filter=stage)
    total_count = len(opportunities)
    subset = opportunities[:limit]

    stage_breakdown: Dict[str, int] = {}
    for opp in opportunities:
        st = opp.stage.value if hasattr(opp.stage, "value") else str(opp.stage)
        stage_breakdown[st] = stage_breakdown.get(st, 0) + 1

    return {
        "total_count": total_count,
        "returned_count": len(subset),
        "stage_breakdown": stage_breakdown,
        "opportunities": [
            {
                "id": opp.id,
                "company": opp.company,
                "job_title": opp.job_title,
                "stage": opp.stage.value if hasattr(opp.stage, "value") else str(opp.stage),
                "overall_score": opp.evaluation.overall_score if opp.evaluation else None,
                "target_rate": opp.persona_intel.candidate.target_rate_eur if (opp.persona_intel and opp.persona_intel.candidate) else "",
                "location": opp.location,
                "url": opp.url
            }
            for opp in subset
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. Command: ingest_cv
# ─────────────────────────────────────────────────────────────────────────────
@CommandRegistry.register(
    name="ingest_cv",
    description="Parses candidate CV text or file into structured profile, extracts telemetry metrics, and indexes into Talent Lake.",
    parameters={
        "type": "object",
        "properties": {
            "cv_text": {"type": "string", "description": "Raw resume text content"},
            "file_path": {"type": "string", "description": "Path to resume file (.md, .txt, .pdf)"},
            "career_mode": {"type": "string", "description": "Preferred mode: freelance, employee, fractional", "default": "freelance"}
        }
    },
    examples=[{"cv_text": "Jean-Luc Picard\nSenior AI Delivery Lead\nParis, France\n..."}]
)
def cmd_ingest_cv(cv_text: Optional[str] = None, file_path: Optional[str] = None, career_mode: str = "freelance") -> Dict[str, Any]:
    from engine.profiles.extractor import ResumeExtractor

    if file_path and not cv_text:
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        cv_text = p.read_text(encoding="utf-8", errors="replace")

    if not cv_text or not cv_text.strip():
        raise ValueError("Either cv_text or file_path must be provided with valid content.")

    profile = ResumeExtractor.ingest_and_save(cv_text, preferred_mode=career_mode)
    return {
        "profile_id": profile.id,
        "full_name": profile.full_name,
        "headline": profile.headline,
        "contact_email": profile.contact_email,
        "location": profile.mobility.base_location if profile.mobility else "",
        "freelance_tjm": profile.commercials.freelance_tjm_eur if profile.commercials else "",
        "proof_metrics_count": len(profile.proof_metrics or []),
        "proof_metrics": [m.evidence for m in (profile.proof_metrics or [])[:5]]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. Command: radar_scan
# ─────────────────────────────────────────────────────────────────────────────
@CommandRegistry.register(
    name="radar_scan",
    description="Executes autonomous job radar scraping & scoring across job boards with candidate matching.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search keyword query (e.g. 'Head of AI', 'Director GenAI')"},
            "location": {"type": "string", "description": "Target geographic location or 'Worldwide'", "default": "Worldwide"},
            "remote": {"type": "boolean", "description": "Filter for remote-first roles", "default": True},
            "limit": {"type": "integer", "description": "Maximum jobs to scrape and score", "default": 5}
        }
    },
    examples=[{"query": "Head of AI", "remote": True, "limit": 3}]
)
def cmd_radar_scan(query: Optional[str] = None, location: str = "Worldwide", remote: bool = True, limit: int = 5) -> Dict[str, Any]:
    from career_radar.radar_agent import RadarAgent

    queries = [q.strip() for q in query.split(",")] if query else None
    agent = RadarAgent()
    try:
        scored_jobs = agent.scan_and_score(
            queries=queries,
            location=location,
            remote=remote,
            limit_per_query=limit
        )
        return {
            "jobs_found_and_scored": len(scored_jobs),
            "jobs": [
                {
                    "title": j.job_title,
                    "company": j.company,
                    "location": j.location,
                    "overall_match_score": j.overall_match_score,
                    "url": j.url,
                    "ats_keyword_gaps": j.ats_keyword_gaps,
                    "recruiter_pitch_hook": j.recruiter_pitch_hook
                }
                for j in scored_jobs
            ]
        }
    finally:
        agent.close()


# ─────────────────────────────────────────────────────────────────────────────
# 7. Command: list_commands
# ─────────────────────────────────────────────────────────────────────────────
@CommandRegistry.register(
    name="list_commands",
    description="Returns metadata and JSON schemas for all available CareerOS commands.",
    parameters={"type": "object", "properties": {}},
    examples=[{}]
)
def cmd_list_commands() -> Dict[str, Any]:
    descriptors = CommandRegistry.get_descriptors()
    return {
        "count": len(descriptors),
        "commands": [d.model_dump() for d in descriptors.values()]
    }


def execute_command(command_name: str, **kwargs) -> Dict[str, Any]:
    """Helper entry point for direct script and library callers."""
    return CommandRegistry.dispatch(command_name, **kwargs)
