"""
CareerOS Master CLI — Autonomous Discovery, Intelligent Evaluation & PDF Pipeline
==================================================================================
Unified command-line interface for the entire CareerOS ecosystem.
"""

import os
import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except AttributeError:
        pass

# Add engine to path
_ROOT_DIR = Path(__file__).resolve().parent
_ENGINE_DIR = _ROOT_DIR / "engine"
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

from dotenv import load_dotenv
load_dotenv(_ROOT_DIR / ".env", override=True)

console = Console()

def cmd_radar_scan(args):
    """Executes live job search across job boards via career_radar."""
    from career_radar_cli import cmd_scan
    cmd_scan(args)

def cmd_radar_fetch(args):
    """Fetches and scores a single job URL via career_radar."""
    from career_radar_cli import cmd_fetch
    cmd_fetch(args)

def cmd_radar_report(args):
    """Displays summary report of tracked jobs."""
    from career_radar_cli import cmd_report
    cmd_report(args)

def cmd_gap_report(args):
    """Runs batch multi-JD gap analysis using CareerOS rubrics and produces cv_gap_report.html."""
    from engine.profiles.manager import ProfileManager
    cand_prof = ProfileManager.load_profile(getattr(args, "profile", None))
    baseline_cv = args.cv or cand_prof.resume_file
    console.print(Panel("[bold cyan]Running CareerOS Batch Gap Analysis[/]\n"
                        f"• Target JDs Directory: [magenta]07_TARGET_JDS[/]\n"
                        f"• Candidate Baseline:   [green]{baseline_cv}[/]\n"
                        f"• Profile:              [yellow]{cand_prof.full_name} ({cand_prof.id})[/]\n"
                        f"• Use Cache:           {args.cache}",
                        title="CareerOS Gap Engine", border_style="cyan"))
    
    from engine.evaluators.cv_gap_analysis import main as run_gap_analysis
    orig_argv = sys.argv
    sys.argv = ["cv_gap_analysis.py"]
    if baseline_cv:
        sys.argv.extend(["--cv", baseline_cv])
    if args.cache:
        sys.argv.append("--cache")
    if args.model:
        sys.argv.extend(["--model", args.model])
    
    try:
        run_gap_analysis()
    finally:
        sys.argv = orig_argv

def cmd_heatmap(args):
    """Generates cross-market ATS skill frequency matrix and markdown report."""
    console.print(Panel("[bold cyan]Synthesizing Cross-Market Demand Heatmap[/]", title="CareerOS Market Intel", border_style="magenta"))
    from engine.reports.generate_master_report import generate_markdown_report
    out = generate_markdown_report(args.out)
    if out and out.exists():
        console.print(f"[bold green]✓ Market Heatmap generated at:[/] {out.absolute()}")

def cmd_export_pdf(args):
    """Compiles resume HTML template to PDF using headless Edge/Chrome."""
    version = args.version or "v12"
    console.print(Panel(f"[bold cyan]Compiling Resume {version} to PDF via Headless Browser[/]", title="CareerOS PDF Compiler", border_style="blue"))
    from engine.compiler.pdf_compiler import compile_latest_resume
    success = compile_latest_resume(version)
    if success:
        console.print(f"[bold green]✓ Resume {version} PDF compilation complete![/]")
    else:
        console.print(f"[bold red]✗ Failed to compile Resume {version} PDF.[/]")

def cmd_enrich(args):
    """Extracts executive signals from the candidate CV."""
    from engine.profiles.manager import ProfileManager
    cand_prof = ProfileManager.load_profile(getattr(args, "profile", None))
    if args.cv:
        cv_path = Path(args.cv)
    else:
        cv_path = _ROOT_DIR / cand_prof.resume_file
        if not cv_path.exists():
            cand_alt = _ROOT_DIR / "resumes" / cand_prof.resume_file
            if cand_alt.exists():
                cv_path = cand_alt
    
    if not cv_path.exists():
        console.print(f"[red]CV not found: {cv_path}[/]")
        return
    
    console.print(Panel(f"[bold cyan]Extracting Executive & Leadership Signals for:[/] {cand_prof.full_name} ({cv_path.name})", title="Executive Enricher", border_style="green"))
    from engine.enrichers.executive_enricher import extract_executive_signals
    signals = extract_executive_signals(cv_path)
    
    table = Table(title="Executive Signals Breakdown", border_style="cyan")
    table.add_column("Signal Dimension", style="bold white", width=28)
    table.add_column("Detected Signals & Metrics", style="green")
    
    for category, items in signals.items():
        cat_clean = category.replace("_", " ").title()
        val_str = ", ".join(items) if items else "[dim]None detected[/dim]"
        table.add_row(cat_clean, val_str)
        
    console.print(table)


def cmd_agent(args):
    """Executes the autonomous CareerOS Antigravity agent."""
    import asyncio
    from careeros_agent import (
        run_goal,
        build_system_prompt,
        CAREEROS_TOOLS,
    )
    from engine.profiles.manager import ProfileManager
    from google.antigravity import LocalAgentConfig, CapabilitiesConfig
    from google.antigravity.hooks import policy

    cand_profile = ProfileManager.load_profile(getattr(args, "profile", None))

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
        goal = args.goal or "List all tracked jobs and extract executive signals from active master resume."
        asyncio.run(run_goal(goal, model_name=args.model, profile=cand_profile))


def cmd_evaluate(args):
    """Runs context-engineered evaluation with autonomous quality gate loop or dual-agent debate."""
    import asyncio
    from engine.profiles.manager import ProfileManager

    cand_profile = ProfileManager.load_profile(args.profile)

    if getattr(args, "debate", False):
        from engine.evaluators.debate.runner import DebateRunner
        from engine.prompts.context_assembler import resolve_jd_file
        from rich.columns import Columns

        jd_path = resolve_jd_file(args.jd)
        jd_text = jd_path.read_text(encoding="utf-8")
        jd_title = jd_path.stem.replace("_", " ")

        runner = DebateRunner(profile=cand_profile, model_name=args.model)

        console.print(Panel(
            f"[bold cyan]Dual-Agent Dialectic Debate:[/] {jd_title}\n"
            f"👤 [bold white]Candidate:[/] {cand_profile.full_name} ({cand_profile.id})\n"
            f"⚖️ [bold gold1]Model:[/] {runner.model_name} | Mode: {'Fast Heuristic' if getattr(args, 'fast', False) else 'Dialectic Runner'}",
            title="Debate Engine Harness",
            border_style="cyan"
        ))

        if getattr(args, "llm", False):
            transcript = asyncio.run(runner.run_llm_debate(jd_id=jd_path.name, jd_title=jd_title, jd_text=jd_text))
        else:
            transcript = runner.run_fast_heuristic_debate(jd_id=jd_path.name, jd_title=jd_title, jd_text=jd_text)

        # 1. Render Prosecutor Panel (Red/Orange)
        db_lines = []
        for d in transcript.indictment.dealbreakers:
            db_lines.append(f"[bold red]• [{d.severity}][/bold red] {d.description}")
        if not db_lines:
            db_lines = ["[dim green]• No fatal boundary dealbreakers detected.[/dim green]"]

        rf_lines = [f"[yellow]• {rf}[/yellow]" for rf in transcript.indictment.unspoken_red_flags]
        if not rf_lines:
            rf_lines = ["[dim]• No unspoken red flags flagged.[/dim]"]

        prosecutor_content = (
            f"[bold red]Verdict:[/] {transcript.indictment.prosecutor_verdict}\n"
            f"[bold red]Trap Score:[/] {transcript.indictment.trap_score:.0f}/100\n\n"
            f"[bold underline]Detected Dealbreakers:[/]\n" + "\n".join(db_lines) + "\n\n"
            f"[bold underline]Unspoken Red Flags:[/]\n" + "\n".join(rf_lines) + "\n\n"
            f"[dim]{transcript.indictment.summary_indictment}[/dim]"
        )
        prosecutor_panel = Panel(prosecutor_content, title="🚨 Skeptical Prosecutor (Deal Killer)", border_style="red", width=58)

        # 2. Render Advocate Panel (Green/Cyan)
        reb_lines = [f"[cyan]• {r}[/cyan]" for r in transcript.defense.rebuttal_points]
        proof_lines = [f"[green]• {p}[/green]" for p in transcript.defense.grounded_proof_citations]

        advocate_content = (
            f"[bold green]Stance:[/] {transcript.defense.advocate_verdict}\n"
            f"[bold green]Positioning:[/] {transcript.defense.target_positioning}\n\n"
            f"[bold underline]Rebuttal & Leverage Points:[/]\n" + "\n".join(reb_lines) + "\n\n"
            f"[bold underline]Grounded Proof Metrics Cited:[/]\n" + "\n".join(proof_lines) + "\n\n"
            f"[bold underline]Negotiation Hook:[/]\n[italic]{transcript.defense.negotiation_hook}[/italic]"
        )
        advocate_panel = Panel(advocate_content, title="🛡️ Opportunity Advocate (Strategist)", border_style="green", width=58)

        # Print Dual Columns
        console.print(Columns([prosecutor_panel, advocate_panel]))

        # 3. Render Arbiter Decision Panel (Gold/White)
        crit_color = "green" if transcript.arbitration.critic_quality_score >= 80 else "yellow"
        cond_lines = "\n".join([f"• {c}" for c in transcript.arbitration.binding_conditions])
        arbiter_content = (
            f"[bold white]Final Strategic Verdict:[/] [bold {crit_color}]{transcript.arbitration.final_verdict}[/bold {crit_color}]  |  "
            f"[bold white]Overall Fit Score:[/] {transcript.arbitration.fit_score:.1f}/100  |  "
            f"[bold white]Quality Gate Score:[/] [{crit_color}]{transcript.arbitration.critic_quality_score:.0f}/100[/]\n\n"
            f"[bold underline]Decision Rationale:[/]\n{transcript.arbitration.decision_rationale}\n\n"
            f"[bold underline]Candidate Binding Conditions:[/]\n{cond_lines}"
        )
        console.print(Panel(arbiter_content, title="⚖️ The Arbiter (Quality Gate Harness)", border_style="gold1"))

    else:
        from careeros_agent import run_strategic_evaluation
        asyncio.run(
            run_strategic_evaluation(
                jd_identifier=args.jd,
                pitch_type=args.pitch,
                model_name=args.model,
                max_iterations=args.max_iterations,
                profile=cand_profile,
            )
        )


def cmd_pipeline(args):
    """Handles pipeline lifecycle state machine operations and multi-persona views."""
    from engine.pipeline.repository import PipelineRepository
    from engine.pipeline.state_machine import PipelineStateMachine, TransitionError
    from engine.pipeline.models import PipelineStage, PersonaType
    from engine.pipeline.views import render_pipeline_table, render_persona_view
    
    repo = PipelineRepository()
    
    if args.pipeline_cmd == "status":
        opportunities = repo.list_all(stage_filter=args.stage)
        table = render_pipeline_table(opportunities)
        console.print(table)
        console.print(f"[dim]Total Opportunities Tracked: {len(opportunities)}[/dim]")
        
    elif args.pipeline_cmd == "view":
        opp = repo.get(args.jd_id)
        if not opp:
            console.print(f"[bold red]Error: Opportunity '{args.jd_id}' not found in pipeline.[/bold red]")
            return
        
        from engine.profiles.manager import ProfileManager
        cand_prof = ProfileManager.load_profile(getattr(args, "profile", None))

        persona_map = {
            "candidate": PersonaType.CANDIDATE,
            "recruiter": PersonaType.RECRUITER,
            "hiring_manager": PersonaType.HIRING_MANAGER,
            "pivot": PersonaType.CAREER_PIVOT,
            "career_pivot": PersonaType.CAREER_PIVOT,
        }
        target_persona = persona_map.get(args.persona.lower(), PersonaType.CANDIDATE)
        render_persona_view(opp, target_persona, console, profile=cand_prof)
        
    elif args.pipeline_cmd == "advance":
        opp = repo.get(args.jd_id)
        if not opp:
            console.print(f"[bold red]Error: Opportunity '{args.jd_id}' not found in pipeline.[/bold red]")
            return
        
        try:
            target_stage = PipelineStage(args.stage.upper())
        except ValueError:
            valid_stages = ", ".join([s.value for s in PipelineStage])
            console.print(f"[bold red]Error: Invalid stage '{args.stage}'. Valid stages: {valid_stages}[/bold red]")
            return
        
        try:
            PipelineStateMachine.transition(opp, target_stage, notes=args.notes or "", actor="user")
            repo.save(opp)
            console.print(f"[bold green]Successfully transitioned {opp.id} to {target_stage.value}.[/bold green]")
        except TransitionError as e:
            console.print(f"[bold red]Transition failed: {e}[/bold red]")
            
    elif args.pipeline_cmd == "feedback":
        opp = repo.get(args.jd_id)
        if not opp:
            console.print(f"[bold red]Error: Opportunity '{args.jd_id}' not found in pipeline.[/bold red]")
            return

        from engine.memory.store import EpisodicMemoryStore
        from engine.memory.models import FeedbackOutcome, ObjectionCategory
        mem_store = EpisodicMemoryStore()

        try:
            outcome_enum = FeedbackOutcome(args.outcome.upper())
        except ValueError:
            valid_outcomes = ", ".join([o.value for o in FeedbackOutcome])
            console.print(f"[bold red]Error: Invalid outcome '{args.outcome}'. Valid outcomes: {valid_outcomes}[/bold red]")
            return

        obj_enum = None
        if args.objection:
            try:
                obj_enum = ObjectionCategory(args.objection.lower())
            except ValueError:
                valid_objs = ", ".join([o.value for o in ObjectionCategory])
                console.print(f"[bold yellow]Warning: Invalid objection '{args.objection}'. Valid: {valid_objs}[/bold yellow]")

        takeaways = [t.strip() for t in args.notes.split(";") if t.strip()] if args.notes else []
        rec = mem_store.record_feedback(
            opportunity_id=opp.id,
            company=opp.company,
            role_title=opp.job_title,
            outcome=outcome_enum,
            objection_category=obj_enum,
            actual_rate_offered_eur=args.rate,
            notes=args.notes or "",
            key_takeaways=takeaways
        )

        # Transition stage accordingly if relevant
        if outcome_enum in (FeedbackOutcome.RATE_REJECTED, FeedbackOutcome.LOCATION_REJECTED, FeedbackOutcome.SCOPE_MISMATCH):
            try:
                PipelineStateMachine.transition(opp, PipelineStage.REJECTED, notes=f"Episodic memory logged: {args.notes}", actor="user")
                repo.save(opp)
            except Exception:
                pass
        elif outcome_enum == FeedbackOutcome.INTERVIEW_SCHEDULED:
            try:
                PipelineStateMachine.transition(opp, PipelineStage.SCREENING_SCHEDULED, notes=f"Screening scheduled: {args.notes}", actor="user")
                repo.save(opp)
            except Exception:
                pass

        console.print(Panel(
            f"[bold green]Feedback Successfully Ingested into Episodic Memory![/]\n"
            f"• Record ID:   [cyan]{rec.id}[/]\n"
            f"• Target:      [white]{opp.job_title} at {opp.company}[/]\n"
            f"• Outcome:     [bold yellow]{outcome_enum.value}[/]\n"
            f"• Rate Noted:  {f'{args.rate:.0f} EUR/day' if args.rate else 'Not specified'}\n"
            f"• Learning:    [italic]{args.notes}[/italic]",
            title="Closed-Loop Feedback Loop",
            border_style="green"
        ))

    elif args.pipeline_cmd == "sync":
        count = repo.sync_from_repository()
        console.print(f"[bold green]Pipeline successfully synced. {count} opportunities indexed.[/bold green]")
    else:
        console.print("[yellow]Please specify a pipeline subcommand: status, view, advance, feedback, sync[/yellow]")


def cmd_memory(args):
    """Displays historical market learnings and company track records from Episodic Memory."""
    from engine.memory.store import EpisodicMemoryStore
    mem_store = EpisodicMemoryStore()

    if args.company:
        track = mem_store.get_company_track_record(args.company)
        console.print(Panel(
            f"[bold cyan]Company Track Record:[/] {track.company_name}\n"
            f"• Total Interactions: [white]{track.total_interactions}[/]\n"
            f"• Avg Rate Disclosed: [white]{f'{track.average_rate_eur:.0f} EUR/day' if track.average_rate_eur else 'N/A'}[/]",
            title="Episodic Memory", border_style="cyan"
        ))
        if track.known_objections:
            console.print("[bold red]Known Objections:[/]")
            for o in track.known_objections:
                console.print(f"  • {o}")
        if track.strategic_rules:
            console.print("[bold green]Strategic Rules & Learnings:[/]")
            for r in track.strategic_rules:
                console.print(f"  ✓ {r}")
        return

    records = mem_store.list_all()
    if not records:
        console.print("[yellow]No episodic records logged yet. Use 'careeros_cli.py pipeline feedback <JD_ID> ...' to log real feedback.[/yellow]")
        return

    table = Table(title=f"CareerOS Episodic Learning Memory ({len(records)} Records)", border_style="cyan")
    table.add_column("Record ID", style="bold cyan", width=14)
    table.add_column("Opportunity / Company", style="white")
    table.add_column("Outcome", style="bold yellow", width=18)
    table.add_column("Rate", style="green", width=12)
    table.add_column("Key Learning / Takeaway", style="italic")

    for r in records:
        rate_s = f"{r.actual_rate_offered_eur:.0f} €/j" if r.actual_rate_offered_eur else "-"
        takeaway_s = "; ".join(r.key_takeaways) if r.key_takeaways else r.notes
        table.add_row(r.id, f"{r.opportunity_id}: {r.company}", r.outcome.value, rate_s, takeaway_s)

    console.print(table)


def cmd_tailor(args):
    """Synthesizes a tailored markdown resume and compiles it to pixel-perfect A4 PDF."""
    from engine.compiler.tailor import ResumeTailor
    from engine.profiles.manager import ProfileManager
    from engine.prompts.context_assembler import resolve_jd_file
    from engine.pipeline.repository import PipelineRepository
    from engine.pipeline.state_machine import PipelineStateMachine
    from engine.pipeline.models import PipelineStage

    cand_profile = ProfileManager.load_profile(args.profile)
    jd_path = resolve_jd_file(args.jd)
    jd_text = jd_path.read_text(encoding="utf-8")
    jd_title = jd_path.stem.replace("_", " ")

    console.print(Panel(
        f"[bold cyan]Automated CV Tailoring & Headless PDF Compiler[/]\n"
        f"👤 [bold white]Candidate:[/] {cand_profile.full_name} ({cand_profile.id})\n"
        f"🎯 [bold green]Target Job:[/] {jd_title} ({jd_path.name})\n"
        f"📄 [bold yellow]Master CV:[/] {cand_profile.resume_file}",
        title="Resume Tailor Engine", border_style="cyan"
    ))

    tailor = ResumeTailor(profile=cand_profile)
    mode = "llm" if getattr(args, "llm", False) else "fast"
    result = tailor.tailor_and_compile(
        jd_id=jd_path.stem,
        jd_title=jd_title,
        jd_text=jd_text,
        mode=mode,
        model_name=args.model
    )

    if result["success"]:
        console.print(f"[bold green]✓ Pixel-Perfect A4 PDF successfully compiled![/bold green]")
    else:
        console.print(f"[bold yellow]⚠️ Markdown and HTML generated, but PDF compiler encountered a warning.[/bold yellow]")

    # Print summary panel
    console.print(Panel(
        f"[bold white]Tailored Headline:[/] [cyan]{result['tailored_headline']}[/cyan]\n\n"
        f"[bold white]Executive Summary Hook:[/] [italic]{result['tailored_summary']}[/italic]\n\n"
        f"[bold white]Artifacts Generated:[/]\n"
        f"• Markdown: [white]{result['md_path']}[/white]\n"
        f"• HTML:     [white]{result['html_path']}[/white]\n"
        f"• PDF:      [bold green]{result['pdf_path']}[/bold green]",
        title="Tailored Resume Artifacts", border_style="green"
    ))

    # Auto-sync pipeline CRM to PITCH_READY
    repo = PipelineRepository()
    opp = repo.get(jd_path.name)
    if opp:
        try:
            if opp.stage in (PipelineStage.DISCOVERED, PipelineStage.QUALIFIED):
                PipelineStateMachine.transition(
                    opp,
                    PipelineStage.PITCH_READY,
                    notes=f"Auto-generated tailored PDF: {result['pdf_path'].name}",
                    actor="careeros_tailor"
                )
                repo.save(opp)
                console.print(f"[dim green]Pipeline Opportunity {opp.id} advanced to PITCH_READY.[/dim green]")
        except Exception as e:
            console.print(f"[dim yellow]Pipeline note: {e}[/dim yellow]")


def cmd_benchmark(args):
    """Executes the offline evaluation benchmark suite against the golden dataset."""
    from engine.evaluators.benchmark import BenchmarkRunner
    runner = BenchmarkRunner(console=console)
    mode = "llm" if getattr(args, "llm", False) else "fast"
    summary = runner.run(
        mode=mode,
        profile_filter=args.profile,
        case_filter=args.case,
        model_name=args.model,
        use_debate=getattr(args, "debate", False)
    )
    if summary.suite_status != "PASS":
        sys.exit(1)


def cmd_server(args):
    """Starts the CareerOS FastAPI backend server (Uvicorn)."""
    import uvicorn
    console.print(Panel(
        f"[bold green]Starting CareerOS Autonomous API Server[/]\n"
        f"• Host:       [cyan]{args.host}[/]\n"
        f"• Port:       [yellow]{args.port}[/]\n"
        f"• Reload:     [magenta]{args.reload}[/]\n"
        f"• Swagger UI: [link=http://{args.host}:{args.port}/docs]http://{args.host}:{args.port}/docs[/]\n"
        f"• Streaming:  [bold white]Vercel AI SDK SSE protocol (/api/chat)[/]",
        title="CareerOS Server", border_style="green"
    ))
    uvicorn.run("api.main:app", host=args.host, port=args.port, reload=args.reload)


def cmd_logs(args):
    """Displays recent CareerOS interaction audit logs and server traces."""
    from api.logger import AuditLogger
    records = AuditLogger.get_recent_logs(limit=args.limit)
    if not records:
        console.print("[yellow]No interaction audit logs found yet in logs/chat_audit.jsonl.[/]")
        return

    table = Table(title=f"CareerOS Interaction Audit Logs (Last {len(records)})", border_style="cyan")
    table.add_column("Timestamp", style="dim", no_wrap=True)
    table.add_column("Req ID", style="bold cyan")
    table.add_column("Route", style="magenta")
    table.add_column("Model", style="blue")
    table.add_column("Duration", style="yellow")
    table.add_column("Tools Emitted", style="green")
    table.add_column("Status", style="bold")
    table.add_column("Prompt Snippet", style="white")

    for r in records:
        ts = r.get("timestamp", "")[:19].replace("T", " ")
        status_style = "[bold green]OK[/]" if r.get("status") == "SUCCESS" else "[bold red]ERR[/]"
        dur = f"{r.get('duration_ms', 0):.0f}ms" if r.get("duration_ms") else "-"
        tools = ", ".join(r.get("tool_calls", [])) or "-"
        msg = r.get("user_message", "")
        snippet = (msg[:38] + "...") if len(msg) > 38 else msg
        table.add_row(
            ts,
            r.get("request_id", "-"),
            r.get("route_taken", "-"),
            r.get("llm_model") or "-",
            dur,
            tools,
            status_style,
            snippet
        )
    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="CareerOS 2.0 Master CLI — Autonomous Job Discovery & Intelligence")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Radar subcommands
    p_scan = subparsers.add_parser("scan", help="Search and scrape newly published job offers (via Career Radar)")
    p_scan.add_argument("-q", "--query", default="AI Delivery Manager,Agentic Delivery Manager", help="Comma-separated query terms")
    p_scan.add_argument("-l", "--location", default="Worldwide", help="Location (e.g. Worldwide, France, Europe)")
    p_scan.add_argument("--contract", action="store_true", default=True, help="Filter for Contract / Freelance (default: True)")
    p_scan.add_argument("--no-contract", dest="contract", action="store_false", help="Do not filter for contract only")
    p_scan.add_argument("--remote", action="store_true", default=True, help="Filter for Remote (default: True)")
    p_scan.add_argument("--no-remote", dest="remote", action="store_false", help="Do not filter for remote only")
    p_scan.add_argument("-t", "--time", default="week", choices=["24h", "3d", "week", "month"], help="Time posted filter")
    p_scan.add_argument("-n", "--limit", type=int, default=4, help="Max results per query")
    p_scan.add_argument("--min-score", type=int, default=50, help="Minimum score to persist to 07_TARGET_JDS")

    p_fetch = subparsers.add_parser("fetch", help="Fetch and analyze a single job description URL")
    p_fetch.add_argument("-u", "--url", required=True, help="Direct URL to job description")

    p_report = subparsers.add_parser("report", help="Display summary report of all tracked radar jobs")

    # Deep Gap & Heatmap subcommands
    p_gap = subparsers.add_parser("gap-report", help="Run batch multi-JD gap analysis and build cv_gap_report.html")
    p_gap.add_argument("--cv", default=None, help="Path to resume file (default: from active candidate profile)")
    p_gap.add_argument("--profile", default=None, help="Candidate profile slug (e.g. default, sophie_cloud_architect)")
    p_gap.add_argument("--cache", action="store_true", default=True, help="Use cached JD evaluations (default: True)")
    p_gap.add_argument("--no-cache", dest="cache", action="store_false", help="Force fresh evaluations")
    p_gap.add_argument("--model", default="gemini-3.7-flash", help="LLM model to use")

    p_heat = subparsers.add_parser("heatmap", help="Generate market-wide ATS skill frequency matrix and report")
    p_heat.add_argument("--out", default=None, help="Output markdown report path")

    # PDF compilation subcommand
    p_pdf = subparsers.add_parser("export-pdf", help="Compile resume HTML template to pixel-perfect PDF")
    p_pdf.add_argument("-v", "--version", default="v12", choices=["v7", "v8", "v9", "v10", "v11", "v12"], help="Resume version")

    # Executive enrichment subcommand
    p_enr = subparsers.add_parser("enrich", help="Extract leadership & executive signals from a resume")
    p_enr.add_argument("--cv", default=None, help="Path to resume file (default: from active candidate profile)")
    p_enr.add_argument("--profile", default=None, help="Candidate profile slug (e.g. default, sophie_cloud_architect)")

    # Autonomous Antigravity Agent subcommand
    p_agent = subparsers.add_parser("agent", help="Run autonomous CareerOS Agent (powered by Antigravity SDK)")
    p_agent.add_argument("goal", nargs="?", default=None, help="Goal or prompt for the autonomous agent")
    p_agent.add_argument("--profile", default=None, help="Candidate profile slug (e.g. default, sophie_cloud_architect)")
    p_agent.add_argument("--interactive", "-i", action="store_true", help="Launch interactive chat session with the agent")
    p_agent.add_argument("--model", "-m", default=os.getenv("DEFAULT_MODEL", "gemini-3.8-flash"), help="Gemini model to use")

    # Canonical Strategic Evaluation subcommand (Context-Engineered Pipeline with Quality Loop)
    p_eval = subparsers.add_parser("evaluate", help="Run context-engineered 7-step evaluation with autonomous quality harness")
    p_eval.add_argument("jd", help="Target JD filename, number (e.g. JD_30 or 30), or stem")
    p_eval.add_argument("--profile", default=None, help="Candidate profile slug (e.g. alaa_roucadi, sophie_cloud_architect)")
    p_eval.add_argument("--pitch", "-p", default="recruiter", choices=["recruiter", "direct", "linkedin"], help="Target pitch type")
    p_eval.add_argument("--model", "-m", default=os.getenv("DEFAULT_MODEL", "gemini-3.8-flash"), help="Gemini model to use")
    p_eval.add_argument("--max-iterations", type=int, default=3, help="Max self-correction iterations in loop")
    p_eval.add_argument("--debate", action="store_true", help="Run dual-agent dialectic debate (Prosecutor vs Advocate)")
    p_eval.add_argument("--fast", action="store_true", default=True, help="Fast heuristic debate simulation (default: True)")
    p_eval.add_argument("--llm", action="store_true", help="Full multi-turn LLM dialectic debate")

    # Opportunity Lifecycle Pipeline subcommand (Chantier 1)
    p_pipe = subparsers.add_parser("pipeline", help="Manage opportunity lifecycle state machine and multi-persona intelligence")
    pipe_subs = p_pipe.add_subparsers(dest="pipeline_cmd", help="Pipeline operations")
    
    p_pipe_status = pipe_subs.add_parser("status", help="Display Rich table of active opportunities across pipeline stages")
    p_pipe_status.add_argument("--stage", "-s", default=None, help="Filter by stage (e.g. DISCOVERED, QUALIFIED, PITCH_READY)")
    
    p_pipe_view = pipe_subs.add_parser("view", help="Render persona-specific briefing panel for a job opportunity")
    p_pipe_view.add_argument("jd_id", help="Opportunity ID (e.g. JD_30 or JD_29)")
    p_pipe_view.add_argument("--persona", "-p", default="candidate", choices=["candidate", "recruiter", "hiring_manager", "pivot"], help="Persona lens")
    p_pipe_view.add_argument("--profile", default=None, help="Candidate profile slug (e.g. alaa_roucadi, sophie_cloud_architect)")
    
    p_pipe_adv = pipe_subs.add_parser("advance", help="Advance opportunity to a new lifecycle stage via the state machine")
    p_pipe_adv.add_argument("jd_id", help="Opportunity ID (e.g. JD_30)")
    p_pipe_adv.add_argument("stage", help="Target stage (e.g. QUALIFIED, PITCH_READY, APPLIED, INTERVIEWING)")
    p_pipe_adv.add_argument("--notes", "-n", default="", help="Audit notes or rationale for stage transition")
    
    # Closed-loop feedback parser
    p_pipe_feed = pipe_subs.add_parser("feedback", help="Ingest real-world market feedback and recruiter responses into Episodic Memory")
    p_pipe_feed.add_argument("jd_id", help="Opportunity ID (e.g. JD_30)")
    p_pipe_feed.add_argument("--outcome", "-o", required=True, help="Outcome (e.g. RATE_REJECTED, INTERVIEW_SCHEDULED, LOCATION_REJECTED, POSITIVE_RESPONSE)")
    p_pipe_feed.add_argument("--notes", "-n", default="", help="Detailed notes or learning takeaways")
    p_pipe_feed.add_argument("--rate", "-r", type=float, default=None, help="Actual rate disclosed or counter-offered (EUR/day)")
    p_pipe_feed.add_argument("--objection", default=None, help="Objection category (rate_budget, remote_policy, seniority_fit, technical_stack, timing)")

    pipe_subs.add_parser("sync", help="Re-sync opportunities from 07_TARGET_JDS directory")

    # Episodic Learning Memory subcommand (Chantier 3)
    p_mem = subparsers.add_parser("memory", help="Query CareerOS Episodic Learning Memory and employer track records")
    p_mem.add_argument("--company", "-c", default=None, help="Inspect historical track record and rules for a specific company or agency")

    # Offline Evaluation Benchmark subcommand (Chantier 1 - Benchmark Harness)
    p_bench = subparsers.add_parser("benchmark", help="Run offline evaluation benchmark against golden dataset")
    p_bench.add_argument("--profile", default=None, help="Filter test cases by candidate profile (e.g. alaa_roucadi, sophie_cloud_architect)")
    p_bench.add_argument("--case", default=None, help="Filter test case by ID substring (e.g. CASE_02)")
    p_bench.add_argument("--fast", action="store_true", default=True, help="Run fast heuristic & critic validation (default: True)")
    p_bench.add_argument("--llm", action="store_true", help="Run full LLM generation and evaluation loop")
    p_bench.add_argument("--debate", action="store_true", help="Run benchmark with Dual-Agent Debate Engine")
    p_bench.add_argument("--model", "-m", default=os.getenv("DEFAULT_MODEL", "gemini-3.8-flash"), help="Gemini model to use for LLM evaluations")

    # Automated Tailored CV Synthesis & PDF Compiler (Option 1)
    p_tailor = subparsers.add_parser("tailor", help="Synthesize tailored markdown resume and compile to pixel-perfect A4 PDF")
    p_tailor.add_argument("jd", help="Target JD filename, number (e.g. JD_30 or 30), or stem")
    p_tailor.add_argument("--profile", default=None, help="Candidate profile slug (e.g. alaa_roucadi, sophie_cloud_architect)")
    p_tailor.add_argument("--fast", action="store_true", default=True, help="Fast heuristic bullet ranking & formatting (default: True)")
    p_tailor.add_argument("--llm", action="store_true", help="Full LLM executive summary refinement")
    p_tailor.add_argument("--model", "-m", default=os.getenv("DEFAULT_MODEL", "gemini-3.8-flash"), help="Gemini model to use")

    # FastAPI Backend Server subcommand
    p_server = subparsers.add_parser("server", help="Start CareerOS FastAPI backend server with Vercel AI SDK streaming")
    p_server.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    p_server.add_argument("-p", "--port", type=int, default=8000, help="Port to bind (default: 8000)")
    p_server.add_argument("--reload", action="store_true", help="Enable auto-reload on code changes")

    # Audit Logs subcommand
    p_logs = subparsers.add_parser("logs", help="Inspect recent agent audit logs and interaction telemetry")
    p_logs.add_argument("-n", "--limit", type=int, default=15, help="Number of records to display (default: 15)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "scan":
        cmd_radar_scan(args)
    elif args.command == "fetch":
        cmd_radar_fetch(args)
    elif args.command == "report":
        cmd_radar_report(args)
    elif args.command == "gap-report":
        cmd_gap_report(args)
    elif args.command == "heatmap":
        cmd_heatmap(args)
    elif args.command == "export-pdf":
        cmd_export_pdf(args)
    elif args.command == "enrich":
        cmd_enrich(args)
    elif args.command == "agent":
        cmd_agent(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "pipeline":
        cmd_pipeline(args)
    elif args.command == "memory":
        cmd_memory(args)
    elif args.command == "tailor":
        cmd_tailor(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)
    elif args.command == "server":
        cmd_server(args)
    elif args.command == "logs":
        cmd_logs(args)

if __name__ == "__main__":
    main()

