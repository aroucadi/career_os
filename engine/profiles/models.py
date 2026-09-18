"""
CareerOS Generic Candidate Profile Models
=========================================
Agnostic schema defining candidate identity, constraints, commercial targets,
scope boundaries, and verified proof metrics.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class MobilityPolicy(BaseModel):
    """Candidate's geographical and working arrangement constraints."""
    base_location: str = Field(description="Home city/country (e.g. 'Nice, France' or 'London, UK')")
    remote_preference: str = Field(
        default="100% Remote",
        description="Remote policy (e.g. '100% Remote', 'Hybrid 1-2 days', 'On-site')"
    )
    travel_tolerance: str = Field(
        default="Quarterly client milestones, PI planning, key kickoffs",
        description="Travel willingness"
    )
    unacceptable_commutes: List[str] = Field(
        default_factory=list,
        description="Cities or formats that represent hard dealbreakers for regular weekly commute"
    )


class LanguageProficiency(BaseModel):
    """Spoken languages and linguistic constraints."""
    fluent_languages: List[str] = Field(
        description="Languages spoken at professional/native level (e.g. ['English C1+', 'French Native'])"
    )
    blocker_languages: List[str] = Field(
        default_factory=list,
        description="Languages the candidate does NOT speak; any mandatory requirement is a hard blocker"
    )


class CommercialExpectations(BaseModel):
    """Freelance daily rates and permanent salary targets."""
    freelance_tjm_eur: str = Field(default="800 - 1,000 EUR / day", description="Target daily rate in EUR")
    permanent_salary_eur: str = Field(default="110k - 130k EUR", description="Target base permanent package")
    currency: str = Field(default="EUR", description="Primary currency")


class TargetRoleScope(BaseModel):
    """Seniority, targeted umbrella titles, and non-negotiable anti-roles."""
    primary_titles: List[str] = Field(
        description="Target role titles (e.g. ['AI Delivery Lead', 'AI Operating Model Architect'])"
    )
    seniority: str = Field(default="Senior / Executive / Lead", description="Target career tier")
    anti_roles: List[str] = Field(
        default_factory=list,
        description="Roles or task types candidate explicitly refuses to take (e.g. ['IC junior developer'])"
    )
    core_domains: List[str] = Field(
        default_factory=list,
        description="Core industry or functional domains (e.g. ['Fintech', 'Banking', 'SaaS'])"
    )


class KeyProofMetric(BaseModel):
    """Concrete, verified telemetry points extracted from the candidate's CV."""
    category: str = Field(description="e.g. 'Scale', 'Innovation', 'Governance', 'Architecture'")
    label: str = Field(description="Short identifier, e.g. 'Headcount Scale'")
    evidence: str = Field(description="Exact grounded citation, e.g. '7 squads, ~50 engineers across 3 tribes'")
    keywords: List[str] = Field(
        default_factory=list,
        description="Search tokens for critic verification, e.g. ['7 squad', '50 engineer']"
    )


class CandidateProfile(BaseModel):
    """Master candidate profile representation."""
    id: str = Field(description="Unique profile slug, e.g. 'alaa_roucadi'")
    full_name: str = Field(description="Full legal name")
    headline: str = Field(description="Professional executive headline")
    resume_file: str = Field(description="Path relative to workspace root of active master CV")
    contact_email: Optional[str] = None
    linkedin_url: Optional[str] = None
    
    mobility: MobilityPolicy
    languages: LanguageProficiency
    commercials: CommercialExpectations
    scope: TargetRoleScope
    proof_metrics: List[KeyProofMetric] = Field(default_factory=list)

    def to_prompt_constraints(self) -> str:
        """Serializes candidate constraints dynamically for the context-engineered prompt."""
        unacc = f" Permanent multi-day weekly commutes ({', '.join(self.mobility.unacceptable_commutes)}) are non-negotiable DEALBREAKERS." if self.mobility.unacceptable_commutes else ""
        block_langs = f" Candidate does NOT speak {', '.join(self.languages.blocker_languages)}. Any role requiring daily communication in these languages is a strict HARD BLOCKER." if self.languages.blocker_languages else ""
        anti = f" Candidate is NOT an {', '.join(self.scope.anti_roles)}." if self.scope.anti_roles else ""

        return (
            f"- Location Base: {self.mobility.base_location}.\n"
            f"- Mobility and Remote Policy: {self.mobility.remote_preference}. Open to: {self.mobility.travel_tolerance}.{unacc}\n"
            f"- Languages: {', '.join(self.languages.fluent_languages)}.{block_langs}\n"
            f"- Seniority and Scope: {self.headline} ({self.scope.seniority}). Target titles: {', '.join(self.scope.primary_titles)}.{anti}\n"
            f"- Commercial Expectations: Target Freelance: {self.commercials.freelance_tjm_eur}; Permanent Target: {self.commercials.permanent_salary_eur}.\n"
        )
