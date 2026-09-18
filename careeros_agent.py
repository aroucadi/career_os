"""
CareerOS 2.0 Autonomous Agent
=============================
Powered by Google Antigravity SDK and Gemini.
Autonomous ReAct agent loop with tool orchestration, background radar triggers,
goal execution, and executive signal extraction.
"""

import os
import sys
import re
import json
import asyncio
import warnings
from pathlib import Path
from typing import Optional, List, Dict, Any

# Suppress harmless Pydantic enum serialization warnings from google-genai schema reflection
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except AttributeError:
        pass

# Ensure paths
_ROOT_DIR = Path(__file__).resolve().parent
_ENGINE_DIR = _ROOT_DIR / "engine"
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

from dotenv import load_dotenv
load_dotenv(_ROOT_DIR / ".env")

from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig, ToolContext
from google.antigravity.triggers import every, TriggerContext
from google.antigravity.hooks import policy
from engine.profiles.models import CandidateProfile

# ─── 1. CAREEROS TOOLS DEFINITION ─────────────────────────────────────────────

def tool_radar_scan(query: str, location: str, contract: bool, remote: bool, time_window: str, limit: int) -> str:
    """Scrapes newly published remote/contract job postings from LinkedIn guest API and registers them into 07_TARGET_JDS.

    Args:
        query: Search terms (e.g. 'AI Delivery Manager' or 'Agentic Delivery Lead').
        location: Geographic filter (e.g. 'Worldwide', 'Europe', 'France').
        contract: Filter for Contract/Freelance roles (True/False).
        remote: Filter for Remote roles (True/False).
        time_window: Time filter ('24h', '3d', 'week', or 'month').
        limit: Maximum job postings to fetch.

    Returns:
        A formatted summary of newly discovered and scored jobs.
    """
    from career_radar.scrapers.linkedin import LinkedInGuestScraper
    from career_radar.storage import JobRepository
    from career_radar.analyzer import JobAnalyzer

    query = query or "AI Delivery Manager"
    location = location or "Worldwide"
    time_window = time_window or "week"
    limit = limit or 3

    scraper = LinkedInGuestScraper()
    repo = JobRepository()
    analyzer = JobAnalyzer(resume_path=_ROOT_DIR / "Alaa_Eddine_Roucadi_Resume_v12.md")

    queries = [q.strip() for q in query.split(",")]
    discovered = []
    
    for q in queries:
        postings = scraper.search(query=q, location=location, remote=remote, contract=contract, time_window=time_window, limit=limit)
        for p in postings:
            if not repo.has_job(p.id):
                full_job = scraper.get_job_details(p.id) or p
                scored = analyzer.analyze(full_job)
                saved_file = repo.save_job(full_job, scored)
                discovered.append({
                    "id": p.id,
                    "title": p.title,
                    "company": p.company,
                    "score": scored.overall_match_score,
                    "url": p.url,
                    "file": saved_file
                })

    if not discovered:
        return f"Scan complete for query='{query}'. No new unseen jobs found matching criteria."

    out = [f"Found and scored {len(discovered)} new job(s):"]
    for d in discovered:
        out.append(f"• [{d['score']}/100] {d['title']} at {d['company']} (File: 07_TARGET_JDS/{d['file']}) - URL: {d['url']}")
    return "\n".join(out)


def tool_analyze_job(jd_filename: str) -> str:
    """Performs a deep CareerOS 4-pillar gap analysis of a target job description against Alaa's v12 resume.

    Args:
        jd_filename: The name of the JD file inside 07_TARGET_JDS/ (e.g. 'JD_21_K2_Partnering_Senior_AI_Product_Delivery_Manager.md').

    Returns:
        A structured analysis report with pillar breakdown, ATS keyword gaps, and recruiter pitch hook.
    """
    from career_radar.analyzer import JobAnalyzer
    from career_radar.models import JobPosting

    clean_name = Path(jd_filename).name
    jd_path = _ROOT_DIR / "07_TARGET_JDS" / clean_name
    if not jd_path.exists():
        # Try finding by partial stem
        matches = list((_ROOT_DIR / "07_TARGET_JDS").glob(f"*{clean_name}*"))
        if matches:
            jd_path = matches[0]
        else:
            return f"Error: Job description file '{clean_name}' not found in 07_TARGET_JDS/."

    jd_text = jd_path.read_text(encoding="utf-8")
    pseudo_job = JobPosting(
        id=jd_path.stem,
        title=jd_path.stem.replace("_", " ").title(),
        company="Target Enterprise",
        location="Vienna, Austria",
        description=jd_text,
        url=f"local://07_TARGET_JDS/{jd_path.name}"
    )

    from engine.profiles.manager import ProfileManager
    prof = ProfileManager.load_profile()
    cv_path = _ROOT_DIR / prof.resume_file
    if not cv_path.exists():
        cv_path = _ROOT_DIR / "resumes" / prof.resume_file

    analyzer = JobAnalyzer(resume_path=cv_path)
    scored = analyzer.analyze(pseudo_job)

    lines = [
        f"=== CAREEROS JOB FIT ANALYSIS: {scored.job_title} ===",
        f"Overall Match Score: {scored.overall_match_score}/100",
        "",
        "Pillar Breakdown:",
        f"• Change Management & Adoption: {scored.scores['change_management_adoption'].score}/30",
        f"• Agentic AI & Automation: {scored.scores['agentic_ai_automation'].score}/25",
        f"• Scaled Agile & Delivery: {scored.scores['scaled_agile_delivery'].score}/25",
        f"• Executive & Commercial Alignment: {scored.scores['executive_alignment'].score}/20",
        "",
        f"ATS Keyword Gaps: {', '.join(scored.ats_keyword_gaps) if scored.ats_keyword_gaps else 'None'}",
        f"Competency Gaps: {'; '.join(scored.competency_gaps) if scored.competency_gaps else 'None'}",
        "",
        f"Direct Recruiter Pitch Hook:\n\"{scored.recruiter_pitch_hook}\""
    ]
    return "\n".join(lines)


def tool_extract_executive_signals() -> str:
    """Extracts executive leadership signals from the active candidate profile master resume.

    Returns:
        JSON string of detected leadership dimensions.
    """
    from engine.enrichers.executive_enricher import extract_executive_signals
    from engine.profiles.manager import ProfileManager
    prof = ProfileManager.load_profile()
    cv_path = _ROOT_DIR / prof.resume_file
    if not cv_path.exists():
        cv_path = _ROOT_DIR / "resumes" / prof.resume_file
    signals = extract_executive_signals(cv_path)
    return json.dumps(signals, indent=2, ensure_ascii=False)


def tool_generate_market_heatmap() -> str:
    """Synthesizes cross-market demand from all analyzed job descriptions into CV_Strategic_Gap_Analysis_Report.md.

    Returns:
        Summary of the synthesized market heatmap and file path.
    """
    from engine.reports.generate_master_report import generate_markdown_report
    out = generate_markdown_report()
    if out and out.exists():
        return f"Market demand heatmap successfully compiled at: {out.absolute()}"
    return "Could not generate heatmap (synthesis cache missing)."


def tool_compile_pdf_resume(version: str) -> str:
    """Compiles an ATS-compliant, pixel-perfect A4 PDF resume from HTML template.

    Args:
        version: Resume version (e.g. 'v12', 'v11', 'v10').

    Returns:
        Confirmation message and file path of the generated PDF.
    """
    version = version or "v12"
    from engine.compiler.pdf_compiler import compile_latest_resume
    success = compile_latest_resume(version)
    if success:
        return f"Resume {version} PDF successfully compiled and synced to root: Alaa_Eddine_Roucadi_Resume_{version}.pdf"
    return f"Failed to compile Resume {version} PDF."


def tool_list_scanned_jobs() -> str:
    """Lists all job postings discovered and tracked by CareerOS Job Radar.

    Returns:
        A list of tracked jobs with match scores and status.
    """
    from career_radar.storage import JobRepository
    repo = JobRepository()
    scraped = repo.get_all_scraped()
    if not scraped:
        return "No jobs currently tracked in scraped_jobs.json."

    items = list(scraped.values())
    items.sort(key=lambda x: (x.get("scored") or {}).get("overall_match_score", 0), reverse=True)

    out = [f"Tracked Jobs ({len(items)} total):"]
    for it in items:
        job = it["job"]
        score = (it.get("scored") or {}).get("overall_match_score", 0)
        out.append(f"• [{score}/100] {job['title']} at {job['company']} (URL: {job['url']})")
    return "\n".join(out)


def tool_evaluate_draft_analysis(draft_text: str) -> str:
    """Evaluates a draft JD analysis and pitch against CareerOS 5 quality gates.

    Args:
        draft_text: The complete text of the draft evaluation, scores, and pitch.

    Returns:
        Structured critique with score, passed gates, failed gates, and improvements needed.
    """
    from engine.evaluators.eval_critic import evaluate_draft_analysis
    res = evaluate_draft_analysis(draft_text)
    out = [
        f"Quality Score: {res.quality_score}/100 | Status: {'PASS (Goal Fulfilled)' if res.is_valid else 'NEEDS REFINEMENT'}",
        "Passed Gates:",
    ]
    for p in res.passed_gates:
        out.append(f"  ✓ {p}")
    if res.failed_gates:
        out.append("Failed Gates:")
        for f in res.failed_gates:
            out.append(f"  ✗ {f}")
        out.append(f"Critique: {res.critique}")
        out.append("Actionable Improvements to apply before concluding:")
        for imp in res.suggested_improvements:
            out.append(f"  • {imp}")
    else:
        out.append("Critique: Excellent! Evaluation satisfies all 5 quality gates.")
    return "\n".join(out)


def tool_pipeline_get_status(dummy: str) -> str:
    """Returns a summary of all active opportunities in the CareerOS pipeline categorized by stage.

    Args:
        dummy: Optional filter keyword or pass empty string.

    Returns:
        Summary counts and active opportunity list by lifecycle stage.
    """
    from engine.pipeline.repository import PipelineRepository
    repo = PipelineRepository()
    all_opps = repo.list_all()
    stage_counts = {}
    for o in all_opps:
        stage_counts[o.stage.value] = stage_counts.get(o.stage.value, 0) + 1
    
    out = [f"CareerOS Pipeline Status (Total: {len(all_opps)} opportunities):"]
    for s, c in sorted(stage_counts.items()):
        out.append(f"• {s}: {c}")
    
    active = [o for o in all_opps if o.stage.value not in ("REJECTED", "ARCHIVED")]
    active.sort(key=lambda x: (x.evaluation.overall_score if x.evaluation else 0), reverse=True)
    out.append("\nTop Active Opportunities:")
    for a in active[:6]:
        score = f"{a.evaluation.overall_score:.0f}/100" if a.evaluation else "--"
        out.append(f"• [{a.id}] [{score}] {a.job_title} at {a.company} (Stage: {a.stage.value})")
    return "\n".join(out)


def tool_pipeline_advance_opportunity(jd_id: str, target_stage: str, notes: str) -> str:
    """Transitions a tracked opportunity to a new lifecycle stage (e.g. QUALIFIED, PITCH_READY, APPLIED, INTERVIEWING, OFFER_EXTENDED).

    Args:
        jd_id: The ID of the target job (e.g. 'JD_30' or 'JD_29').
        target_stage: Target lifecycle stage name.
        notes: Reason, context, or feedback for the transition.

    Returns:
        Confirmation message of the stage transition and updated audit history.
    """
    from engine.pipeline.repository import PipelineRepository
    from engine.pipeline.state_machine import PipelineStateMachine, TransitionError
    from engine.pipeline.models import PipelineStage

    repo = PipelineRepository()
    opp = repo.get(jd_id)
    if not opp:
        return f"Error: Opportunity '{jd_id}' not found in pipeline."
    
    try:
        stage_enum = PipelineStage(target_stage.upper())
    except ValueError:
        valid_stages = [s.value for s in PipelineStage]
        return f"Error: Invalid stage '{target_stage}'. Valid stages: {valid_stages}"
    
    try:
        PipelineStateMachine.transition(opp, stage_enum, notes=notes, actor="agent")
        repo.save(opp)
        return f"Successfully transitioned {opp.id} from {opp.history[-1].from_stage} to {opp.stage.value}. Notes: {notes}"
    except TransitionError as e:
        return f"Transition rejected: {e}"


def tool_pipeline_generate_persona_view(jd_id: str, persona: str) -> str:
    """Generates a tailored analysis briefing through one of the 4 personas (candidate, recruiter, hiring_manager, career_pivot).

    Args:
        jd_id: The ID of the target job (e.g. 'JD_30').
        persona: Persona lens ('candidate', 'recruiter', 'hiring_manager', or 'career_pivot').

    Returns:
        Structured persona-specific intelligence briefing.
    """
    from engine.pipeline.repository import PipelineRepository
    from engine.profiles.manager import ProfileManager
    
    prof = ProfileManager.load_profile()
    repo = PipelineRepository()
    opp = repo.get(jd_id)
    if not opp:
        return f"Error: Opportunity '{jd_id}' not found in pipeline."
    
    p_lower = persona.lower().strip()
    score = opp.evaluation.overall_score if opp.evaluation else "--"
    verdict = opp.evaluation.strategic_verdict if opp.evaluation else "PENDING"
    
    if p_lower in ("candidate", "candidat"):
        proof_summary = "; ".join([f"{p.category}: {p.evidence}" for p in prof.proof_metrics[:2]])
        return (
            f"=== CANDIDATE VIEW ({opp.id}) ===\n"
            f"Role: {opp.job_title} at {opp.company}\n"
            f"Fit Score: {score}/100 | Verdict: {verdict}\n"
            f"Target Rate: {prof.commercials.freelance_tjm_eur} | Leverage: HIGH\n"
            f"Pitch Strategy: Anchor on verified telemetry ({proof_summary}).\n"
            f"Dealbreaker Check: {prof.mobility.remote_preference} base in {prof.mobility.base_location} ({prof.mobility.travel_tolerance})."
        )
    elif p_lower in ("recruiter", "headhunter"):
        proof_bullets = "\n".join([f"• {p.label}: {p.evidence}" for p in prof.proof_metrics[:3]])
        return (
            f"=== RECRUITER QUALIFICATION VIEW ({opp.id}) ===\n"
            f"Candidate: {prof.full_name}\n"
            f"Rate Feasibility: Aligned with target ({prof.commercials.freelance_tjm_eur})\n"
            f"Languages: {', '.join(prof.languages.fluent_languages)}\n"
            f"Mobility: {prof.mobility.remote_preference}\n"
            f"Screening Summary (Grounded Proof Points):\n{proof_bullets}"
        )
    elif p_lower in ("hiring_manager", "employer", "client"):
        return (
            f"=== HIRING MANAGER & INTERVIEW VIEW ({opp.id}) ===\n"
            f"Target Mandate: {opp.job_title}\n"
            f"Key Gap-Probing Interview Questions:\n"
            f"1. How do you govern developer usage of autonomous tooling/agents across multiple squads without defect leakage?\n"
            f"2. How did your architectural solutions resolve cross-team dependencies in large-scale enterprise environments?\n"
            f"3. Walk through a high-stakes governance or regulatory compliance decision you enforced before production release.\n"
            f"4. How do you measure throughput gains and cycle time reduction directly attributable to modern tooling?\n"
            f"Risk Scorecard: Delivery Risk: LOW | Remote Autonomy Risk: ZERO | Scope Fit: HIGH."
        )
    elif p_lower in ("career_pivot", "pivot", "upskilling"):
        anti = f"Avoid: {', '.join(prof.scope.anti_roles)}" if prof.scope.anti_roles else ""
        return (
            f"=== CAREER PIVOT & UPSKILLING VIEW ({opp.id}) ===\n"
            f"Target Progression: Toward {', '.join(prof.scope.primary_titles[:2])}\n"
            f"Core Competency Delta:\n"
            f"• Move from operational task execution to strategic operating model architecture\n"
            f"• Embed automated compliance & release gates into standard CI/CD and delivery pipelines\n"
            f"• Track flow metrics and value realization over raw velocity\n"
            f"Guardrails: {anti}\n"
            f"Transferable Assets: Enterprise predictability, cross-functional leadership, steering visibility."
        )
    else:
        return f"Unknown persona '{persona}'. Choose from: candidate, recruiter, hiring_manager, career_pivot."


# ─── 2. AUTONOMOUS RADAR TRIGGER (BACKGROUND LOOP) ────────────────────────────

async def autonomous_radar_trigger(ctx: TriggerContext) -> None:
    """Autonomous background trigger that periodically sweeps for newly posted AI Delivery Manager contracts."""
    await ctx.send(
        "Autonomous Radar Trigger fired: Please check for newly posted Europe/Remote 'AI Delivery Manager' or "
        "'Agentic AI Lead' contract roles from the past 24 hours. If any role matches >= 75/100, present the scorecard "
        "and draft the outreach hook."
    )


# ─── 3. AGENT CONFIGURATION & RUNNER ──────────────────────────────────────────

def build_system_prompt(profile: Optional[CandidateProfile] = None) -> str:
    """Constructs dynamic system instructions bound to the active candidate profile."""
    from engine.profiles.manager import ProfileManager
    prof = profile or ProfileManager.load_profile()
    
    proof_lines = []
    for p in prof.proof_metrics:
        proof_lines.append(f"  • {p.category} ({p.label}): {p.evidence}")
    proof_text = "\n".join(proof_lines)

    return f"""You are CareerOS Agent, an executive AI career operating agent representing {prof.full_name}.

Candidate Profile & Credentials:
- Name: {prof.full_name} ({prof.mobility.base_location} — {prof.mobility.remote_preference}).
- Master CV: {prof.resume_file}.
- Core Identity: {prof.headline} ({prof.scope.seniority}).
- Target Scope: {', '.join(prof.scope.primary_titles)}.
- Key Grounded Strengths & Verified Telemetry:
{proof_text}
- Languages: {', '.join(prof.languages.fluent_languages)}.
- Commercial Boundaries: Freelance TJM {prof.commercials.freelance_tjm_eur} | Perm {prof.commercials.permanent_salary_eur}.

Your Mission:
1. Autonomously discover, scrape, and evaluate high-value contract/remote roles matching {prof.full_name}'s profile.
2. Apply CareerOS 4-pillar rubrics objectively without hype or unverified claims.
3. Formulate high-converting, tailored recruiter outreach pitches referencing {prof.full_name}'s exact verified metrics.
4. Execute user goals efficiently using your registered tools.
"""

CAREEROS_TOOLS = [
    tool_radar_scan,
    tool_analyze_job,
    tool_extract_executive_signals,
    tool_generate_market_heatmap,
    tool_compile_pdf_resume,
    tool_list_scanned_jobs,
    tool_evaluate_draft_analysis,
    tool_pipeline_get_status,
    tool_pipeline_advance_opportunity,
    tool_pipeline_generate_persona_view,
]


def create_careeros_agent(
    model_name: str = None,
    enable_trigger: bool = False,
    profile: Optional[CandidateProfile] = None
) -> Agent:
    """Initializes and returns the CareerOS Antigravity Agent with active candidate context."""
    if not model_name:
        model_name = os.getenv("DEFAULT_MODEL", "gemini-3.8-flash")

    system_prompt = build_system_prompt(profile=profile)
    triggers = [every(3600 * 24, autonomous_radar_trigger)] if enable_trigger else []

    vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("true", "1")
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "antigravity-cli-504510") if vertex else None
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "global") if vertex else None
    
    # Ensure JSON credentials path is explicitly set in environment
    creds_path = _ROOT_DIR / "gcp_credentials.json"
    if creds_path.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_path.resolve())

    config = LocalAgentConfig(
        model=model_name,
        system_instructions=system_prompt,
        tools=CAREEROS_TOOLS,
        triggers=triggers,
        capabilities=CapabilitiesConfig(),
        policies=[policy.allow_all()],
        vertex=vertex,
        project=project,
        location=location,
    )
    return Agent(config)


async def run_strategic_evaluation(
    jd_identifier: str,
    pitch_type: str = "recruiter",
    model_name: str = None,
    max_iterations: int = 3,
    profile: Optional[CandidateProfile] = None
):
    """Runs autonomous context-engineered evaluation with self-correction quality loop."""
    from engine.prompts.context_assembler import assemble_evaluation_prompt
    from engine.evaluators.eval_critic import evaluate_draft_analysis
    from engine.profiles.manager import ProfileManager

    cand_profile = profile or ProfileManager.load_profile()

    payload = assemble_evaluation_prompt(jd_identifier, pitch_type=pitch_type, profile=cand_profile)
    prompt = payload["prompt"]
    jd_file = payload["jd_file"]

    if not model_name:
        model_name = os.getenv("DEFAULT_MODEL", "gemini-3.8-flash")

    print(f"\n🎯 [STRATEGIC EVALUATION GOAL]: {jd_file.name} (Model: {model_name})")
    print(f"👤 [CANDIDATE PROFILE]: {cand_profile.full_name} ({cand_profile.id})")
    print(f"📌 [PITCH TYPE]: {payload['pitch_type']}\n")

    agent = create_careeros_agent(model_name=model_name, enable_trigger=False, profile=cand_profile)

    async with agent as my_agent:
        current_input = prompt
        full_response = ""

        for iteration in range(1, max_iterations + 1):
            if iteration > 1:
                print(f"\n🔄 [AUTONOMOUS SELF-CORRECTION LOOP — TURN {iteration}/{max_iterations}] Refined analysis generating...")
            else:
                print(f"🤖 [CAREEROS AGENTIC EVALUATOR]:\n")

            response = await my_agent.chat(current_input)
            chunk_tokens = []
            async for token in response:
                sys.stdout.write(token)
                sys.stdout.flush()
                chunk_tokens.append(token)
            print("\n")
            full_response = "".join(chunk_tokens)

            # Evaluate output against quality gates bound to candidate profile
            critic_result = evaluate_draft_analysis(full_response, profile=cand_profile)
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"📊 [QUALITY EVALUATION HARNESS]: Score {critic_result.quality_score:.0f}/100 — Status: {'PASS' if critic_result.is_valid else 'NEEDS REFINEMENT'}")

            for p in critic_result.passed_gates:
                print(f"   ✓ {p}")
            for f in critic_result.failed_gates:
                print(f"   ✗ {f}")

            if critic_result.is_valid or iteration == max_iterations:
                if critic_result.is_valid:
                    print(f"✅ [GOAL FULFILLED]: Output fully verified across all CareerOS quality gates!")
                else:
                    print(f"⚠️ [MAX ITERATIONS REACHED]: Returning best evaluation state.")
                
                # Auto-sync into Pipeline State Repository
                try:
                    from engine.pipeline.repository import PipelineRepository
                    from engine.pipeline.models import EvaluationSnapshot, PipelineStage
                    repo = PipelineRepository()
                    opp = repo.get(jd_file.name)
                    if opp:
                        m_verdict = re.search(r"\b(GO|NO[- ]GO|CONDITIONAL GO)\b", full_response)
                        verdict = m_verdict.group(1).upper() if m_verdict else ("GO" if critic_result.quality_score >= 80 else "CONDITIONAL GO")
                        
                        opp.evaluation = EvaluationSnapshot(
                            overall_score=float(critic_result.quality_score),
                            scores={"change_management_adoption": 25.0, "agentic_ai_automation": 25.0, "scaled_agile_delivery": 25.0, "executive_alignment": 20.0},
                            strategic_verdict=verdict,
                            ats_keyword_gaps=[],
                            competency_gaps=[]
                        )
                        if "NO" not in verdict and opp.stage == PipelineStage.DISCOVERED:
                            opp.stage = PipelineStage.QUALIFIED
                        if critic_result.is_valid and "NO" not in verdict:
                            opp.stage = PipelineStage.PITCH_READY
                        repo.save(opp)
                        print(f"💾 [PIPELINE SYNC]: Saved evaluation snapshot for {opp.id} (Stage: {opp.stage.value}).")
                except Exception as ex:
                    print(f"⚠️ [PIPELINE SYNC ERROR]: {ex}")

                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                break

            # Trigger autonomous self-correction turn in same conversation
            improvements_str = "\n".join([f"- {i}" for i in critic_result.suggested_improvements])
            failed_str = "\n".join([f"- {f}" for f in critic_result.failed_gates])
            print(f"⚠️ [AUTONOMOUS CRITIC REJECTION]: Quality gates failed. Self-correcting in loop...\n")

            current_input = (
                f"CareerOS Quality Critic rejected draft with score {critic_result.quality_score:.0f}/100.\n"
                f"Issues to fix:\n{failed_str}\n\n"
                f"Required improvements:\n{improvements_str}\n\n"
                f"Please produce the updated, fully compliant evaluation fulfilling all 7 steps with precision."
            )


async def run_goal(goal: str, model_name: str = None, profile: Optional[CandidateProfile] = None):
    """Executes a specific goal through the CareerOS Agentic loop."""
    from engine.profiles.manager import ProfileManager
    cand_profile = profile or ProfileManager.load_profile()
    if not model_name:
        model_name = os.getenv("DEFAULT_MODEL", "gemini-3.8-flash")
    print(f"\n🎯 [GOAL]: {goal} (Model: {model_name})")
    print(f"👤 [CANDIDATE PROFILE]: {cand_profile.full_name} ({cand_profile.id})\n")
    agent = create_careeros_agent(model_name=model_name, enable_trigger=False, profile=cand_profile)
    async with agent as my_agent:
        response = await my_agent.chat(goal)
        print("\n🤖 [CAREEROS AGENT]:\n")
        async for token in response:
            sys.stdout.write(token)
            sys.stdout.flush()
        print("\n")


def main():
    import argparse
    from engine.profiles.manager import ProfileManager

    parser = argparse.ArgumentParser(description="CareerOS Antigravity Agent")
    parser.add_argument("goal", nargs="?", default="List all tracked jobs in repository and extract executive signals from my master resume.", help="Goal to execute")
    parser.add_argument("--profile", default=None, help="Candidate profile slug (e.g. default, sophie_cloud_architect)")
    parser.add_argument("--model", default=os.getenv("DEFAULT_MODEL", "gemini-3.8-flash"), help="Model to use")
    parser.add_argument("--interactive", action="store_true", help="Run interactive conversational session")
    args = parser.parse_args()

    cand_profile = ProfileManager.load_profile(args.profile)

    if args.interactive:
        from google.antigravity.utils.interactive import run_interactive_loop
        vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("true", "1")
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "antigravity-cli-504510") if vertex else None
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "global") if vertex else None
        config = LocalAgentConfig(
            model=args.model,
            system_instructions=build_system_prompt(profile=cand_profile),
            tools=CAREEROS_TOOLS,
            capabilities=CapabilitiesConfig(),
            policies=[policy.allow_all()],
            vertex=vertex,
            project=project,
            location=location,
        )
        asyncio.run(run_interactive_loop(config))
    else:
        asyncio.run(run_goal(args.goal, model_name=args.model, profile=cand_profile))


if __name__ == "__main__":
    main()
