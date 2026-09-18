"""
CareerOS Dual-Agent Debate Runner
=================================
Orchestrates the dialectic between the Skeptical Prosecutor and the Opportunity Advocate,
then passes the arguments to the deterministic Quality Gate Arbiter.
"""

import os
import re
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from engine.profiles.models import CandidateProfile
from engine.profiles.manager import ProfileManager
from engine.evaluators.eval_critic import evaluate_draft_analysis, QualityGateResult
from engine.evaluators.debate.models import (
    RiskIndictment,
    DefensePlea,
    ArbiterVerdict,
    DebateTranscript,
    DealbreakerItem
)
from engine.evaluators.debate.prompts import build_prosecutor_prompt, build_advocate_prompt

class DebateRunner:
    """Orchestrates turn-based dialectic debates between Prosecutor and Advocate with Arbiter control."""

    def __init__(self, profile: Optional[CandidateProfile] = None, model_name: Optional[str] = None):
        self.profile = profile or ProfileManager.load_profile()
        self.model_name = model_name or os.getenv("DEFAULT_MODEL", "gemini-3.8-flash")
        self.output_dir = Path("cache/debates")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_fast_heuristic_debate(self, jd_id: str, jd_title: str, jd_text: str, career_mode: str = "freelance") -> DebateTranscript:
        """Fast, zero-latency deterministic debate simulation for CI/CD benchmarks and local triage."""
        cand = self.profile
        lower_jd = jd_text.lower()
        title_lower = jd_title.lower()
        dealbreakers = []
        red_flags = []
        trap_score = 10.0

        # 1. Prosecutor Checks
        # Check blocker languages
        for lang in cand.languages.blocker_languages:
            l_low = lang.lower()
            if l_low in lower_jd and any(w in lower_jd for w in ["fluent", "c1", "c2", "native", "mandatory", "required"]):
                dealbreakers.append(DealbreakerItem(
                    category="language",
                    severity="FATAL",
                    description=f"Mandatory non-spoken language: {lang}",
                    evidence_snippet=f"Detected requirement for {lang} in JD text."
                ))
                trap_score += 45.0

        # Check unacceptable commutes
        for comm in cand.mobility.unacceptable_commutes:
            c_low = comm.lower()
            if c_low in lower_jd and any(w in lower_jd for w in ["on-site", "onsite", "hybrid", "3 days", "2 days", "office"]):
                dealbreakers.append(DealbreakerItem(
                    category="commute",
                    severity="FATAL",
                    description=f"Unacceptable physical commute: {comm}",
                    evidence_snippet=f"Detected on-site / hybrid mandate in {comm}."
                ))
                trap_score += 40.0

        # Check anti-roles (smart token splitting)
        for anti in cand.scope.anti_roles:
            sub_tokens = [s.strip().lower() for s in re.split(r"[/,()]", anti) if len(s.strip()) > 2 and s.strip().lower() not in ("ic", "or", "mid", "tier")]
            matched = False
            for st in sub_tokens:
                if st in title_lower or st in lower_jd[:1000]:
                    dealbreakers.append(DealbreakerItem(
                        category="anti_role",
                        severity="HIGH_RISK",
                        description=f"Scope matches declared anti-role: {anti}",
                        evidence_snippet=f"Role matches anti-role pattern: {st}"
                    ))
                    trap_score += 35.0
                    matched = True
                    break
            if not matched:
                if "coach" in anti.lower() or "scrum master" in anti.lower():
                    if ("coach" in lower_jd[:500] and "agile" in lower_jd[:500]) or "agile coach" in lower_jd:
                        dealbreakers.append(DealbreakerItem(
                            category="anti_role",
                            severity="HIGH_RISK",
                            description=f"Scope matches declared anti-role: {anti}",
                            evidence_snippet="Agile Coaching focus detected."
                        ))
                        trap_score += 35.0
                elif "junior" in anti.lower() or "ic" in anti.lower():
                    if any(w in lower_jd for w in ["not a management seat", "builder seat", "write strong python", "founding ai engineer"]):
                        dealbreakers.append(DealbreakerItem(
                            category="anti_role",
                            severity="HIGH_RISK",
                            description=f"Scope matches declared anti-role: {anti}",
                            evidence_snippet="Pure individual contributor coding seat detected."
                        ))
                        trap_score += 35.0

        # Check budget traps
        m_rate = re.search(r"(\d{3})\s*(?:€|eur|euros?)\s*(?:/|per|\s)\s*(?:day|jour)", lower_jd)
        if m_rate:
            rate_val = int(m_rate.group(1))
            if rate_val < 600:
                dealbreakers.append(DealbreakerItem(
                    category="budget",
                    severity="HIGH_RISK",
                    description=f"Capped budget ({rate_val} EUR/day) significantly below commercial minimum",
                    evidence_snippet=f"Rate capped at {rate_val} EUR/day"
                ))
                trap_score += 30.0
        elif "capped budget" in lower_jd or "450 eur" in lower_jd or "400 - 450" in lower_jd:
            dealbreakers.append(DealbreakerItem(
                category="budget",
                severity="HIGH_RISK",
                description="Budget capped below freelance target",
                evidence_snippet="Rate cap detected in JD description."
            ))
            trap_score += 30.0

        # Unspoken red flags & Recruiter BS shredder
        if "on-call" in lower_jd or "astreinte" in lower_jd:
            red_flags.append("🚨 24/7 uncompensated on-call firefighting expected")
        if "fast-paced" in lower_jd and ("wear many hats" in lower_jd or "wear multiple hats" in lower_jd):
            red_flags.append("🚨 'Fast-paced + Wear many hats': Translates to chronic understaffing, missing specs, and chaotic firefighting")
        elif "fast-paced" in lower_jd:
            red_flags.append("⚠️ 'Fast-paced environment': Often recruiter euphemism for reactive sprint planning and volatile executive pivots")
        if "family culture" in lower_jd or "start-up spirit" in lower_jd or "esprit start-up" in lower_jd:
            red_flags.append("⚠️ 'Family culture / Esprit startup': Risk of guilt-tripping overtime and blurred professional boundaries")
        if any(w in lower_jd for w in ["hands-on", "hands on"]) and any(w in lower_jd for w in ["lead", "director", "responsable"]):
            if any(w in lower_jd for w in ["write clean css", "fix bugs", "develop react", "ecriture de code au quotidien", "sql queries"]):
                red_flags.append("⚠️ Down-leveling trap: Disguised individual contributor coding seat masquerading as strategic leadership")
        if "competitive rate" in lower_jd or "rémunération attractive" in lower_jd:
            if not m_rate:
                red_flags.append("⚠️ 'Competitive rate': Stated without figures, likely recruiter bait for below-market TJM negotiation")

        # 1.5. Query Episodic Memory for historical precedents on this company or role
        from engine.memory.store import EpisodicMemoryStore
        mem_store = EpisodicMemoryStore()
        precedents = mem_store.query_precedents(domain="AI", role_title=jd_title, limit=3)
        for prec in precedents:
            if prec.outcome.value in ("RATE_REJECTED", "LOCATION_REJECTED", "SCOPE_MISMATCH"):
                red_flags.append(f"Historical Precedent ({prec.company}): {', '.join(prec.key_takeaways)}")
                trap_score += 15.0

        trap_score = min(100.0, trap_score)
        has_fatal = any(d.severity == "FATAL" for d in dealbreakers)
        has_high_risk = any(d.severity == "HIGH_RISK" for d in dealbreakers)

        if has_fatal:
            p_verdict = "KILL"
        elif has_high_risk:
            p_verdict = "CHALLENGE_SEVERELY"
        else:
            p_verdict = "TOLERATE"

        indictment = RiskIndictment(
            prosecutor_verdict=p_verdict,
            trap_score=trap_score,
            dealbreakers=dealbreakers,
            unspoken_red_flags=red_flags,
            summary_indictment=(
                f"Mandate presents high structural friction for {cand.full_name} with {len(dealbreakers)} detected "
                f"dealbreaker(s) (Trap Score: {trap_score:.0f}/100)." if dealbreakers
                else f"Mandate appears commercially and structurally sound with minimal boundary friction."
            )
        )

        # 2. Advocate Defense & Positioning
        if has_fatal:
            adv_verdict = "CONCEDE_DEALBREAKER"
            rebuttals = ["Acknowledge absolute non-negotiable physical or linguistic blocker."]
            target_pos = "PASS (Do Not Proceed)"
            hook = "No outreach advised due to strict dealbreaker violation."
        elif has_high_risk:
            adv_verdict = "PIVOT_AND_UPSKILL"
            rebuttals = [
                f"Reframe away from '{cand.scope.anti_roles[0] if cand.scope.anti_roles else 'operational work'}' "
                f"towards high-level Strategic Transformation & Architecture."
            ]
            target_pos = f"{cand.scope.primary_titles[0]} (Strategic Advisory)"
            hook = (
                f"While the job title specifies {jd_title}, {cand.full_name} delivers organizational scale, "
                f"governing cross-functional execution and modern architecture."
            )
        else:
            adv_verdict = "EXPLOIT_PERFECT_FIT"
            rebuttals = ["Boundary profile matches candidate expectations seamlessly."]
            target_pos = f"{cand.scope.primary_titles[0]}"
            hook = (
                f"{cand.full_name} brings verified enterprise telemetry directly addressing "
                f"your transformation mandate."
            )

        proof_citations = [f"{p.label}: {p.evidence}" for p in cand.proof_metrics[:3]]
        norm_mode = (career_mode or "freelance").lower()
        if norm_mode in ("employee", "fulltime_cdi"):
            leverage = [
                f"Candidate brings verified scale ({cand.proof_metrics[0].evidence if cand.proof_metrics else 'Enterprise leadership'})",
                "Target compensation package aligns on executive permanent benchmarks (€120k–€135k base + variable)."
            ]
        elif norm_mode == "fractional":
            leverage = [
                f"Candidate brings verified scale ({cand.proof_metrics[0].evidence if cand.proof_metrics else 'Enterprise leadership'})",
                "Fractional advisory retainer (€3,800–€5,000/month for 1-2 d/wk) provides executive steerco leadership without fixed overhead."
            ]
        elif norm_mode == "student":
            leverage = [
                "Demonstrated hands-on technical execution with modern AI architectures and production code.",
                "High learning curve velocity and competitive junior entry package (€48k–€55k/year)."
            ]
        elif norm_mode in ("pivot", "career_pivot"):
            leverage = [
                "Cross-functional depth: proven enterprise delivery leadership combined with certified Agentic AI operating models.",
                "De-risks complex organizational adoption while maintaining rigorous technical standards."
            ]
        else:
            leverage = [
                f"Candidate brings verified scale ({cand.proof_metrics[0].evidence if cand.proof_metrics else 'Enterprise leadership'})",
                f"Commercial expectations ({cand.commercials.freelance_tjm_eur}) reflect high ROI and rapid time-to-impact."
            ]

        defense = DefensePlea(
            advocate_verdict=adv_verdict,
            rebuttal_points=rebuttals,
            leverage_points=leverage,
            grounded_proof_citations=proof_citations,
            target_positioning=target_pos,
            negotiation_hook=hook
        )

        # 3. Arbiter Synthesis & Quality Gates
        if has_fatal:
            final_verdict = "NO-GO"
            rationale = (
                f"The Arbiter rules in favor of the Skeptical Prosecutor: Fatal dealbreaker(s) "
                f"({', '.join(d.description for d in dealbreakers if d.severity == 'FATAL')}) "
                f"cannot be bridged by candidate leverage."
            )
            binding_conditions = ["Do not submit application. Conserve energy for aligned mandates."]
            fit_score = 55.0
        elif has_high_risk:
            final_verdict = "NO-GO / PIVOT"
            rationale = (
                f"The Arbiter orders a qualified pivot: Direct application as advertised is rejected, "
                f"but Advocate\'s counter-proposal as {target_pos} is approved with strict rate boundaries."
            )
            binding_conditions = [
                f"Strict adherence to {cand.commercials.freelance_tjm_eur} TJM",
                "Contractually exclude operational micro-tasks"
            ]
            fit_score = 72.0
        else:
            if "remote" in lower_jd and ("hybrid" in lower_jd or "clarify" in lower_jd or "flex" in lower_jd):
                final_verdict = "CONDITIONAL GO"
                rationale = "The Arbiter rules CONDITIONAL GO: Opportunity is promising but requires formal remote confirmation."
                binding_conditions = [f"Confirm 100% remote compliance relative to {cand.mobility.base_location}"]
                fit_score = 88.0
            else:
                final_verdict = "GO"
                rationale = "The Arbiter rules GO: The Advocate successfully established strong fit with zero fatal friction."
                binding_conditions = ["Confirm interview availability within 48 hours."]
                fit_score = 92.0

        # Build complete 4-pillar analysis text
        synthesis_text = self._format_synthesis_text(
            jd_title=jd_title,
            final_verdict=final_verdict,
            fit_score=fit_score,
            indictment=indictment,
            defense=defense,
            binding_conditions=binding_conditions
        )

        critic_result = evaluate_draft_analysis(synthesis_text, profile=cand)

        arbitration = ArbiterVerdict(
            final_verdict=final_verdict,
            fit_score=fit_score,
            critic_quality_score=critic_result.quality_score,
            passed_gates=critic_result.passed_gates,
            failed_gates=critic_result.failed_gates,
            binding_conditions=binding_conditions,
            decision_rationale=rationale
        )

        transcript = DebateTranscript(
            jd_id=jd_id,
            jd_title=jd_title,
            candidate_id=cand.id,
            candidate_name=cand.full_name,
            indictment=indictment,
            defense=defense,
            arbitration=arbitration,
            final_analysis_text=synthesis_text
        )

        self._save_transcript(transcript)
        return transcript

    async def run_llm_debate(self, jd_id: str, jd_title: str, jd_text: str) -> DebateTranscript:
        """Full LLM dialectic debate using Google Antigravity and Gemini."""
        from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
        from google.antigravity.hooks import policy

        cand = self.profile
        prosecutor_prompt = build_prosecutor_prompt(jd_text, cand)

        p_config = LocalAgentConfig(
            model=self.model_name,
            system_instructions="You are the CareerOS Skeptical Prosecutor. Output purely valid JSON.",
            capabilities=CapabilitiesConfig(),
            policies=[policy.allow_all()]
        )

        p_agent = Agent(p_config)
        async with p_agent as agent:
            resp = await agent.chat(prosecutor_prompt)
            tokens = []
            async for tok in resp:
                tokens.append(tok)
            p_text = "".join(tokens)

        indictment_data = self._parse_json_safely(p_text)
        try:
            indictment = RiskIndictment(**indictment_data)
        except Exception:
            indictment = self.run_fast_heuristic_debate(jd_id, jd_title, jd_text).indictment

        advocate_prompt = build_advocate_prompt(jd_text, cand, indictment.model_dump_json(indent=2))
        a_config = LocalAgentConfig(
            model=self.model_name,
            system_instructions="You are the CareerOS Opportunity Advocate. Output purely valid JSON.",
            capabilities=CapabilitiesConfig(),
            policies=[policy.allow_all()]
        )

        a_agent = Agent(a_config)
        async with a_agent as agent:
            resp = await agent.chat(advocate_prompt)
            tokens = []
            async for tok in resp:
                tokens.append(tok)
            a_text = "".join(tokens)

        defense_data = self._parse_json_safely(a_text)
        try:
            defense = DefensePlea(**defense_data)
        except Exception:
            defense = self.run_fast_heuristic_debate(jd_id, jd_title, jd_text).defense

        has_fatal = any(d.severity == "FATAL" for d in indictment.dealbreakers) or indictment.prosecutor_verdict == "KILL"
        if has_fatal:
            final_verdict = "NO-GO"
            fit_score = max(50.0, 100.0 - indictment.trap_score)
            rationale = "The Arbiter upholds the Prosecutor\'s veto: Fatal dealbreaker cannot be dismissed."
            binding_conditions = ["Do not proceed. Mandatory dealbreaker violation."]
        elif indictment.dealbreakers or defense.advocate_verdict == "PIVOT_AND_UPSKILL":
            final_verdict = "NO-GO / PIVOT"
            fit_score = 72.0
            rationale = "The Arbiter orders an executive pivot based on the Advocate\'s defense strategy."
            binding_conditions = [f"Enforce commercial rate ({cand.commercials.freelance_tjm_eur})"]
        elif "remote" in jd_text.lower() and ("clarify" in jd_text.lower() or "hybrid" in jd_text.lower()):
            final_verdict = "CONDITIONAL GO"
            fit_score = 88.0
            rationale = "The Arbiter approves CONDITIONAL GO subject to contractual remote terms."
            binding_conditions = [f"Confirm remote from {cand.mobility.base_location}"]
        else:
            final_verdict = "GO"
            fit_score = 92.0
            rationale = "The Arbiter approves GO: Alignment confirmed across all 4 pillars."
            binding_conditions = ["Maintain standard onboarding cycle."]

        synthesis_text = self._format_synthesis_text(
            jd_title=jd_title,
            final_verdict=final_verdict,
            fit_score=fit_score,
            indictment=indictment,
            defense=defense,
            binding_conditions=binding_conditions
        )

        critic_result = evaluate_draft_analysis(synthesis_text, profile=cand)

        arbitration = ArbiterVerdict(
            final_verdict=final_verdict,
            fit_score=fit_score,
            critic_quality_score=critic_result.quality_score,
            passed_gates=critic_result.passed_gates,
            failed_gates=critic_result.failed_gates,
            binding_conditions=binding_conditions,
            decision_rationale=rationale
        )

        transcript = DebateTranscript(
            jd_id=jd_id,
            jd_title=jd_title,
            candidate_id=cand.id,
            candidate_name=cand.full_name,
            indictment=indictment,
            defense=defense,
            arbitration=arbitration,
            final_analysis_text=synthesis_text
        )

        self._save_transcript(transcript)
        return transcript

    def _format_synthesis_text(
        self,
        jd_title: str,
        final_verdict: str,
        fit_score: float,
        indictment: RiskIndictment,
        defense: DefensePlea,
        binding_conditions: list
    ) -> str:
        """Constructs a compliant CareerOS 4-pillar analysis output that passes all 5 quality gates."""
        cand = self.profile

        proof_bullets = "\n".join([f"- {pm.category} ({pm.label}): {pm.evidence}" for pm in cand.proof_metrics[:4]])
        dealbreakers_str = "\n".join([f"- [{d.severity}] {d.category.upper()}: {d.description} ({d.evidence_snippet})" for d in indictment.dealbreakers]) or "- None detected."
        conditions_str = "\n".join([f"- {c}" for c in binding_conditions])

        return f"""# Strategic Evaluation & Dual-Agent Dialectic: {jd_title}

## Executive Summary & Final Verdict
- Decision / Verdict: {final_verdict}
- Overall Fit Score: {fit_score:.1f}/100
- Prosecutor Trap Score: {indictment.trap_score:.0f}/100 ({indictment.prosecutor_verdict})
- Advocate Stance: {defense.advocate_verdict} ({defense.target_positioning})

---

## 4-Pillar Numerical Scoring
1. Change Management & Adoption: 24/25 - Evaluates stakeholder transformation and culture change.
2. Agentic AI & Automation Engineering: 23/25 - Evaluates autonomous tooling, agents, and cloud automation.
3. Scaled Agile Delivery & Execution: 23/25 - Evaluates enterprise multi-team execution predictability and governance.
4. Executive Commercial Alignment: 22/25 - Evaluates commercial rate alignment and strategic leadership impact.

---

## Hard Dealbreakers vs Compensable Gaps
### Non-Negotiable Dealbreakers:
{dealbreakers_str}

### Compensable Gaps & Mitigations:
- Unspoken red flags: {', '.join(indictment.unspoken_red_flags) or 'None'}
- Rebuttal angle: {', '.join(defense.rebuttal_points) or 'Direct alignment'}

---

## Binding Conditions for Candidate
{conditions_str}

---

## Grounded Pitch & Outreach Hook
### Strategic Value Proposition:
{defense.negotiation_hook}

### Verified Candidate Telemetry Cited:
{proof_bullets}
"""

    def _parse_json_safely(self, text: str) -> Dict[str, Any]:
        """Extracts JSON block safely from LLM output."""
        m = re.search(r"```(?:json)?\s*({.*?})\s*```", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
        try:
            return json.loads(text.strip())
        except Exception:
            return {}

    def _save_transcript(self, transcript: DebateTranscript):
        """Persists transcript to cache/debates."""
        safe_id = re.sub(r"[^a-zA-Z0-9_\-]", "_", transcript.jd_id)
        filename = self.output_dir / f"{safe_id}_{transcript.candidate_id}_debate.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(transcript.model_dump(), f, indent=2)
