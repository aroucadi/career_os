"""
CareerOS Anonymized Talent Graph Models
=======================================
GDPR-compliant anonymized candidate representation for B2B recruiter matching.
Strips all candidate PII (names, emails, phone numbers, exact addresses) while
preserving hard proof metrics, governance tags, compensation floors, and readiness.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class ReadinessStatus(str, Enum):
    ACTIVE_VERIFIED = "ACTIVE_VERIFIED"  # Profile parsed, verified proof metrics, actively evaluating
    DORMANT = "DORMANT"                  # High-skill candidate open only to exceptional inbound
    UPSKILLING = "UPSKILLING"            # Candidate actively closing skill gaps

class TalentProofMetric(BaseModel):
    label: str
    evidence: str
    category: str = "Delivery & Architecture"

class TalentGraphProfile(BaseModel):
    profile_id: str = Field(description="Opaque hashed identifier, e.g. 'cand_7402f1'")
    anonymized_alias: str = Field(description="e.g. 'Candidate #7402 — Lead AI Architect'")
    headline: str
    seniority: str = "Senior / Executive"
    target_roles: List[str] = Field(default_factory=list)
    core_competencies: List[str] = Field(default_factory=list)
    governance_tags: List[str] = Field(default_factory=list)
    readiness_status: ReadinessStatus = ReadinessStatus.ACTIVE_VERIFIED
    verified_proof_metrics: List[TalentProofMetric] = Field(default_factory=list)
    target_compensation: Dict[str, Any] = Field(default_factory=dict)
    mobility: Dict[str, Any] = Field(default_factory=dict)
    consent_broadcast_enabled: bool = True
    verified_composite_score: float = 85.0
    last_evaluated_jd: Optional[str] = None
    indexed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def from_candidate_profile(cls, cand, verified_score: float = 88.0, last_jd: Optional[str] = None) -> "TalentGraphProfile":
        """Converts a rich CandidateProfile into an anonymized TalentGraphProfile."""
        import hashlib
        h = hashlib.sha256(cand.id.encode()).hexdigest()[:6]
        alias = f"Candidate #{h.upper()[:4]} — {cand.primary_title if hasattr(cand, 'primary_title') else cand.headline.split('|')[0].strip()}"
        
        # Extract governance tags
        gov_tags = []
        proof_items = []
        full_text = " ".join([m.evidence for m in getattr(cand, "proof_metrics", [])] + [cand.headline])
        lower_text = full_text.lower()
        if "eu ai act" in lower_text or "responsible ai" in lower_text:
            gov_tags.append("EU AI Act & Responsible AI")
        if "sox" in lower_text or "audit" in lower_text:
            gov_tags.append("SOX 404 / Risk Automation")
        if "hitl" in lower_text or "governance" in lower_text:
            gov_tags.append("HITL Governance")
        if "core banking" in lower_text or "fintech" in lower_text:
            gov_tags.append("Regulated Fintech & Banking")
        if not gov_tags:
            gov_tags.append("Enterprise Architecture")

        for m in getattr(cand, "proof_metrics", []):
            proof_items.append(TalentProofMetric(
                label=m.label,
                evidence=m.evidence,
                category=getattr(m, "category", "Scale & Execution")
            ))

        # Dynamically extract competencies from candidate profile
        extracted_competencies = []
        if hasattr(cand, "scope") and getattr(cand.scope, "core_domains", None):
            extracted_competencies.extend(cand.scope.core_domains)
        for m in getattr(cand, "proof_metrics", []):
            if getattr(m, "label", None) and m.label not in extracted_competencies:
                extracted_competencies.append(m.label)
        if not extracted_competencies:
            extracted_competencies = ["Enterprise Architecture", "AI Delivery", "Operating Model"]

        return cls(
            profile_id=f"cand_{h}",
            anonymized_alias=alias,
            headline=cand.headline,
            seniority=getattr(cand.scope, "seniority", "Executive / Lead"),
            target_roles=getattr(cand.scope, "primary_titles", []),
            core_competencies=extracted_competencies,
            governance_tags=gov_tags,
            readiness_status=ReadinessStatus.ACTIVE_VERIFIED,
            verified_proof_metrics=proof_items,
            target_compensation={
                "freelance_tjm": getattr(cand.commercials, "freelance_tjm_eur", "950€"),
                "permanent_salary": getattr(cand.commercials, "permanent_salary_eur", "125k€"),
                "currency": getattr(cand.commercials, "currency", "EUR")
            },
            mobility={
                "base_location": getattr(cand.mobility, "base_location", "Remote EU"),
                "remote_preference": getattr(cand.mobility, "remote_preference", "100% Remote")
            },
            consent_broadcast_enabled=True,
            verified_composite_score=verified_score,
            last_evaluated_jd=last_jd
        )
