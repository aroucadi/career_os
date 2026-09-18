"""
Pipeline Views & Multi-Persona Renderers
=========================================
Renders Rich terminal tables, Kanban pipelines, and persona-specific briefings.
"""

from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .models import Opportunity, PipelineStage, PersonaType
from engine.profiles.models import CandidateProfile


STAGE_COLORS = {
    PipelineStage.DISCOVERED: "dim cyan",
    PipelineStage.QUALIFIED: "cyan",
    PipelineStage.PITCH_READY: "yellow",
    PipelineStage.APPLIED: "blue",
    PipelineStage.SCREENING_SCHEDULED: "magenta",
    PipelineStage.INTERVIEWING: "bold magenta",
    PipelineStage.OFFER_EXTENDED: "bold green",
    PipelineStage.NEGOTIATING: "bold yellow",
    PipelineStage.ACCEPTED: "green on black",
    PipelineStage.REJECTED: "dim red",
    PipelineStage.ARCHIVED: "dim white",
}


def render_pipeline_table(opportunities: List[Opportunity], title: str = "CareerOS Active Pipeline") -> Table:
    """Renders high-visibility terminal table of opportunities."""
    table = Table(title=title, border_style="cyan", show_lines=True)
    table.add_column("ID", style="bold white", width=8)
    table.add_column("Role & Company", style="white", min_width=28)
    table.add_column("Location", style="dim white", width=18)
    table.add_column("Score", justify="center", width=8)
    table.add_column("Verdict", justify="center", width=16)
    table.add_column("Stage", style="bold", width=20)
    table.add_column("Last Updated", style="dim", width=12)

    # Sort: active stages first, then score
    stage_order = {
        PipelineStage.OFFER_EXTENDED: 0,
        PipelineStage.NEGOTIATING: 1,
        PipelineStage.INTERVIEWING: 2,
        PipelineStage.SCREENING_SCHEDULED: 3,
        PipelineStage.APPLIED: 4,
        PipelineStage.PITCH_READY: 5,
        PipelineStage.QUALIFIED: 6,
        PipelineStage.DISCOVERED: 7,
        PipelineStage.REJECTED: 8,
        PipelineStage.ACCEPTED: 9,
        PipelineStage.ARCHIVED: 10,
    }

    sorted_opps = sorted(
        opportunities,
        key=lambda o: (stage_order.get(o.stage, 99), -(o.evaluation.overall_score if o.evaluation else 0))
    )

    for opp in sorted_opps:
        color = STAGE_COLORS.get(opp.stage, "white")
        stage_badge = f"[{color}]{opp.stage.value}[/{color}]"

        score_str = f"[bold green]{opp.evaluation.overall_score:.0f}[/]" if opp.evaluation else "[dim]--[/]"
        verdict_str = "[dim]PENDING[/]"
        if opp.evaluation:
            v = opp.evaluation.strategic_verdict
            if "GO" in v and "NO" not in v and "CONDITIONAL" not in v:
                verdict_str = f"[bold green]{v}[/]"
            elif "CONDITIONAL" in v:
                verdict_str = f"[yellow]{v}[/]"
            else:
                verdict_str = f"[red]{v}[/]"

        updated_short = opp.last_updated_at[:10] if opp.last_updated_at else ""

        table.add_row(
            opp.id,
            f"[bold]{opp.job_title[:32]}[/]\n[dim]{opp.company[:32]}[/]",
            opp.location[:18],
            score_str,
            verdict_str,
            stage_badge,
            updated_short
        )

    return table


def render_persona_view(
    opp: Opportunity,
    persona: PersonaType,
    console: Console,
    profile: Optional[CandidateProfile] = None
):
    """Renders rich persona-specific briefing panel dynamically bound to candidate profile."""
    from engine.profiles.manager import ProfileManager
    prof = profile or ProfileManager.load_profile()

    if persona == PersonaType.CANDIDATE:
        _render_candidate_view(opp, console, prof)
    elif persona == PersonaType.RECRUITER:
        _render_recruiter_view(opp, console, prof)
    elif persona == PersonaType.HIRING_MANAGER:
        _render_hiring_manager_view(opp, console, prof)
    elif persona == PersonaType.CAREER_PIVOT:
        _render_pivot_view(opp, console, prof)


def _render_candidate_view(opp: Opportunity, console: Console, prof: CandidateProfile):
    intel = opp.persona_intel.candidate
    score = opp.evaluation.overall_score if opp.evaluation else "--"
    verdict = opp.evaluation.strategic_verdict if opp.evaluation else "PENDING"
    target_rate = prof.commercials.freelance_tjm_eur if intel.target_rate_eur == "850-1000 EUR/day" else intel.target_rate_eur

    proof_summary = "; ".join([f"{p.category}: {p.evidence}" for p in prof.proof_metrics[:2]])
    strat = intel.strategic_advice or f"Review Dealbreakers: Check remote policy vs {prof.mobility.base_location} base; {prof.languages.fluent_languages[0]} verified."
    hook = intel.pitch_hook or f"Reference verified candidate telemetry: {proof_summary}"

    content = f"""[bold cyan]Target Role:[/] {opp.job_title} at {opp.company}
[bold cyan]Location / Working Model:[/] {opp.location} ({opp.employment_type})
[bold cyan]Fit Score:[/] [bold green]{score}/100[/] | [bold cyan]Verdict:[/] [yellow]{verdict}[/]
[bold cyan]Negotiation Leverage:[/] [bold magenta]{intel.negotiation_leverage}[/] | [bold cyan]Target Rate:[/] {target_rate}

[bold underline white]Candidate Strategic Positioning:[/]
{strat}

[bold underline white]Grounded Pitch Hook:[/]
{hook}
"""
    console.print(Panel(content, title=f"Candidate View ({prof.full_name}): {opp.id}", border_style="green"))


def _render_recruiter_view(opp: Opportunity, console: Console, prof: CandidateProfile):
    intel = opp.persona_intel.recruiter
    proof_bullets = "\n".join([f"• {p.label}: {p.evidence}" for p in prof.proof_metrics[:3]])

    content = f"""[bold cyan]Role Qualified:[/] {opp.job_title} ({opp.company})
[bold cyan]Rate Feasibility:[/] [bold green]{intel.rate_feasibility} ({prof.commercials.freelance_tjm_eur})[/]
[bold cyan]Availability:[/] [bold magenta]{intel.availability_status}[/]

[bold underline white]Executive Candidate Screening Summary (Grounded Proof Points):[/]
{proof_bullets}

[bold underline white]Recruiter Screening Checklist:[/]
• [x] Working Language: {', '.join(prof.languages.fluent_languages)}.
• [x] Mobility: {prof.mobility.remote_preference}.
• [x] Seniority Stature: {prof.scope.seniority} ({', '.join(prof.scope.primary_titles[:2])}).
"""
    console.print(Panel(content, title=f"Recruiter Qualification View ({prof.full_name}): {opp.id}", border_style="blue"))


def _render_hiring_manager_view(opp: Opportunity, console: Console, prof: CandidateProfile):
    intel = opp.persona_intel.hiring_manager
    
    questions = []
    if prof.proof_metrics:
        for idx, pm in enumerate(prof.proof_metrics[:3], 1):
            questions.append(f"{idx}. [bold white]{pm.category} ({pm.label}):[/] Walk through how you achieved '{pm.evidence}' and how you would adapt that approach to {opp.company}'s context.")
    
    remaining_needed = 5 - len(questions)
    generic_probes = [
        ("Stakeholder Alignment", f"How do you resolve resistance when aligning leadership and engineering on {opp.job_title} initiatives?"),
        ("Autonomous Delivery", f"How do you ensure predictability and high throughput while operating under a {prof.mobility.remote_preference} model?"),
        ("Quality & Risk Governance", "Walk me through a high-stakes release decision where you had to balance time-to-market against strict quality or compliance gates?"),
        ("Measurement & Impact", "What concrete telemetry and KPIs do you track to measure the direct business return of your deliverables?")
    ]
    for cat, probe in generic_probes[:remaining_needed]:
        questions.append(f"{len(questions)+1}. [bold white]{cat}:[/] {probe}")

    q_block = "\n".join(questions)

    anti_match = any(ar.lower() in opp.job_title.lower() for ar in prof.scope.anti_roles) if prof.scope.anti_roles else False
    scope_risk = "[red]HIGH (Matches Anti-Role!)[/red]" if anti_match else "[green]LOW (Strong Seniority Alignment)[/green]"

    content = f"""[bold cyan]Mandate:[/] {opp.job_title} | [bold cyan]Evaluation Stage:[/] {opp.stage.value}

[bold underline yellow]Top 5 Technical & Behavioral Interview Questions (Gap-Probing):[/]
{q_block}

[bold underline white]Hiring Risk Scorecard ({prof.full_name}):[/]
• Technical Delivery Risk: [green]LOW[/green] ({prof.scope.seniority}, {', '.join(prof.scope.core_domains[:2]) if prof.scope.core_domains else 'proven enterprise scale'}).
• Remote Autonomy Risk: [green]ZERO[/green] (autonomous track record from {prof.mobility.base_location}, {prof.mobility.remote_preference}).
• Scope Alignment: {scope_risk} (target roles: {', '.join(prof.scope.primary_titles[:2])}).
"""
    console.print(Panel(content, title=f"Hiring Manager & Interviewer View ({prof.full_name}): {opp.id}", border_style="magenta"))


def _render_pivot_view(opp: Opportunity, console: Console, prof: CandidateProfile):
    primary_target = prof.scope.primary_titles[0] if prof.scope.primary_titles else opp.job_title
    proof_assets = "\n".join([f"• [bold white]{p.category}:[/] {p.evidence}" for p in prof.proof_metrics[:3]])
    anti_guard = f"\n• Avoid anti-roles: [yellow]{', '.join(prof.scope.anti_roles)}[/yellow]" if prof.scope.anti_roles else ""

    content = f"""[bold cyan]Candidate Background:[/] {prof.headline}
[bold cyan]Target Trajectory:[/] {opp.job_title} ──► [bold green]{primary_target}[/]

[bold underline white]Core Skill Delta & Strategic Focus Areas:[/]
1. [bold white]Leadership & Scope:[/] Elevate from tactical execution to organizational operating model and strategic direction.
2. [bold white]Domain Governance:[/] Anchor credibility in rigorous standards, compliance, and risk frameworks relevant to {', '.join(prof.scope.core_domains[:2]) if prof.scope.core_domains else 'enterprise systems'}.
3. [bold white]Telemetry & Value Realization:[/] Shift reporting from operational activity to quantifiable business value, cost efficiency, and delivery predictability.

[bold underline white]Transferable Verified Assets ({prof.full_name}):[/]
• {prof.scope.seniority} in {', '.join(prof.scope.core_domains)}.{anti_guard}
{proof_assets}
"""
    console.print(Panel(content, title=f"Career Pivot & Upskilling View ({prof.full_name}): {opp.id}", border_style="yellow"))
