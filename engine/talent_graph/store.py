"""
CareerOS Talent Intelligence Lake Store
=======================================
Stores and indexes GDPR-compliant anonymized candidate profiles.
Provides query and retrieval interfaces for recruiter matching without exposing PII.
"""

import json
import logging
import threading
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from .models import TalentGraphProfile, ReadinessStatus

logger = logging.getLogger("careeros.talent_lake")

LAKE_STORAGE_PATH = Path(__file__).resolve().parent.parent.parent / "storage" / "talent_lake.json"
_lake_lock = threading.Lock()

class TalentLakeStore:
    """Persistent storage and indexing for the anonymized talent graph."""

    _profiles: Dict[str, TalentGraphProfile] = {}
    _loaded: bool = False

    @classmethod
    def _ensure_loaded(cls):
        with _lake_lock:
            if cls._loaded:
                return
            LAKE_STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
            if LAKE_STORAGE_PATH.exists():
                try:
                    with open(LAKE_STORAGE_PATH, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        cls._profiles = {k: TalentGraphProfile.model_validate(v) for k, v in data.items()}
                except Exception as e:
                    logger.error(f"Failed to load talent lake: {e}")
                    cls._profiles = {}
            cls._loaded = True

    @classmethod
    def _save(cls):
        try:
            LAKE_STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
            temp_file = LAKE_STORAGE_PATH.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump({k: v.model_dump() for k, v in cls._profiles.items()}, f, indent=2)
            shutil.move(str(temp_file), str(LAKE_STORAGE_PATH))
        except Exception as e:
            logger.error(f"Failed to persist talent lake: {e}")

    @classmethod
    def upsert_profile(cls, profile: TalentGraphProfile):
        cls._ensure_loaded()
        with _lake_lock:
            cls._profiles[profile.profile_id] = profile
            cls._save()
        logger.info(f"[TalentLake] Indexed candidate node: '{profile.anonymized_alias}' (ID: {profile.profile_id})")

    @classmethod
    def get_profile(cls, profile_id: str) -> Optional[TalentGraphProfile]:
        cls._ensure_loaded()
        with _lake_lock:
            return cls._profiles.get(profile_id)

    @classmethod
    def list_profiles(
        cls,
        status: Optional[ReadinessStatus] = None,
        governance_tag: Optional[str] = None
    ) -> List[TalentGraphProfile]:
        cls._ensure_loaded()
        profiles = list(cls._profiles.values())
        if status:
            profiles = [p for p in profiles if p.readiness_status == status]
        if governance_tag:
            profiles = [p for p in profiles if any(governance_tag.lower() in t.lower() for t in p.governance_tags)]
        return profiles

    @classmethod
    def index_candidate(cls, cand, verified_score: float = 88.0, last_jd: Optional[str] = None) -> TalentGraphProfile:
        """Helper to convert and index an active candidate profile."""
        profile = TalentGraphProfile.from_candidate_profile(cand, verified_score=verified_score, last_jd=last_jd)
        cls.upsert_profile(profile)
        return profile

    @classmethod
    def seed_default_talent_pool(cls):
        """Seeds the lake with multi-persona verified candidate profiles if lake is sparsely populated."""
        cls._ensure_loaded()
        with _lake_lock:
            from engine.profiles.manager import ProfileManager
            from engine.talent_graph.models import TalentProofMetric

            # 1. Alaa - Lead AI Architect
            cand_alaa = ProfileManager.load_profile("alaa_roucadi")
            p_alaa = TalentGraphProfile.from_candidate_profile(cand_alaa, verified_score=94.0)
            cls._profiles[p_alaa.profile_id] = p_alaa

            # 2. Sarah - Director of Audit & Risk
            p_sarah = TalentGraphProfile(
                profile_id="cand_sarah_audit",
                anonymized_alias="Candidate #4129 — Senior Manager & Director of Financial Audit / Tech Risk",
                headline="Senior Manager / Director of Internal Audit, Tech Risk & SOX Automation",
                seniority="Director / Senior Manager (12+ YOE)",
                target_roles=["Director of Internal Audit", "Head of Tech Compliance & Risk", "Chief Audit Executive"],
                core_competencies=["SOX 404", "ITGC Controls", "Internal Audit", "Risk Automation", "Fintech Compliance"],
                governance_tags=["SOX 404 / Risk Automation", "Regulated Fintech & Banking", "Audit Committee Reporting"],
                readiness_status=ReadinessStatus.ACTIVE_VERIFIED,
                verified_proof_metrics=[
                    TalentProofMetric(label="SOX Automation", evidence="Automated 42% of manual SOX testing, saving €1.2M in annual external audit fees.", category="Efficiency"),
                    TalentProofMetric(label="Audit Committee Governance", evidence="Delivered 28 clean regulatory audit opinions across Tier-1 banks.", category="Governance")
                ],
                target_compensation={"permanent_salary": "120k - 135k EUR base + bonus", "currency": "EUR"},
                mobility={"base_location": "Paris, France", "remote_preference": "Hybrid (1-2 days onsite)"},
                consent_broadcast_enabled=True,
                verified_composite_score=91.0
            )
            cls._profiles[p_sarah.profile_id] = p_sarah

            # 3. Julien - Fractional CTO
            p_julien = TalentGraphProfile(
                profile_id="cand_julien_fractional",
                anonymized_alias="Candidate #8904 — Fractional CTO & Tech Advisory Partner",
                headline="Fractional CTO & Strategic Architecture Advisor for Series A-B Startups",
                seniority="Executive VP / CTO Tier (15+ YOE)",
                target_roles=["Fractional CTO", "Tech Advisor", "Interim VP Engineering"],
                core_competencies=["Steerco Advisory", "System Architecture", "Team Scaling", "Cloud Migration"],
                governance_tags=["Steerco Governance", "Board Reporting", "Due Diligence"],
                readiness_status=ReadinessStatus.ACTIVE_VERIFIED,
                verified_proof_metrics=[
                    TalentProofMetric(label="Startup Scaling", evidence="Scaled 3 B2B SaaS startups from Seed to Series B ($15M ARR exit).", category="Growth"),
                    TalentProofMetric(label="Retainer Governance", evidence="Governs technical roadmaps across 3 concurrent high-growth clients under structured retainers.", category="Governance")
                ],
                target_compensation={"monthly_retainer": "4,000 - 5,500 EUR / month (1-2 d/wk)", "currency": "EUR"},
                mobility={"base_location": "Remote Europe", "remote_preference": "100% Remote"},
                consent_broadcast_enabled=True,
                verified_composite_score=93.0
            )
            cls._profiles[p_julien.profile_id] = p_julien

            # 4. Lucas - Junior AI Engineer
            p_lucas = TalentGraphProfile(
                profile_id="cand_lucas_ai",
                anonymized_alias="Candidate #1023 — Junior AI & LLM Systems Engineer",
                headline="Junior Applied AI Engineer | LLM Evaluations, FastAPI, LangChain & Agentic Workflows",
                seniority="Junior / Associate (2 YOE)",
                target_roles=["Junior AI Engineer", "Applied LLM Developer", "Python Backend Engineer"],
                core_competencies=["Python", "FastAPI", "LLM Benchmarking", "RAG Systems", "Docker"],
                governance_tags=["LLM Evaluation", "Automated Testing"],
                readiness_status=ReadinessStatus.ACTIVE_VERIFIED,
                verified_proof_metrics=[
                    TalentProofMetric(label="Live Deployments", evidence="Shipped open-source LLM eval harness with 1,200 GitHub stars and automated CI/CD.", category="Engineering"),
                    TalentProofMetric(label="Learning Velocity", evidence="Built production FastAPI microservices handling 50k requests/day.", category="Scale")
                ],
                target_compensation={"permanent_salary": "48k - 55k EUR base", "currency": "EUR"},
                mobility={"base_location": "Lyon, France", "remote_preference": "100% Remote / Flexible"},
                consent_broadcast_enabled=True,
                verified_composite_score=86.0
            )
            cls._profiles[p_lucas.profile_id] = p_lucas

            cls._save()
            logger.info(f"[TalentLake] Seeded {len(cls._profiles)} candidate profiles.")
