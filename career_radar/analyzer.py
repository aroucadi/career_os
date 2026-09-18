"""CareerOS Universal Generic Job Analyzer and Rubric Evaluator."""
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .models import JobPosting, RubricPillarScore, ScoredJob

try:
    from engine.profiles.manager import ProfileManager
    from engine.profiles.models import CandidateProfile
except ImportError:
    ProfileManager = None
    CandidateProfile = None

GENERIC_STOPWORDS = {
    "and", "the", "for", "with", "from", "that", "this", "will", "your", "our", "you",
    "are", "have", "been", "has", "who", "what", "which", "across", "their", "into",
    "within", "including", "such", "ability", "experience", "skills", "proven", "strong",
    "track", "record", "work", "working", "team", "teams", "role", "years", "least",
    "help", "join", "part", "looking", "candidate", "about", "other", "more", "well",
    "must", "should", "could", "also", "plus", "bonus", "knowledge", "understanding",
    "description", "responsibilities", "requirements", "overview", "mission", "context",
    "ideal", "successful", "closely", "environment", "solutions", "business", "company",
    "contract", "location", "duration", "client", "clients", "opportunity", "opportunities",
    "pour", "dans", "avec", "nous", "vous", "votre", "notre", "plus", "chez", "être",
    "avoir", "faire", "comme", "aussi", "tout", "tous", "sont", "cette", "leur", "leurs"
}


class JobAnalyzer:
    """Evaluates job descriptions dynamically against ANY candidate profile and resume."""

    def __init__(self, resume_path: Optional[Path] = None, profile: Optional[Any] = None):
        if profile is not None:
            self.profile = profile
        elif ProfileManager:
            self.profile = ProfileManager.load_profile()
        else:
            self.profile = None

        if resume_path is None:
            _root = Path(__file__).resolve().parent.parent
            if self.profile and hasattr(self.profile, "resume_file"):
                resume_path = _root / self.profile.resume_file
                if not resume_path.exists():
                    alt = _root / "resumes" / self.profile.resume_file
                    if alt.exists():
                        resume_path = alt
            else:
                resume_path = _root / "Alaa_Eddine_Roucadi_Resume_v12.md"

        self.resume_path = resume_path
        if self.resume_path and self.resume_path.exists():
            self.resume_text = self.resume_path.read_text(encoding="utf-8")
        else:
            self.resume_text = ""

    def analyze(self, job: JobPosting) -> ScoredJob:
        """Scores a job description dynamically using candidate profile and resume."""
        jd_full_text = f"{job.title}\n{job.description}"
        lower_jd = jd_full_text.lower()
        lower_resume = self.resume_text.lower()

        # ─── 1. PILLAR 1: Core Domain & Functional Match (Max 30) ─────────────
        domain_matches = []
        if self.profile:
            for domain in self.profile.scope.core_domains:
                d_low = domain.lower()
                if d_low in lower_jd:
                    domain_matches.append(domain)
                else:
                    words = [w for w in re.split(r"[\s/,-]+", d_low) if len(w) > 3 and w not in GENERIC_STOPWORDS]
                    matched_words = [w for w in words if w in lower_jd]
                    if len(matched_words) >= 2 or (len(words) == 1 and len(matched_words) == 1):
                        domain_matches.append(" ".join(matched_words))

            for title in self.profile.scope.primary_titles:
                t_low = title.lower()
                if t_low in lower_jd:
                    domain_matches.append(title)
                else:
                    t_words = [w for w in re.split(r"[\s/,-]+", t_low) if len(w) > 3 and w not in GENERIC_STOPWORDS]
                    matched_t = [w for w in t_words if w in lower_jd]
                    if len(matched_t) >= 2:
                        domain_matches.append(" ".join(matched_t))

        domain_matches = list(dict.fromkeys(domain_matches))
        base_domain_score = 12.0
        domain_score = min(30.0, base_domain_score + len(domain_matches) * 4.0)

        top_matches_str = ", ".join(domain_matches[:4]) if domain_matches else "general functional alignment"
        domain_evidence = (
            f"Core domain match ({top_matches_str}). "
            f"Candidate targets: {self.profile.headline if self.profile else 'Senior Professional'}."
        )

        # ─── 2. PILLAR 2: Operational Scale & Delivery Impact (Max 25) ────────
        scale_indicators_in_jd = [
            kw for kw in [
                "squads", "tribes", "clusters", "teams", "engineers", "scale",
                "high-traffic", "multi-region", "enterprise", "global", "millions", "throughput", "uptime"
            ] if kw in lower_jd
        ]

        scale_proof = None
        if self.profile:
            for pm in self.profile.proof_metrics:
                if pm.category.lower() in ("scale", "ci/cd velocity", "delivery"):
                    scale_proof = pm
                    break
            if not scale_proof and self.profile.proof_metrics:
                scale_proof = self.profile.proof_metrics[0]

        scale_evidence_str = scale_proof.evidence if scale_proof else "Proven delivery track record across enterprise environments"
        scale_score = min(25.0, 14.0 + len(scale_indicators_in_jd) * 2.0)
        scale_evidence = (
            f"Scale alignment ({', '.join(scale_indicators_in_jd[:3]) if scale_indicators_in_jd else 'standard operational scope'}). "
            f"Candidate verified proof: {scale_evidence_str}."
        )

        # ─── 3. PILLAR 3: Innovation, Governance & Modernization (Max 25) ───────
        gov_inno_proof = None
        if self.profile:
            for pm in self.profile.proof_metrics:
                if pm.category.lower() in ("innovation", "governance", "tooling ip", "cost & finops", "architecture"):
                    gov_inno_proof = pm
                    break

        inno_evidence_str = gov_inno_proof.evidence if gov_inno_proof else "Technical modernization and best practices implementation"
        
        modernization_in_jd = [
            kw for kw in [
                "architecture", "governance", "automation", "compliance", "observability",
                "framework", "modern", "security", "optimization", "finops", "quality", "guardrails"
            ] if kw in lower_jd
        ]
        inno_score = min(25.0, 15.0 + len(modernization_in_jd) * 1.5)
        inno_evidence = (
            f"Modernization & execution hygiene ({', '.join(modernization_in_jd[:3]) if modernization_in_jd else 'standard practice'}). "
            f"Candidate credentials: {inno_evidence_str}."
        )

        # ─── 4. PILLAR 4: Commercial, Location & Seniority Alignment (Max 20) ──
        seniority_matches = []
        if self.profile:
            sen_words = [w.lower() for w in re.split(r"[\s/,-]+", self.profile.scope.seniority) if len(w) > 3]
            seniority_matches = [w for w in sen_words if w in lower_jd]

        remote_compatible = ("remote" in lower_jd) or ("teletravail" in lower_jd) or ("flexible" in lower_jd)
        comm_score = 12.0
        if remote_compatible:
            comm_score += 4.0
        if seniority_matches:
            comm_score += min(4.0, len(seniority_matches) * 2.0)
        comm_score = min(20.0, comm_score)

        comm_evidence = (
            f"Seniority alignment ({', '.join(seniority_matches) if seniority_matches else 'aligned'}); "
            f"Working model compatibility: {'Supported (remote/flexible)' if remote_compatible else 'On-site presence required'}."
        )

        # Build scores dictionary (universal names + backward compatible aliases)
        scores_dict = {
            # Universal Canonical Pillars
            "domain_functional_match": RubricPillarScore(score=round(domain_score, 1), max_score=30.0, evidence=domain_evidence),
            "operational_scale": RubricPillarScore(score=round(scale_score, 1), max_score=25.0, evidence=scale_evidence),
            "governance_modernization": RubricPillarScore(score=round(inno_score, 1), max_score=25.0, evidence=inno_evidence),
            "commercial_seniority_alignment": RubricPillarScore(score=round(comm_score, 1), max_score=20.0, evidence=comm_evidence),

            # Backward-Compatible Aliases for Legacy CareerOS Consumers
            "change_management_adoption": RubricPillarScore(score=round(domain_score, 1), max_score=30.0, evidence=domain_evidence),
            "agentic_ai_automation": RubricPillarScore(score=round(inno_score, 1), max_score=25.0, evidence=inno_evidence),
            "scaled_agile_delivery": RubricPillarScore(score=round(scale_score, 1), max_score=25.0, evidence=scale_evidence),
            "executive_alignment": RubricPillarScore(score=round(comm_score, 1), max_score=20.0, evidence=comm_evidence),
        }

        # ─── 5. DYNAMIC BONUS & DEDUCTIONS (DRIVEN BY CANDIDATE PROFILE) ──────
        bonus = 0
        deductions = 0
        competency_gaps = []

        if self.profile:
            proof_keywords_hit = 0
            for pm in self.profile.proof_metrics:
                for kw in pm.keywords:
                    if kw.lower() in lower_jd:
                        proof_keywords_hit += 1
                        break
            if proof_keywords_hit >= 2:
                bonus += 4

            for bl in self.profile.languages.blocker_languages:
                if bl.lower() in lower_jd and any(w in lower_jd for w in ["fluent", "c1", "c2", "native", "mandatory", "required"]):
                    deductions += 10
                    competency_gaps.append(f"Mandatory language barrier: {bl}")

            for comm in self.profile.mobility.unacceptable_commutes:
                if comm.lower() in lower_jd:
                    deductions += 10
                    competency_gaps.append(f"Unacceptable commute location: {comm}")

            for anti in self.profile.scope.anti_roles:
                sub_tokens = [s.strip().lower() for s in re.split(r"[/,()]", anti) if len(s.strip()) > 2 and s.strip().lower() not in ("ic", "or", "mid", "tier")]
                for st in sub_tokens:
                    if st in job.title.lower() or st in lower_jd[:400]:
                        deductions += 15
                        competency_gaps.append(f"Anti-role conflict: {anti}")
                        break
                if ("coach" in anti.lower() or "scrum master" in anti.lower()) and ("coach" in lower_jd[:300] and "agile" in lower_jd[:300]):
                    deductions += 15
                    competency_gaps.append(f"Anti-role conflict: {anti}")

        pillar_sum = domain_score + scale_score + inno_score + comm_score
        total = int(pillar_sum + bonus - deductions)
        overall_match = max(0, min(100, total))

        # ─── 6. DYNAMIC ATS KEYWORD GAP EXTRACTION ────────────────────────────
        ats_gaps = []
        candidate_terms = set()
        words_in_jd = re.findall(r"\b[A-Za-z][A-Za-z0-9_\-\+\#]{2,}\b", jd_full_text)
        for i in range(len(words_in_jd) - 1):
            w1, w2 = words_in_jd[i].lower(), words_in_jd[i+1].lower()
            if w1 not in GENERIC_STOPWORDS and w2 not in GENERIC_STOPWORDS:
                candidate_terms.add(f"{w1} {w2}")
        for w in words_in_jd:
            wl = w.lower()
            if len(wl) > 3 and wl not in GENERIC_STOPWORDS:
                candidate_terms.add(wl)

        for term in sorted(candidate_terms, key=len, reverse=True):
            if term in lower_jd and term not in lower_resume:
                if not any(sw in term.split() for sw in ["responsibilities", "experience", "candidate"]):
                    ats_gaps.append(term)
                    if len(ats_gaps) >= 8:
                        break

        # ─── 7. DYNAMIC RECOMMENDATIONS & ACTIONS ─────────────────────────────
        recommended_actions = []
        if self.profile and self.profile.proof_metrics:
            top_p = self.profile.proof_metrics[0]
            recommended_actions.append(f"Anchor outreach on verified impact: {top_p.evidence}")
            if len(self.profile.proof_metrics) > 1:
                recommended_actions.append(f"Reinforce with secondary proof: {self.profile.proof_metrics[1].evidence}")
        if ats_gaps:
            recommended_actions.append(f"Address key JD terminology gaps in interview preparation: {', '.join(ats_gaps[:3])}")

        # ─── 8. DYNAMIC RECRUITER PITCH HOOK ──────────────────────────────────
        company_clean = job.company if job.company != "Unknown Company" else "your team"
        headline = self.profile.headline if self.profile else "Senior Professional"
        proof_cit = f" ({self.profile.proof_metrics[0].evidence})" if (self.profile and self.profile.proof_metrics) else ""
        
        pitch_hook = (
            f"Hello, I noticed {company_clean}'s opening for {job.title}. "
            f"As a {headline}{proof_cit}, I specialize in driving high-impact, "
            f"measurable production outcomes. I'd love to connect to discuss how my background aligns with your roadmap."
        )

        return ScoredJob(
            job_id=job.id,
            job_title=job.title,
            company=job.company,
            url=job.url,
            overall_match_score=overall_match,
            scores=scores_dict,
            bonus_points=bonus,
            deductions=deductions,
            ats_keyword_gaps=ats_gaps,
            competency_gaps=competency_gaps,
            recommended_actions=recommended_actions,
            recruiter_pitch_hook=pitch_hook,
        )

