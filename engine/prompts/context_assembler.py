"""
CareerOS Context Assembler
==========================
Dynamically synthesizes target JD, candidate master resume, verified executive
telemetry, and anti-delusion constraints into the canonical 7-step evaluation prompt.
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, Any

from engine.profiles.models import CandidateProfile
from engine.profiles.manager import ProfileManager

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
_TEMPLATE_PATH = _ROOT_DIR / "06_PROMPT_COMPONENTS" / "PC_JD_Strategic_Evaluation.md"
_TARGET_JDS_DIR = _ROOT_DIR / "07_TARGET_JDS"


def resolve_jd_file(identifier: str) -> Path:
    """Resolves a JD file by full name, partial number, or stem."""
    p = _TARGET_JDS_DIR / identifier
    if p.exists() and p.is_file():
        return p

    p = Path(identifier)
    if p.exists() and p.is_file():
        return p

    clean_id = identifier.replace(".md", "")
    matches = list(_TARGET_JDS_DIR.glob(f"*{clean_id}*.md"))
    if matches:
        return matches[0]

    # Also check evals/test_jds/ directory
    eval_jds_dir = _ROOT_DIR / "evals" / "test_jds"
    if eval_jds_dir.exists():
        eval_p = eval_jds_dir / identifier
        if eval_p.exists() and eval_p.is_file():
            return eval_p
        eval_matches = list(eval_jds_dir.glob(f"*{clean_id}*.md"))
        if eval_matches:
            return eval_matches[0]

    raise FileNotFoundError(f"Target JD '{identifier}' could not be resolved in {_TARGET_JDS_DIR} or {eval_jds_dir}")


def assemble_evaluation_prompt(
    jd_identifier: str,
    pitch_type: str = "recruiter_counter_proposal",
    resume_path: Optional[Path] = None,
    profile: Optional[CandidateProfile] = None
) -> Dict[str, Any]:
    """Assembles the complete context payload and fully bound evaluation prompt."""
    # Resolve active candidate profile
    cand_profile = profile or ProfileManager.load_profile()

    jd_file = resolve_jd_file(jd_identifier)
    jd_content = jd_file.read_text(encoding="utf-8")

    # Resolve resume file
    if resume_path:
        cv_file = resume_path
    else:
        cv_file = _ROOT_DIR / cand_profile.resume_file
        if not cv_file.exists():
            # Try searching inside resumes/ directory
            cand_alt = _ROOT_DIR / "resumes" / cand_profile.resume_file
            if cand_alt.exists():
                cv_file = cand_alt

    if not cv_file.exists():
        raise FileNotFoundError(f"Resume file '{cv_file}' not found.")

    # Dynamically format profile summary and verified proof metrics
    profile_summary_lines = [
        f"{cand_profile.full_name} — {cand_profile.headline}",
        f"Domains: {', '.join(cand_profile.scope.core_domains)}",
        "Verified Metrics & Key Proof Telemetry:"
    ]
    for pm in cand_profile.proof_metrics:
        profile_summary_lines.append(f"- {pm.category} ({pm.label}): {pm.evidence}")
    profile_summary = "\n".join(profile_summary_lines)

    candidate_constraints = cand_profile.to_prompt_constraints()

    template = _TEMPLATE_PATH.read_text(encoding="utf-8")

    pitch_label_map = {
        "recruiter": "Recruiter Counter-Proposal / Headhunter Outreach Pitch",
        "recruiter_counter_proposal": "Recruiter Counter-Proposal / Headhunter Outreach Pitch",
        "direct": "Direct Hiring Manager Cover Application Pitch",
        "direct_application": "Direct Hiring Manager Cover Application Pitch",
        "linkedin": "Short 150-Word LinkedIn InMail Outreach Message",
        "linkedin_inmail": "Short 150-Word LinkedIn InMail Outreach Message",
    }
    pitch_description = pitch_label_map.get(pitch_type.lower(), pitch_type)

    # Query Episodic Memory Store for historical precedents
    from engine.memory.store import EpisodicMemoryStore
    mem_store = EpisodicMemoryStore()
    
    # Try to extract company name from JD filename or text
    company_hint = ""
    parts = jd_file.stem.split("_")
    if len(parts) >= 3:
        company_hint = parts[-1]
    precedents_context = mem_store.format_precedents_context(
        company=company_hint,
        role_title=jd_file.stem.replace("_", " ")
    )

    prompt = template
    prompt = prompt.replace("{{JD_IDENTIFIER}}", jd_file.name)
    prompt = prompt.replace("{{RESUME_VERSION}}", cv_file.name)
    prompt = prompt.replace("{{CANDIDATE_PROFILE_SUMMARY}}", profile_summary)
    prompt = prompt.replace("{{CANDIDATE_HARD_CONSTRAINTS}}", candidate_constraints)
    prompt = prompt.replace("{{JD_CONTENT}}", jd_content)
    prompt = prompt.replace("{{HISTORICAL_PRECEDENTS}}", precedents_context)
    prompt = prompt.replace("{{PITCH_TYPE}}", pitch_description)

    return {
        "prompt": prompt,
        "jd_file": jd_file,
        "resume_file": cv_file,
        "pitch_type": pitch_type,
        "profile": cand_profile,
    }

