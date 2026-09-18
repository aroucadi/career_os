"""
CareerOS Episodic Memory Data Models
====================================
Pydantic schemas capturing real-world market feedback, employer interactions,
negotiation outcomes, and structural market learnings.
"""

from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class FeedbackOutcome(str, Enum):
    POSITIVE_RESPONSE = "POSITIVE_RESPONSE"          # Recruiter replied with interest
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"      # Screening or hiring manager interview booked
    INTERVIEW_PASSED = "INTERVIEW_PASSED"            # Advanced to next round
    OFFER_RECEIVED = "OFFER_RECEIVED"                # Commercial contract offered
    OFFER_ACCEPTED = "OFFER_ACCEPTED"                # Mission signed
    RATE_REJECTED = "RATE_REJECTED"                  # Budget mismatch / client capped rate below TJM
    LOCATION_REJECTED = "LOCATION_REJECTED"          # Unadvertised hybrid / on-site obligation
    SCOPE_MISMATCH = "SCOPE_MISMATCH"                # Seeking junior builder or micromanaged profile
    GHOSTED = "GHOSTED"                              # No answer after application / pitch
    CLIENT_CANCELLED = "CLIENT_CANCELLED"            # Mandate pulled internally by client


class ObjectionCategory(str, Enum):
    RATE_BUDGET = "rate_budget"
    REMOTE_POLICY = "remote_policy"
    SENIORITY_FIT = "seniority_fit"
    TECHNICAL_STACK = "technical_stack"
    COMMUNICATION_LANGUAGE = "communication_language"
    TIMING = "timing"
    OTHER = "other"


class EpisodicRecord(BaseModel):
    """A structured memory unit recording an actual interaction or outcome."""
    id: str = Field(description="Unique record identifier (e.g. MEM_JD_30_01)")
    opportunity_id: str = Field(description="Associated opportunity (e.g. JD_30)")
    company: str = Field(description="Company or end client name")
    agency: Optional[str] = Field(default=None, description="Staffing or recruitment agency name")
    role_title: str = Field(description="Job title evaluated")
    domain: str = Field(default="AI & Delivery", description="Primary domain tag")
    candidate_profile_id: str = Field(default="alaa_roucadi", description="Profile used")
    outcome: FeedbackOutcome
    objection_category: Optional[ObjectionCategory] = None
    actual_rate_offered_eur: Optional[float] = Field(default=None, description="Exact rate disclosed by client/recruiter")
    notes: str = Field(default="", description="Human notes or recruiter feedback snippet")
    key_takeaways: List[str] = Field(default_factory=list, description="Distilled actionable rules for future evaluations")
    successful_angles: List[str] = Field(default_factory=list, description="Arguments or proofs that resonated strongly")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class CompanyTrackRecord(BaseModel):
    """Aggregated memory profile for a specific company or agency."""
    company_name: str
    total_interactions: int = 0
    outcomes_count: Dict[str, int] = Field(default_factory=dict)
    average_rate_eur: Optional[float] = None
    known_objections: List[str] = Field(default_factory=list)
    strategic_rules: List[str] = Field(default_factory=list)
