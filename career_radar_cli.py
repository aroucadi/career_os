"""CareerOS Job Radar CLI - Autonomous Scraping & Scoring Tool."""
import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from career_radar.radar_agent import RadarAgent
from career_radar.storage import JobRepository

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()

def print_scorecard(scored):
    """Prints a detailed visual scorecard for a job."""
    score_color = "green" if scored.overall_match_score >= 70 else ("yellow" if scored.overall_match_score >= 50 else "red")
    
    header = f"[{score_color} bold]{scored.overall_match_score}/100[/] | [bold]{scored.job_title}[/] at [cyan]{scored.company}[/]"
    
    body = []
    body.append(f"[bold]URL:[/] [link={scored.url}]{scored.url}[/link]")
    if scored.saved_jd_file:
        body.append(f"[bold]Saved to:[/] [magenta]07_TARGET_JDS/{scored.saved_jd_file}[/]")
    body.append("")
    body.append("[bold underline]Pillar Scores Breakdown:[/]")
    for pillar, p_data in scored.scores.items():
        name_clean = pillar.replace("_", " ").title()
        body.append(f"  * [bold]{name_clean}:[/] {p_data.score}/{int(p_data.max_score)}")
        body.append(f"    [dim]{p_data.evidence}[/dim]")
    
    if scored.ats_keyword_gaps:
        body.append("")
        body.append(f"[bold yellow]ATS Keyword Gaps:[/] {', '.join(scored.ats_keyword_gaps)}")
    
    if scored.competency_gaps:
        body.append(f"[bold red]Competency Gaps:[/] {'; '.join(scored.competency_gaps)}")
        
    if scored.recommended_actions:
        body.append("")
        body.append("[bold cyan]Recommended Resume Tailoring:[/]")
        for action in scored.recommended_actions:
            body.append(f"  -> {action}")

    if scored.recruiter_pitch_hook:
        body.append("")
        body.append("[bold green]Direct Recruiter Outreach Hook:[/]")
        body.append(f"  \"{scored.recruiter_pitch_hook}\"")

    console.print(Panel("\n".join(body), title=header, border_style=score_color))

def cmd_scan(args):
    """Executes a live search and scoring run across job boards."""
    queries = [q.strip() for q in args.query.split(",")] if args.query else None
    
    console.print(Panel(
        f"[bold cyan]Starting CareerOS Job Radar Scan[/]\n"
        f"* Queries: {queries or 'Default AI Delivery Roles'}\n"
        f"* Contract Only: {args.contract}\n"
        f"* Remote Only: {args.remote}\n"
        f"* Time Filter: {args.time}\n"
        f"* Limit Per Query: {args.limit}",
        title="CareerOS Radar Initialized",
        border_style="blue"
    ))


    agent = RadarAgent()
    try:
        results = agent.scan_and_score(
            queries=queries,
            location=args.location,
            remote=args.remote,
            contract=args.contract,
            time_filter=args.time,
            limit_per_query=args.limit,
            min_score_to_save=args.min_score,
        )
        
        if not results:
            console.print("[yellow]No new jobs found matching the exact filters. Try relaxing the time window (--time week) or contract filter.[/yellow]")
            return

        console.print(f"\n[bold green]Scan Complete: Processed {len(results)} opportunities[/]\n")

        # Summary Table
        table = Table(title="Top Matched Opportunities (Ranked by CareerOS Fit)", show_header=True, header_style="bold magenta")
        table.add_column("Match", style="bold", justify="center", width=10)
        table.add_column("Job Title", style="cyan", width=36)
        table.add_column("Company", style="white", width=24)
        table.add_column("Saved File", style="dim", width=28)

        for s in results:
            score_style = "green" if s.overall_match_score >= 70 else ("yellow" if s.overall_match_score >= 50 else "red")
            table.add_row(
                f"[{score_style}]{s.overall_match_score}/100[/]",
                s.job_title[:35],
                s.company[:22],
                s.saved_jd_file or "Below Threshold",
            )
        console.print(table)
        console.print("\n")

        # Display full detailed scorecards for top matches
        for s in results[:3]:
            print_scorecard(s)

    finally:
        agent.close()

def cmd_fetch(args):
    """Fetches a specific job URL and evaluates it."""
    console.print(f"[cyan]Fetching and analyzing URL:[/] {args.url}")
    agent = RadarAgent()
    try:
        scored = agent.process_url(args.url)
        if not scored:
            console.print("[red]Failed to fetch or parse job from URL.[/red]")
            return
        print_scorecard(scored)
    finally:
        agent.close()

def cmd_report(args):
    """Displays report of previously analyzed jobs."""
    repo = JobRepository()
    scraped = repo._load_scraped()
    if not scraped:
        console.print("[yellow]No jobs in repository yet. Run 'scan' first.[/yellow]")
        return

    table = Table(title=f"All Scanned Jobs in Repository ({len(scraped)} total)", show_header=True, header_style="bold magenta")
    table.add_column("Match", style="bold", justify="center", width=10)
    table.add_column("Title", style="cyan", width=34)
    table.add_column("Company", style="white", width=24)
    table.add_column("Source", style="dim", width=10)
    table.add_column("URL", style="blue")

    items = list(scraped.values())
    items.sort(key=lambda x: (x.get("scored") or {}).get("overall_match_score", 0), reverse=True)

    for item in items:
        job = item["job"]
        scored = item.get("scored")
        score_val = scored.get("overall_match_score", 0) if scored else 0
        score_style = "green" if score_val >= 70 else ("yellow" if score_val >= 50 else "red")
        table.add_row(
            f"[{score_style}]{score_val}/100[/]" if scored else "N/A",
            job["title"][:32],
            job["company"][:20],
            job.get("source", "web"),
            job["url"],
        )
    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="CareerOS Job Radar — Autonomous Scraper & JD Evaluator")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan command
    p_scan = subparsers.add_parser("scan", help="Search and scrape newly published job offers")
    p_scan.add_argument("-q", "--query", default="AI Delivery Manager,Agentic Delivery Manager", help="Comma-separated query terms")
    p_scan.add_argument("-l", "--location", default="Worldwide", help="Location (e.g. Worldwide, France, Europe)")
    p_scan.add_argument("--contract", action="store_true", default=True, help="Filter for Contract / Freelance (default: True)")
    p_scan.add_argument("--no-contract", dest="contract", action="store_false", help="Do not filter for contract only")
    p_scan.add_argument("--remote", action="store_true", default=True, help="Filter for Remote (default: True)")
    p_scan.add_argument("--no-remote", dest="remote", action="store_false", help="Do not filter for remote only")
    p_scan.add_argument("-t", "--time", default="week", choices=["24h", "3d", "week", "month"], help="Time posted filter")
    p_scan.add_argument("-n", "--limit", type=int, default=4, help="Max results per query")
    p_scan.add_argument("--min-score", type=int, default=50, help="Minimum score to persist to 07_TARGET_JDS")

    # Fetch command
    p_fetch = subparsers.add_parser("fetch", help="Fetch and analyze a single job description URL")
    p_fetch.add_argument("-u", "--url", required=True, help="Direct URL to job description")

    # Report command
    p_report = subparsers.add_parser("report", help="Display summary report of all tracked jobs")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "fetch":
        cmd_fetch(args)
    elif args.command == "report":
        cmd_report(args)

if __name__ == "__main__":
    main()
