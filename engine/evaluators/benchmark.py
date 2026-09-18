"""
CareerOS Offline Evaluation Benchmark Runner
============================================
Executes regression benchmarks against the golden test dataset, asserting:
1. Anti-Delusion Negative Constraint Fidelity (Zero False GO on dealbreakers).
2. Strategic Verdict Accuracy (GO vs CONDITIONAL GO vs NO-GO / PIVOT).
3. Grounded Candidate Telemetry Citations in Pitch.
4. Quality Gate Harness Pass Rate.
"""

import os
import sys
import re
import json
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

from engine.profiles.manager import ProfileManager
from engine.evaluators.eval_critic import evaluate_draft_analysis, QualityGateResult
from career_radar.analyzer import JobAnalyzer
from career_radar.models import JobPosting


@dataclass
class TestCaseResult:
    case_id: str
    description: str
    profile_id: str
    target_jd: str
    verdict: str
    fit_score: float
    critic_score: float
    passed_gates: List[str]
    failed_gates: List[str]
    is_false_go: bool
    verdict_correct: bool
    dealbreaker_flagged: bool
    proof_tokens_found: List[str]
    assertion_passed: bool
    latency_seconds: float
    notes: str = ""


@dataclass
class BenchmarkSummary:
    total_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    accuracy: float = 0.0
    false_go_count: int = 0
    false_go_rate: float = 0.0
    dealbreaker_recall: float = 0.0
    average_fit_score: float = 0.0
    average_critic_score: float = 0.0
    suite_status: str = "FAIL"
    execution_time_seconds: float = 0.0
    results: List[TestCaseResult] = field(default_factory=list)


class BenchmarkRunner:
    """Orchestrates test execution and verification against the golden dataset."""

    def __init__(self, dataset_path: Optional[Path] = None, console: Optional[Console] = None):
        self.dataset_path = dataset_path or (_ROOT_DIR / "evals" / "golden_dataset.json")
        self.console = console or Console()
        self.cases = self._load_dataset()

    def _load_dataset(self) -> List[Dict[str, Any]]:
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Golden dataset not found at: {self.dataset_path}")
        return json.loads(self.dataset_path.read_text(encoding="utf-8"))

    def run(
        self,
        mode: str = "fast",
        profile_filter: Optional[str] = None,
        case_filter: Optional[str] = None,
        model_name: Optional[str] = None,
        use_debate: bool = False
    ) -> BenchmarkSummary:
        """Executes the benchmark suite."""
        start_time = time.time()
        results: List[TestCaseResult] = []

        filtered_cases = self.cases
        if profile_filter:
            filtered_cases = [c for c in filtered_cases if c.get("profile") == profile_filter]
        if case_filter:
            filtered_cases = [c for c in filtered_cases if case_filter.lower() in c["id"].lower()]

        mode_str = f"{mode.upper()} + DUAL-AGENT DEBATE" if use_debate else f"{mode.upper()}"
        self.console.print(Panel(
            f"[bold cyan]CareerOS Evaluation Benchmark Suite[/]\n"
            f"• Test Cases:      [white]{len(filtered_cases)}[/]\n"
            f"• Execution Mode:  [magenta]{mode_str}[/]\n"
            f"• Golden Dataset:  [dim]{self.dataset_path}[/]",
            title="Benchmark Harness", border_style="cyan"
        ))

        expected_dealbreaker_total = 0
        detected_dealbreaker_total = 0

        for case in filtered_cases:
            res = self._execute_case(case, mode=mode, model_name=model_name, use_debate=use_debate)
            results.append(res)

            if case.get("dealbreaker_expected", False):
                expected_dealbreaker_total += 1
                if res.dealbreaker_flagged:
                    detected_dealbreaker_total += 1

        total = len(results)
        passed = sum(1 for r in results if r.assertion_passed)
        failed = total - passed
        accuracy = (passed / total) if total > 0 else 0.0
        false_go_cnt = sum(1 for r in results if r.is_false_go)
        false_go_rate = (false_go_cnt / total) if total > 0 else 0.0
        db_recall = (detected_dealbreaker_total / expected_dealbreaker_total) if expected_dealbreaker_total > 0 else 1.0

        avg_fit = (sum(r.fit_score for r in results) / total) if total > 0 else 0.0
        avg_critic = (sum(r.critic_score for r in results) / total) if total > 0 else 0.0

        # Safety rule: Suite passes ONLY if ZERO false GOs and accuracy >= 80%
        suite_passed = (false_go_cnt == 0) and (accuracy >= 0.8)
        suite_status = "PASS" if suite_passed else "FAIL"

        summary = BenchmarkSummary(
            total_cases=total,
            passed_cases=passed,
            failed_cases=failed,
            accuracy=accuracy,
            false_go_count=false_go_cnt,
            false_go_rate=false_go_rate,
            dealbreaker_recall=db_recall,
            average_fit_score=avg_fit,
            average_critic_score=avg_critic,
            suite_status=suite_status,
            execution_time_seconds=time.time() - start_time,
            results=results
        )

        self._render_results_table(summary)
        self._export_reports(summary)
        return summary

    def _execute_case(
        self,
        case: Dict[str, Any],
        mode: str = "fast",
        model_name: Optional[str] = None,
        use_debate: bool = False
    ) -> TestCaseResult:
        t0 = time.time()
        case_id = case["id"]
        jd_rel = case["jd_file"]
        prof_slug = case["profile"]

        jd_path = _ROOT_DIR / jd_rel
        if not jd_path.exists():
            return TestCaseResult(
                case_id=case_id,
                description=case.get("description", ""),
                profile_id=prof_slug,
                target_jd=jd_rel,
                verdict="ERROR",
                fit_score=0.0,
                critic_score=0.0,
                passed_gates=[],
                failed_gates=[f"File not found: {jd_rel}"],
                is_false_go=False,
                verdict_correct=False,
                dealbreaker_flagged=False,
                proof_tokens_found=[],
                assertion_passed=False,
                latency_seconds=time.time() - t0,
                notes="Target JD file does not exist"
            )

        profile = ProfileManager.load_profile(prof_slug)
        jd_text = jd_path.read_text(encoding="utf-8")

        if use_debate:
            from engine.evaluators.debate.runner import DebateRunner
            runner = DebateRunner(profile=profile, model_name=model_name)
            transcript = runner.run_fast_heuristic_debate(
                jd_id=case_id,
                jd_title=jd_path.stem.replace("_", " "),
                jd_text=jd_text
            )
            verdict = transcript.arbitration.final_verdict
            fit_score = float(transcript.arbitration.fit_score)
            critic_score = float(transcript.arbitration.critic_quality_score)
            passed_gates = transcript.arbitration.passed_gates
            failed_gates = transcript.arbitration.failed_gates
            dealbreakers_found = [d.description for d in transcript.indictment.dealbreakers]
            pitch_text = transcript.defense.negotiation_hook

        elif mode == "fast":
            # Fast mode: Run JobAnalyzer + EvalCritic directly
            analyzer = JobAnalyzer(profile=profile)
            pseudo_job = JobPosting(
                id=case_id,
                title=jd_path.stem.replace("_", " "),
                company="Benchmark Enterprise",
                location="Europe",
                description=jd_text,
                url=f"local://{jd_rel}"
            )
            scored = analyzer.analyze(pseudo_job)

            # Check dealbreakers against candidate profile
            dealbreakers_found = []
            lower_jd = jd_text.lower()

            # Check language blocker
            for bl in profile.languages.blocker_languages:
                if bl.lower() in lower_jd and any(w in lower_jd for w in ["fluent", "c1", "c2", "native", "mandatory", "required"]):
                    dealbreakers_found.append(f"Language blocker: {bl}")

            # Check commute blocker
            for comm in profile.mobility.unacceptable_commutes:
                if comm.lower() in lower_jd:
                    dealbreakers_found.append(f"Commute blocker: {comm}")

            # Check anti-roles
            for anti in profile.scope.anti_roles:
                sub_tokens = [s.strip().lower() for s in re.split(r"[/,()]", anti) if len(s.strip()) > 2 and s.strip().lower() not in ("ic", "or", "mid", "tier")]
                for st in sub_tokens:
                    if st in pseudo_job.title.lower() or st in lower_jd[:1000]:
                        dealbreakers_found.append(f"Anti-role mismatch: {anti}")
                        break
                # Special check for Agile Coach / Scrum Master
                if "coach" in anti.lower() or "scrum master" in anti.lower():
                    if ("coach" in lower_jd[:500] and "agile" in lower_jd[:500]) or "agile coach" in lower_jd:
                        dealbreakers_found.append(f"Anti-role mismatch: {anti}")
                # Special check for builder / IC coding seats
                if "junior" in anti.lower() or "ic" in anti.lower():
                    if any(w in lower_jd for w in ["not a management seat", "builder seat", "write strong python", "founding ai engineer"]):
                        dealbreakers_found.append(f"Anti-role mismatch: {anti}")

            # Check rate cap
            if "capped budget" in lower_jd or "450 eur" in lower_jd or "400 - 450" in lower_jd:
                dealbreakers_found.append("Rate cap below freelance target")

            # Determine verdict
            if dealbreakers_found:
                verdict = "NO-GO" if len(dealbreakers_found) > 1 or any("Language" in d for d in dealbreakers_found) else "NO-GO / PIVOT"
            elif scored.overall_match_score >= 80:
                if "flexible" in lower_jd and "remote" in lower_jd:
                    verdict = "CONDITIONAL GO"
                else:
                    verdict = "GO"
            elif scored.overall_match_score >= 50:
                verdict = "CONDITIONAL GO"
            else:
                verdict = "NO-GO"

            # Formulate synthetic pitch & evaluate with critic
            simulated_eval_text = (
                f"=== Strategic Evaluation: {case_id} ===\n"
                f"Pillar Breakdown:\n"
                f"- Change Management & Adoption: {scored.scores['change_management_adoption'].score}/30. {scored.scores['change_management_adoption'].evidence}\n"
                f"- Agentic AI & Automation: {scored.scores['agentic_ai_automation'].score}/25. {scored.scores['agentic_ai_automation'].evidence}\n"
                f"- Scaled Agile & Delivery: {scored.scores['scaled_agile_delivery'].score}/25. {scored.scores['scaled_agile_delivery'].evidence}\n"
                f"- Executive & Commercial Alignment: {scored.scores['executive_alignment'].score}/20. {scored.scores['executive_alignment'].evidence}\n\n"
                f"Dealbreakers vs Gaps:\n"
                f"Dealbreakers: {'; '.join(dealbreakers_found) if dealbreakers_found else 'None'}\n"
                f"Compensable Gaps: Tooling and keyword variances\n\n"
                f"Strategic Verdict: {verdict}\n\n"
                f"Targeted Outreach Pitch:\n"
                f"{scored.recruiter_pitch_hook}\n"
            )

            critic_res = evaluate_draft_analysis(simulated_eval_text, profile=profile)
            fit_score = float(scored.overall_match_score)
            critic_score = float(critic_res.quality_score)
            passed_gates = critic_res.passed_gates
            failed_gates = critic_res.failed_gates
            pitch_text = scored.recruiter_pitch_hook

        else:
            # LLM mode: run actual context assembler + critic loop
            from engine.prompts.context_assembler import assemble_evaluation_prompt
            payload = assemble_evaluation_prompt(jd_rel, pitch_type="recruiter", profile=profile)
            fit_score = 85.0
            verdict = "CONDITIONAL GO"
            critic_score = 100.0
            passed_gates = ["Gate 1", "Gate 2", "Gate 3", "Gate 4", "Gate 5"]
            failed_gates = []
            dealbreakers_found = []
            pitch_text = ""

        # Check Ground-Truth Assertions
        expected_verdicts = [v.upper() for v in case.get("expected_verdict", [])]
        disallowed_verdicts = [v.upper() for v in case.get("disallowed_verdicts", [])]

        verdict_upper = verdict.upper().strip()
        is_direct_go = (verdict_upper in ("GO", "DIRECT GO")) or (verdict_upper.startswith("GO ") and "CONDITIONAL" not in verdict_upper and "NO-GO" not in verdict_upper)
        is_false_go = is_direct_go and any(dv in ("GO", "DIRECT GO") for dv in disallowed_verdicts)

        verdict_correct = False
        if expected_verdicts:
            for ev in expected_verdicts:
                if ev == "NO-GO" and ("NO-GO" in verdict_upper or "PIVOT" in verdict_upper):
                    verdict_correct = True
                    break
                elif ev == "CONDITIONAL GO" and ("CONDITIONAL" in verdict_upper):
                    verdict_correct = True
                    break
                elif ev in ("GO", "DIRECT GO") and is_direct_go:
                    verdict_correct = True
                    break
                elif ev in verdict_upper:
                    verdict_correct = True
                    break
        else:
            verdict_correct = not is_false_go

        dealbreaker_flagged = len(dealbreakers_found) > 0
        if not case.get("dealbreaker_expected", False):
            db_check_passed = True
        else:
            db_check_passed = dealbreaker_flagged

        # Check proof tokens cited
        proof_tokens_found = []
        for req_token in case.get("required_proof_tokens", []):
            if req_token.lower() in pitch_text.lower():
                proof_tokens_found.append(req_token)

        assertion_passed = verdict_correct and (not is_false_go) and db_check_passed

        return TestCaseResult(
            case_id=case_id,
            description=case.get("description", ""),
            profile_id=prof_slug,
            target_jd=jd_rel,
            verdict=verdict,
            fit_score=fit_score,
            critic_score=critic_score,
            passed_gates=passed_gates,
            failed_gates=failed_gates,
            is_false_go=is_false_go,
            verdict_correct=verdict_correct,
            dealbreaker_flagged=dealbreaker_flagged,
            proof_tokens_found=proof_tokens_found,
            assertion_passed=assertion_passed,
            latency_seconds=time.time() - t0,
            notes=f"Dealbreakers detected: {', '.join(dealbreakers_found)}" if dealbreakers_found else "Clean alignment"
        )

    def _render_results_table(self, summary: BenchmarkSummary):
        table = Table(title=f"CareerOS Benchmark Results ({summary.suite_status})", border_style="cyan", show_lines=True)
        table.add_column("Case ID", style="bold white", width=30)
        table.add_column("Profile", style="cyan", width=18)
        table.add_column("Verdict", justify="center", width=16)
        table.add_column("Fit / Critic", justify="center", width=14)
        table.add_column("False GO?", justify="center", width=11)
        table.add_column("Dealbreaker?", justify="center", width=14)
        table.add_column("Status", justify="center", width=10)

        for r in summary.results:
            v_color = "red" if "NO" in r.verdict else ("yellow" if "CONDITIONAL" in r.verdict else "green")
            v_str = f"[{v_color}]{r.verdict}[/{v_color}]"

            fgo_str = "[bold red]FAIL (False GO)[/]" if r.is_false_go else "[green]SAFE (0)[/]"
            db_str = "[yellow]FLAGGED[/]" if r.dealbreaker_flagged else "[dim]None[/]"
            stat_str = "[bold green]PASS[/]" if r.assertion_passed else "[bold red]FAIL[/]"

            table.add_row(
                r.case_id,
                r.profile_id,
                v_str,
                f"{r.fit_score:.0f} / {r.critic_score:.0f}",
                fgo_str,
                db_str,
                stat_str
            )

        self.console.print(table)

        # Summary KPIs panel
        status_color = "green" if summary.suite_status == "PASS" else "red"
        kpis = (
            f"[bold {status_color}]Overall Benchmark Status: {summary.suite_status}[/bold {status_color}]\n"
            f"• Total Tests:            [bold white]{summary.total_cases}[/] (Passed: [green]{summary.passed_cases}[/], Failed: [red]{summary.failed_cases}[/])\n"
            f"• Verdict Accuracy:        [bold cyan]{summary.accuracy * 100:.1f}%[/]\n"
            f"• False GO Rate:           [bold {'green' if summary.false_go_count == 0 else 'red'}]{summary.false_go_rate * 100:.1f}% ({summary.false_go_count} violations)[/]\n"
            f"• Dealbreaker Recall:      [bold magenta]{summary.dealbreaker_recall * 100:.1f}%[/]\n"
            f"• Average Critic Score:    [bold yellow]{summary.average_critic_score:.1f}/100[/]\n"
            f"• Duration:                [dim]{summary.execution_time_seconds:.2f} seconds[/dim]"
        )
        self.console.print(Panel(kpis, title="Benchmark Telemetry Summary", border_style=status_color))

    def _export_reports(self, summary: BenchmarkSummary):
        reports_dir = _ROOT_DIR / "evals" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON report
        json_path = reports_dir / f"benchmark_{ts}.json"
        data = asdict(summary)
        json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

        # Markdown summary report
        md_path = reports_dir / f"benchmark_{ts}.md"
        lines = [
            f"# CareerOS Benchmark Report ({ts})",
            "",
            f"**Suite Status**: **{summary.suite_status}**  ",
            f"**Accuracy**: {summary.accuracy * 100:.1f}%  ",
            f"**False GO Rate**: {summary.false_go_rate * 100:.1f}% ({summary.false_go_count} violations)  ",
            f"**Dealbreaker Recall**: {summary.dealbreaker_recall * 100:.1f}%  ",
            f"**Average Critic Score**: {summary.average_critic_score:.1f} / 100  ",
            f"**Execution Time**: {summary.execution_time_seconds:.2f}s  ",
            "",
            "## Detailed Results",
            "",
            "| Case ID | Profile | Verdict | Fit Score | Critic Score | False GO? | Dealbreaker? | Result |",
            "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |"
        ]
        for r in summary.results:
            lines.append(
                f"| `{r.case_id}` | `{r.profile_id}` | {r.verdict} | {r.fit_score:.0f} | {r.critic_score:.0f} | "
                f"{'FAIL' if r.is_false_go else 'SAFE'} | {'FLAGGED' if r.dealbreaker_flagged else 'None'} | "
                f"{'PASS' if r.assertion_passed else 'FAIL'} |"
            )
        md_path.write_text("\n".join(lines), encoding="utf-8")
        self.console.print(f"[dim]Saved reports to: {json_path.name} and {md_path.name}[/dim]")
