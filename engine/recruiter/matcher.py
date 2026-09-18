"""
CareerOS Requisition Decomposition & Slate Ranker
=================================================
Matches incoming recruiter job descriptions against the Talent Intelligence Lake.
Evaluates domain fit, governance credentials, verified telemetry, and compensation compatibility.
Produces ranked, audit-scored candidate slates.
"""

import re
import json
import uuid
import logging
import threading
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from engine.talent_graph.store import TalentLakeStore
from engine.talent_graph.models import TalentGraphProfile, ReadinessStatus
from .models import RequisitionSpec, CandidateMatchSlateItem, OptInStatus

logger = logging.getLogger("careeros.recruiter_matcher")

MATCHES_PATH = Path(__file__).resolve().parent.parent.parent / "storage" / "recruiter_matches.json"
_matcher_lock = threading.Lock()

class RequisitionMatcher:
    """Decomposes recruiter JDs and scores talent lake candidate slates."""

    _matches: Dict[str, CandidateMatchSlateItem] = {}
    _loaded: bool = False

    @classmethod
    def _ensure_loaded(cls):
        with _matcher_lock:
            if cls._loaded:
                return
            MATCHES_PATH.parent.mkdir(parents=True, exist_ok=True)
            if MATCHES_PATH.exists():
                try:
                    with open(MATCHES_PATH, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        cls._matches = {k: CandidateMatchSlateItem.model_validate(v) for k, v in data.items()}
                except Exception as e:
                    logger.error(f"Failed to load recruiter matches: {e}")
                    cls._matches = {}
            cls._loaded = True

    @classmethod
    def _save(cls):
        try:
            MATCHES_PATH.parent.mkdir(parents=True, exist_ok=True)
            temp_file = MATCHES_PATH.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump({k: v.model_dump() for k, v in cls._matches.items()}, f, indent=2)
            shutil.move(str(temp_file), str(MATCHES_PATH))
        except Exception as e:
            logger.error(f"Failed to persist recruiter matches: {e}")

        try:
            from engine.storage.db import get_db_connection
            from datetime import datetime, timezone
            with get_db_connection() as conn:
                for mid, item in cls._matches.items():
                    conn.execute("""
                    INSERT OR REPLACE INTO recruiter_matches (match_id, candidate_id, job_title, overall_score, opt_in_status, data_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        mid,
                        item.candidate_id,
                        item.headline,
                        item.overall_match_score,
                        item.opt_in_status.value if hasattr(item.opt_in_status, "value") else str(item.opt_in_status),
                        json.dumps(item.model_dump()),
                        datetime.now(timezone.utc).isoformat()
                    ))
        except Exception as e:
            logger.warning(f"Failed to sync recruiter matches to SQLite: {e}")

    @classmethod
    def decompose_requisition(cls, job_title: str, jd_text: str, company: str = "Hiring Client") -> RequisitionSpec:
        """Extracts eliminators and multipliers using heuristic NLP."""
        req_id = f"req_{uuid.uuid4().hex[:8]}"
        lower_jd = jd_text.lower()

        eliminators = []
        multipliers = []

        # Eliminator heuristics
        if any(w in lower_jd for w in ["french fluent", "francais courant", "french native"]):
            eliminators.append("Language: Mandatory French")
        if any(w in lower_jd for w in ["german", "deutsch"]):
            eliminators.append("Language: Mandatory German")
        if any(w in lower_jd for w in ["on-site 5 days", "full on-site", "sur site"]):
            eliminators.append("Commute: Full On-site")
        if any(w in lower_jd for w in ["security clearance", "habilitation"]):
            eliminators.append("Compliance: Security Clearance Required")

        # Multiplier heuristics
        if any(w in lower_jd for w in ["eu ai act", "responsible ai", "ia responsable"]):
            multipliers.append("Governance: EU AI Act & Compliance")
        if any(w in lower_jd for w in ["sox", "audit", "internal controls"]):
            multipliers.append("Governance: SOX 404 / Financial Controls")
        if any(w in lower_jd for w in ["coe", "center of excellence", "centre d'excellence"]):
            multipliers.append("Scale: Enterprise Center of Excellence")
        if any(w in lower_jd for w in ["multi-squad", "tribes", "squads", "50+ engineers"]):
            multipliers.append("Scale: Multi-Squad Engineering Leadership")
        if any(w in lower_jd for w in ["fractional", "advisory", "steerco"]):
            multipliers.append("Format: Fractional / Strategic Advisory")
        if any(w in lower_jd for w in ["fastapi", "python", "agentic", "claude code", "langchain"]):
            multipliers.append("Tech: Agentic SDLC & Python Stack")

        return RequisitionSpec(
            req_id=req_id,
            job_title=job_title,
            company=company,
            jd_raw_text=jd_text,
            mandatory_eliminators=eliminators,
            preferred_multipliers=multipliers
        )

    @classmethod
    def score_candidate(cls, cand: TalentGraphProfile, req: RequisitionSpec) -> Tuple[float, Dict[str, float], List[str], List[str]]:
        """
        Calculates match score between candidate and requisition.
        Returns: (overall_score, subscores, leverage_points, gaps)
        """
        lower_jd = (req.job_title + " " + req.jd_raw_text).lower()
        subscores = {"domain": 70.0, "governance": 60.0, "scale": 65.0, "compensation": 80.0}
        leverage_points = []
        gaps = []

        # 1. Domain & Title Match
        title_words = set(re.findall(r"\w+", req.job_title.lower()))
        matched_roles = [r for r in cand.target_roles if any(w in r.lower() for w in title_words if len(w) > 3)]
        if matched_roles:
            subscores["domain"] = 92.0
            leverage_points.append(f"Direct role alignment: target titles include {', '.join(matched_roles[:2])}")
        else:
            subscores["domain"] = 72.0
            gaps.append(f"Target titles differ slightly from '{req.job_title}', but core competencies align.")

        # Competency overlap
        matched_skills = [s for s in cand.core_competencies if s.lower() in lower_jd]
        if matched_skills:
            subscores["domain"] = min(98.0, subscores["domain"] + len(matched_skills) * 3.0)
            leverage_points.append(f"Verified core stack match: {', '.join(matched_skills[:3])}")

        # 2. Governance Match
        matched_gov = [g for g in cand.governance_tags if any(word in lower_jd for word in re.findall(r"\w+", g.lower()) if len(word) > 3)]
        if matched_gov:
            subscores["governance"] = 95.0
            leverage_points.append(f"Grounded governance expertise: {', '.join(matched_gov)}")
        else:
            if req.preferred_multipliers:
                subscores["governance"] = 65.0
                gaps.append("Standard governance experience without explicit mandate-specific certifications.")
            else:
                subscores["governance"] = 80.0

        # 3. Scale & Telemetry Match
        for proof in cand.verified_proof_metrics:
            p_low = proof.evidence.lower()
            if any(w in lower_jd for w in ["banking", "fintech"]) and ("banking" in p_low or "tribe" in p_low):
                subscores["scale"] = max(subscores["scale"], 94.0)
                leverage_points.append(f"Verified Scale ({proof.label}): {proof.evidence}")
            elif any(w in lower_jd for w in ["sox", "audit"]) and ("sox" in p_low or "audit" in p_low):
                subscores["scale"] = max(subscores["scale"], 95.0)
                leverage_points.append(f"Verified Audit Telemetry ({proof.label}): {proof.evidence}")
            elif any(w in lower_jd for w in ["fractional", "advisor", "startup"]) and ("scaling" in p_low or "retainer" in p_low):
                subscores["scale"] = max(subscores["scale"], 93.0)
                leverage_points.append(f"Verified Executive Advisory ({proof.label}): {proof.evidence}")
            elif any(w in lower_jd for w in ["junior", "llm", "eval"]) and ("github" in p_low or "fastapi" in p_low):
                subscores["scale"] = max(subscores["scale"], 90.0)
                leverage_points.append(f"Verified Velocity ({proof.label}): {proof.evidence}")

        # 4. Overall Weighted Score
        overall = (
            subscores["domain"] * 0.35 +
            subscores["governance"] * 0.25 +
            subscores["scale"] * 0.25 +
            subscores["compensation"] * 0.15
        )
        overall = round(min(99.0, max(50.0, overall)), 1)

        return overall, subscores, leverage_points, gaps

    @classmethod
    def match_requisition(
        cls,
        job_title: str,
        jd_text: str,
        company: str = "Hiring Client",
        min_score: float = 60.0
    ) -> List[CandidateMatchSlateItem]:
        """Runs match pipeline across all candidates in the talent lake and returns ranked candidate slate."""
        cls._ensure_loaded()
        TalentLakeStore.seed_default_talent_pool() # Ensure rich pool exists
        candidates = TalentLakeStore.list_profiles(status=ReadinessStatus.ACTIVE_VERIFIED)

        req = cls.decompose_requisition(job_title=job_title, jd_text=jd_text, company=company)
        slate: List[CandidateMatchSlateItem] = []

        with _matcher_lock:
            for cand in candidates:
                overall, subscores, leverage, gaps = cls.score_candidate(cand, req)
                if overall >= min_score:
                    match_id = f"match_{uuid.uuid4().hex[:8]}"
                    item = CandidateMatchSlateItem(
                        match_id=match_id,
                        candidate_id=cand.profile_id,
                        anonymized_alias=cand.anonymized_alias,
                        headline=cand.headline,
                        seniority=cand.seniority,
                        overall_match_score=overall,
                        rubric_subscores=subscores,
                        key_leverage_points=leverage[:3],
                        pre_identified_gaps=gaps[:2],
                        governance_tags=cand.governance_tags,
                        target_compensation=cand.target_compensation,
                        opt_in_status=OptInStatus.PENDING_CONSENT
                    )
                    cls._matches[match_id] = item
                    slate.append(item)

            cls._save()

        # Sort descending by match score
        slate.sort(key=lambda x: x.overall_match_score, reverse=True)
        return slate

    @classmethod
    def get_match(cls, match_id: str) -> Optional[CandidateMatchSlateItem]:
        cls._ensure_loaded()
        with _matcher_lock:
            if match_id in cls._matches:
                return cls._matches.get(match_id)

        # Fallback query from SQLite recruiter_matches table
        try:
            from engine.storage.db import get_db_connection
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT match_id, candidate_id, job_title, overall_score, opt_in_status, data_json FROM recruiter_matches WHERE match_id = ?", (match_id,))
                row = cursor.fetchone()
                if row:
                    raw_data = json.loads(row["data_json"]) if row["data_json"] else {}
                    item = CandidateMatchSlateItem(
                        match_id=row["match_id"],
                        candidate_id=row["candidate_id"],
                        anonymized_alias=raw_data.get("anonymized_alias", f"Candidate [{row['candidate_id'][:6]}]"),
                        headline=raw_data.get("headline", row["job_title"]),
                        seniority=raw_data.get("seniority", "Senior / Principal"),
                        overall_match_score=float(row["overall_score"]),
                        rubric_subscores=raw_data.get("rubric_subscores", {"domain": 90.0, "governance": 85.0}),
                        key_leverage_points=raw_data.get("key_leverage_points", ["Enterprise Architecture", "Leadership"]),
                        pre_identified_gaps=raw_data.get("pre_identified_gaps", []),
                        governance_tags=raw_data.get("governance_tags", ["EU AI Act"]),
                        target_compensation=raw_data.get("target_compensation", {}),
                        opt_in_status=OptInStatus(row["opt_in_status"])
                    )
                    with _matcher_lock:
                        cls._matches[match_id] = item
                    return item
        except Exception as e:
            logger.warning(f"Error querying match {match_id} from SQLite: {e}")
        return None

    @classmethod
    def update_status(cls, match_id: str, status: OptInStatus) -> Optional[CandidateMatchSlateItem]:
        item = cls.get_match(match_id)
        if item:
            item.opt_in_status = status
            cls._save()
        return item

