"""
Pipeline Data Models
====================
Pydantic models representing opportunity states, transitions,
snapshots, and multi-persona perspectives.
"""

from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class PipelineStage(str, Enum):
    DISCOVERED = "DISCOVERED"
    QUALIFIED = "QUALIFIED"
    PITCH_READY = "PITCH_READY"
    APPLIED = "APPLIED"
    SCREENING_SCHEDULED = "SCREENING_SCHEDULED"
    INTERVIEWING = "INTERVIEWING"
    OFFER_EXTENDED = "OFFER_EXTENDED"
    NEGOTIATING = "NEGOTIATING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class PersonaType(str, Enum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    CAREER_PIVOT = "career_pivot"


class EvaluationSnapshot(BaseModel):
    overall_score: float = 0.0
    scores: Dict[str, float] = Field(default_factory=dict)
    strategic_verdict: str = "PENDING"  # GO, CONDITIONAL GO, NO-GO
    ats_keyword_gaps: List[str] = Field(default_factory=list)
    competency_gaps: List[str] = Field(default_factory=list)
    dealbreaker_flags: List[str] = Field(default_factory=list)
    evaluated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class CandidatePerspective(BaseModel):
    pitch_hook: str = ""
    negotiation_leverage: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    target_rate_eur: str = "850-1000 EUR/day"
    counter_proposal_needed: bool = False
    strategic_advice: str = ""


class RecruiterPerspective(BaseModel):
    executive_summary_3bullets: List[str] = Field(default_factory=list)
    rate_feasibility: str = "Within budget"
    availability_status: str = "Immediate / 2-3 weeks"
    screening_checklist: List[str] = Field(default_factory=list)


class HiringManagerPerspective(BaseModel):
    top_5_interview_questions: List[str] = Field(default_factory=list)
    risk_scorecard: Dict[str, str] = Field(default_factory=dict)
    team_impact_assessment: str = ""


class CareerPivotPerspective(BaseModel):
    current_role_x: str = "Agile Delivery Manager / Technical PM"
    target_role_y: str = "AI Delivery Manager / AI CoE Lead"
    skill_delta_matrix: Dict[str, str] = Field(default_factory=dict)
    prioritized_upskilling_roadmap: List[str] = Field(default_factory=list)
    transferable_assets: List[str] = Field(default_factory=list)


class MultiPersonaIntel(BaseModel):
    candidate: CandidatePerspective = Field(default_factory=CandidatePerspective)
    recruiter: RecruiterPerspective = Field(default_factory=RecruiterPerspective)
    hiring_manager: HiringManagerPerspective = Field(default_factory=HiringManagerPerspective)
    career_pivot: CareerPivotPerspective = Field(default_factory=CareerPivotPerspective)


class HistoryEvent(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    from_stage: Optional[PipelineStage] = None
    to_stage: PipelineStage
    actor: str = "user"
    notes: str = ""
    follow_up_date: Optional[str] = None


class Opportunity(BaseModel):
    id: str  # e.g. "JD_30"
    jd_filename: str
    job_title: str
    company: str
    location: str = "Unknown"
    employment_type: str = "Contract"  # Contract, Permanent, Hybrid
    stage: PipelineStage = PipelineStage.DISCOVERED
    source: str = "radar"  # radar, email, direct, referral
    url: str = ""
    discovered_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    next_follow_up: Optional[str] = None
    evaluation: Optional[EvaluationSnapshot] = None
    persona_intel: MultiPersonaIntel = Field(default_factory=MultiPersonaIntel)
    history: List[HistoryEvent] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
