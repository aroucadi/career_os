"""
CareerOS Dual-Agent Debate Data Models
=======================================
Pydantic schemas defining the dialectic exchange between:
1. The Skeptical Prosecutor (Deal Killer & Risk Screener)
2. The Opportunity Advocate (Talent Strategist & Negotiator)
3. The Arbiter (Quality Gate Harness & Strategic Synthesis)
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DealbreakerItem(BaseModel):
    category: str = Field(description="commute, language, anti_role, budget, or other")
    severity: str = Field(description="FATAL (strict NO-GO) or HIGH_RISK (CONDITIONAL)")
    description: str = Field(description="Detailed reason for objection")
    evidence_snippet: str = Field(default="", description="Extracted text snippet from JD")

    @property
    def dealbreaker_name(self) -> str:
        return self.description

class RiskIndictment(BaseModel):
    """Structured objection bill drafted by the Skeptical Prosecutor."""
    prosecutor_verdict: str = Field(description="KILL, CHALLENGE_SEVERELY, or TOLERATE")
    trap_score: float = Field(ge=0.0, le=100.0, description="0 to 100 toxicity/trap rating")
    dealbreakers: List[DealbreakerItem] = Field(default_factory=list)
    unspoken_red_flags: List[str] = Field(default_factory=list, description="Hidden burdens (on-call, micromanagement, legacy debt)")
    summary_indictment: str = Field(description="Executive indictment paragraph")

class DefensePlea(BaseModel):
    """Strategic defense and pivot proposal drafted by the Opportunity Advocate."""
    advocate_verdict: str = Field(description="EXPLOIT_PERFECT_FIT, PIVOT_AND_UPSKILL, or CONCEDE_DEALBREAKER")
    rebuttal_points: List[str] = Field(default_factory=list, description="How candidate telemetry neutralizes or pivots around objections")
    leverage_points: List[str] = Field(default_factory=list, description="Why the client is in desperate need of this candidate profile")
    grounded_proof_citations: List[str] = Field(default_factory=list, description="Citations from candidate profile proof_metrics")
    target_positioning: str = Field(description="Exact title and value proposition to put forward")
    negotiation_hook: str = Field(description="Tactical opening hook for recruiter or hiring manager")

class ArbiterVerdict(BaseModel):
    """Definitive arbitration rendered by the deterministic Quality Gate Harness."""
    final_verdict: str = Field(description="GO, CONDITIONAL GO, or NO-GO / PIVOT")
    fit_score: float = Field(ge=0.0, le=100.0)
    critic_quality_score: float = Field(ge=0.0, le=100.0)
    passed_gates: List[str] = Field(default_factory=list)
    failed_gates: List[str] = Field(default_factory=list)
    binding_conditions: List[str] = Field(default_factory=list, description="Non-negotiable terms candidate must enforce before signing")
    decision_rationale: str = Field(description="Why the arbiter ruled in favor of prosecutor, advocate, or a qualified compromise")

class DebateTranscript(BaseModel):
    """Full audit transcript of the dual-agent debate."""
    jd_id: str
    jd_title: str
    candidate_id: str
    candidate_name: str
    indictment: RiskIndictment
    defense: DefensePlea
    arbitration: ArbiterVerdict
    final_analysis_text: str = Field(description="Synthesized 4-pillar analysis matching standard CareerOS format")
