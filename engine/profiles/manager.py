"""
CareerOS Profile Manager
========================
Loads, saves, and resolves candidate profiles from the profiles/ directory.
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict

from .models import CandidateProfile

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
_PROFILES_DIR = _ROOT_DIR / "profiles"


class ProfileManager:
    """Manages multi-candidate profile resolution and persistence."""

    @classmethod
    def get_profiles_dir(cls) -> Path:
        _PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        return _PROFILES_DIR

    @classmethod
    def list_available_profiles(cls) -> List[str]:
        pdir = cls.get_profiles_dir()
        return [f.stem for f in pdir.glob("*.json")]

    @classmethod
    def load_profile(cls, identifier: Optional[str] = None) -> CandidateProfile:
        """Resolves and loads a CandidateProfile by slug, filename, or default fallback."""
        pdir = cls.get_profiles_dir()

        # 1. Explicit identifier provided
        if identifier:
            cand_p = Path(identifier)
            if cand_p.exists() and cand_p.is_file():
                return cls._load_file(cand_p)

            clean = identifier.replace(".json", "")
            matches = list(pdir.glob(f"{clean}.json"))
            if matches:
                return cls._load_file(matches[0])

        # 2. Check active_profile.json
        active_p = pdir / "active_profile.json"
        if active_p.exists():
            return cls._load_file(active_p)

        # 3. Check default.json
        default_p = pdir / "default.json"
        if default_p.exists():
            return cls._load_file(default_p)

        # 4. Check alaa_roucadi.json
        alaa_p = pdir / "alaa_roucadi.json"
        if alaa_p.exists():
            return cls._load_file(alaa_p)

        # 5. Fallback: Generate and save default
        fallback = cls.create_default_alaa_profile()
        cls.save_profile(fallback, filename="default.json")
        cls.save_profile(fallback, filename="alaa_roucadi.json")
        return fallback

    @classmethod
    def _load_file(cls, path: Path) -> CandidateProfile:
        data = json.loads(path.read_text(encoding="utf-8"))
        return CandidateProfile.model_validate(data)

    @classmethod
    def save_profile(cls, profile: CandidateProfile, filename: Optional[str] = None):
        pdir = cls.get_profiles_dir()
        fname = filename or f"{profile.id}.json"
        target = pdir / fname
        target.write_text(profile.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def create_default_alaa_profile(cls) -> CandidateProfile:
        """Constructs the canonical profile for Alaa Eddine Roucadi."""
        from .models import (
            MobilityPolicy,
            LanguageProficiency,
            CommercialExpectations,
            TargetRoleScope,
            KeyProofMetric
        )
        return CandidateProfile(
            id="alaa_roucadi",
            full_name="Alaa Eddine Roucadi",
            headline="Senior AI Product & Delivery Manager / AI Operating Model Architect",
            resume_file="Alaa_Eddine_Roucadi_Resume_v12.md",
            contact_email="alaaeddineroucadi@gmail.com",
            linkedin_url="https://www.linkedin.com/in/alaaeddineroucadi/",
            mobility=MobilityPolicy(
                base_location="Nice, France",
                remote_preference="100% Remote across Europe/EMEA",
                travel_tolerance="Periodic travel for quarterly kickoffs, PI planning, and key client milestones",
                unacceptable_commutes=["Vienna", "Munich", "Frankfurt", "Zurich", "multi-day weekly on-site commutes"]
            ),
            languages=LanguageProficiency(
                fluent_languages=["English (Fluent / C1+ professional working proficiency)", "French (Bilingual / Native)", "Arabic (Native)"],
                blocker_languages=["German", "Dutch", "Scandinavian languages", "Italian"]
            ),
            commercials=CommercialExpectations(
                freelance_tjm_eur="800 - 1,000 EUR / day",
                permanent_salary_eur="110k - 130k EUR base + bonus",
                currency="EUR"
            ),
            scope=TargetRoleScope(
                primary_titles=[
                    "AI Delivery Lead & Operating Model Architect",
                    "Senior AI Product & Delivery Manager",
                    "AI Center of Excellence Lead",
                    "Head of AI Platform Delivery"
                ],
                seniority="Senior / Lead / Executive Director tier (10+ YOE)",
                anti_roles=["individual contributor (IC) junior or mid Python developer"],
                core_domains=["Tier-1 Banking", "Corporate Finance / Factoring", "Large Scale Agile", "SaaS Marketplaces"]
            ),
            proof_metrics=[
                KeyProofMetric(
                    category="Scale",
                    label="Banking CoE Scale",
                    evidence="Governed 3 banking tribes and 7 squads (~50 engineers/POs) across 3 AI product streams.",
                    keywords=["7 squad", "50 engineer", "3 tribe"]
                ),
                KeyProofMetric(
                    category="Innovation",
                    label="Agentic SDLC & Tooling",
                    evidence="Shipped Atlassian Rovo AI Agents and Claude Code with Spec-Driven Development (SDD) guardrails.",
                    keywords=["rovo", "claude code", "spec-driven", "sdd"]
                ),
                KeyProofMetric(
                    category="Tooling IP",
                    label="Alignify Custom Jira App",
                    evidence="Created Alignify, a custom internal Jira portfolio dependency application for cross-tribe delivery.",
                    keywords=["alignify"]
                ),
                KeyProofMetric(
                    category="Governance",
                    label="EU AI Act Risk Gates",
                    evidence="Enforced hands-on EU AI Act risk classification and Responsible AI production release gates.",
                    keywords=["eu ai act", "responsible ai", "governance gate"]
                )
            ]
        )

    @classmethod
    def create_sophie_devops_profile(cls) -> CandidateProfile:
        """Constructs a secondary, generic candidate profile (DevOps / Cloud Architect)."""
        from .models import (
            MobilityPolicy,
            LanguageProficiency,
            CommercialExpectations,
            TargetRoleScope,
            KeyProofMetric
        )
        return CandidateProfile(
            id="sophie_cloud_architect",
            full_name="Sophie Laurent",
            headline="Staff Cloud & DevOps Platform Architect (AWS / Kubernetes)",
            resume_file="resumes/Sophie_DevOps_Resume.md",
            contact_email="sophie.laurent.cloud@gmail.com",
            linkedin_url="https://www.linkedin.com/in/sophielaurent-cloud/",
            mobility=MobilityPolicy(
                base_location="Lyon, France",
                remote_preference="Full Remote or Hybrid Lyon/Paris",
                travel_tolerance="Occasional travel to Paris or Western Europe",
                unacceptable_commutes=["London on-site", "Berlin on-site", "non-Schengen on-site"]
            ),
            languages=LanguageProficiency(
                fluent_languages=["French (Native)", "English (Full Professional B2/C1)"],
                blocker_languages=["German", "Spanish", "Japanese"]
            ),
            commercials=CommercialExpectations(
                freelance_tjm_eur="650 - 800 EUR / day",
                permanent_salary_eur="85k - 100k EUR",
                currency="EUR"
            ),
            scope=TargetRoleScope(
                primary_titles=[
                    "Staff Cloud Architect",
                    "Lead DevOps Engineer",
                    "Platform Engineering Lead",
                    "SRE Director"
                ],
                seniority="Lead / Staff Engineer tier (8+ YOE)",
                anti_roles=["Agile Coach / Scrum Master", "Frontend Developer", "Manual QA"],
                core_domains=["Cloud Infrastructure", "E-Commerce", "SaaS Scaleups", "Fintech"]
            ),
            proof_metrics=[
                KeyProofMetric(
                    category="Scale",
                    label="Kubernetes Scale",
                    evidence="Managed 12 multi-region EKS clusters serving 20M daily requests with 99.99% uptime.",
                    keywords=["eks", "kubernetes", "12 cluster", "99.99%"]
                ),
                KeyProofMetric(
                    category="Cost & FinOps",
                    label="AWS Cloud Cost Optimization",
                    evidence="Reduced annualized AWS cloud expenditure by 38% ($450k/year) via Graviton and Karpenter autoscaling.",
                    keywords=["38%", "450k", "karpenter", "graviton", "finops"]
                ),
                KeyProofMetric(
                    category="CI/CD Velocity",
                    label="Deployment Flow Velocity",
                    evidence="Engineered GitOps ArgoCD pipeline decreasing mean time to release from 4 days to 25 minutes.",
                    keywords=["argocd", "gitops", "25 minute", "pipeline"]
                )
            ]
        )
