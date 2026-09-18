"""
CareerOS Recruiter Delegation Domain Models
===========================================
Defines the data contracts for B2B recruiter requisition decomposition,
candidate match slate ranking, the Double Opt-In state machine,
and the paid Executive Dossier.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class OptInStatus(str, Enum):
    PENDING_CONSENT = "PENDING_CONSENT"  # Recruiter requested intro; awaiting candidate consent
    APPROVED = "APPROVED"                # Candidate consented; Executive Dossier & PII unlocked
    DECLINED = "DECLINED"                # Candidate declined; dossier remains permanently locked
    EXPIRED = "EXPIRED"                  # Request timed out (7 days)

class RequisitionSpec(BaseModel):
    """Structured representation of an incoming recruiter job mandate."""
    req_id: str = Field(description="Unique requisition identifier, e.g. 'req_a721b'")
    job_title: str
    company: str
    jd_raw_text: str
    mandatory_eliminators: List[str] = Field(default_factory=list, description="Hard disqualifiers (e.g. 'EU Citizenship', 'Min 5 yrs', 'Onsite')")
    preferred_multipliers: List[str] = Field(default_factory=list, description="Value boosters (e.g. 'EU AI Act', 'Banking CoE Scale', 'Agentic SDLC')")
    budget_range: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CandidateMatchSlateItem(BaseModel):
    """An individual candidate scored and ranked against a recruiter requisition."""
    match_id: str = Field(description="Unique match transaction ID, e.g. 'match_38219'")
    candidate_id: str = Field(description="Opaque hashed profile ID (e.g. 'cand_6f234c')")
    anonymized_alias: str = Field(description="Opaque title, e.g. 'Candidate #6F23 — Senior AI Product & Delivery Manager'")
    headline: str
    seniority: str
    overall_match_score: float = Field(ge=0.0, le=100.0, description="Composite weighted match score (0-100)")
    rubric_subscores: Dict[str, float] = Field(default_factory=dict, description="Domain, Governance, Scale, and Compensation subscores")
    key_leverage_points: List[str] = Field(default_factory=list, description="Verified proofs directly matching the requisition")
    pre_identified_gaps: List[str] = Field(default_factory=list, description="Minor areas candidate has already mitigated")
    governance_tags: List[str] = Field(default_factory=list)
    target_compensation: Dict[str, Any] = Field(default_factory=dict)
    opt_in_status: OptInStatus = OptInStatus.PENDING_CONSENT
    requested_at: Optional[str] = None
    unlocked_at: Optional[str] = None

class ExecutiveDossier(BaseModel):
    """
    The high-value audit certainty package recruiters pay for.
    Contact information and full identity are ONLY revealed when access_status is UNLOCKED.
    """
    dossier_id: str
    match_id: str
    candidate_id: str
    anonymized_alias: str
    access_status: str = Field(default="LOCKED", description="'LOCKED' (pre-consent) or 'UNLOCKED' (consented)")
    
    # PII Fields (Gated behind Double Opt-In consent)
    unlocked_full_name: Optional[str] = None
    unlocked_email: Optional[str] = None
    unlocked_phone: Optional[str] = None
    unlocked_linkedin: Optional[str] = None
    
    # Audit Certainty Data (Always available or unlocked upon match)
    verified_telemetry: List[Dict[str, str]] = Field(default_factory=list)
    gap_mitigations: List[Dict[str, str]] = Field(default_factory=list)
    custom_interview_cheatsheet: List[str] = Field(default_factory=list, description="5 tactical questions tailored specifically to this candidate vs JD")
    pre_negotiated_compensation: Dict[str, Any] = Field(default_factory=dict)
    audit_verdict: str = "RECOMMENDED_FOR_IMMEDIATE_INTERVIEW"
    compiled_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
