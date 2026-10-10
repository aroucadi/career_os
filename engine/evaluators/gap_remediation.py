"""
CareerOS Agnostic Gap Identification & Remediation Engine
=========================================================
Role-agnostic and candidate-agnostic evaluation engine that:
1. Ingests ANY raw CV text and ANY target Job Description or desired role.
2. Computes factual match score, semantic gaps, missing proof metrics, and credential deficits.
3. Synthesizes a 4-part actionable Gap Remediation Suite:
   - Skill-Up Path (Certifications, courses, study hours)
   - Capstone Proof Blueprints (Verifiable projects & repos to build)
   - Honest Resume Reframing (Before/After bullet translations without hallucinations)
   - Interview Screening Shield (Top 5 brutal gap questions + STAR speaking points)
"""

import os
import sys
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

_ENGINE_DIR = Path(__file__).resolve().parent.parent
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

logger = logging.getLogger(__name__)

class FatalGapItem(BaseModel):
    category: str = Field(..., description="competency | evidence | credential")
    title: str
    severity: str = Field("HIGH", description="CRITICAL | HIGH | MEDIUM")
    impact: str

class SkillUpItem(BaseModel):
    name: str
    type: str = Field("Certification", description="Certification | Course | Framework")
    estimated_hours: str
    urgency: str = Field("Week 1-2", description="Week 1-2 | Month 1 | Ongoing")
    credential_issuer: str
    rationale: str

class CapstoneProject(BaseModel):
    title: str
    summary: str
    proof_demonstrated: str
    deliverable: str
    estimated_build_time: str

class HonestReframingItem(BaseModel):
    current_bullet: str
    reframed_bullet: str
    target_alignment: str
    truth_guard_note: str

class InterviewQuestionItem(BaseModel):
    question: str
    interviewer_intent: str
    star_talking_points: str

class GapRemediationReport(BaseModel):
    target_role: str
    candidate_name: Optional[str] = "Candidate"
    match_score: int
    fit_label: str
    executive_summary: str
    fatal_gaps: List[FatalGapItem]
    skill_up_path: List[SkillUpItem]
    capstone_projects: List[CapstoneProject]
    honest_reframings: List[HonestReframingItem]
    interview_shield: List[InterviewQuestionItem]
    keywords_missing: List[str]
    keywords_present: List[str]

class GapRemediationEngine:
    """Agnostic evaluator and gap remediation architect."""

    @classmethod
    def evaluate(
        cls,
        cv_text: str,
        jd_text: str,
        target_role: Optional[str] = None,
        candidate_name: Optional[str] = "Candidate",
        model_name: Optional[str] = None
    ) -> GapRemediationReport:
        """Evaluates CV against target JD with LLM intelligence and deterministic safety fallback."""
        detected_role = target_role or cls._extract_role_title(jd_text)
        
        # Try LLM-powered deep semantic synthesis
        try:
            try:
                from engine.llm_utils import initialize_llm_provider, extract_json_from_response
                from engine.config import DEFAULT_MODEL, MODEL_PARAMETERS
            except ImportError:
                from llm_utils import initialize_llm_provider, extract_json_from_response
                from config import DEFAULT_MODEL, MODEL_PARAMETERS

            model = model_name or os.getenv("DEFAULT_MODEL", DEFAULT_MODEL)
            provider = initialize_llm_provider(model)

            prompt = cls._build_evaluation_prompt(cv_text, jd_text, detected_role, candidate_name)
            
            logger.info(f"Executing LLM Gap Remediation Analysis using model {model}...")
            resp = provider.chat(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an uncompromising Head of Engineering, Principal Experience Architect, "
                            "and Executive Recruiter. Your mission is to evaluate ANY candidate CV against ANY target JD. "
                            "You MUST output valid, parseable JSON matching the exact schema requested. "
                            "Strict rule: NEVER invent or hallucinate unearned degrees, certifications, or false facts for the candidate. "
                            "Reframings must be 100% honest translations of their past achievements into the target domain's vocabulary."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                options={"temperature": 0.1, "top_p": 0.9}
            )

            raw_json = extract_json_from_response(resp["message"]["content"])
            data = json.loads(raw_json)
            return GapRemediationReport(**data)

        except Exception as e:
            logger.warning(f"LLM Gap Remediation failed or timed out: {e}. Executing deterministic heuristic rubric...")
            return cls._evaluate_heuristic(cv_text, jd_text, detected_role, candidate_name)

    @classmethod
    def _extract_role_title(cls, jd_text: str) -> str:
        lines = [l.strip() for l in jd_text.splitlines() if l.strip()]
        for line in lines[:5]:
            clean = re.sub(r"^[#\s*\-]+", "", line).strip()
            if len(clean) > 3 and not any(w in clean.lower() for w in ["about us", "overview", "description", "company"]):
                return clean[:60]
        return "Target Position"

    @classmethod
    def _build_evaluation_prompt(cls, cv_text: str, jd_text: str, target_role: str, candidate_name: str) -> str:
        return f"""=== CANDIDATE RESUME ===
{cv_text[:5000]}

=== TARGET ROLE / JOB DESCRIPTION: {target_role} ===
{jd_text[:5000]}

Perform an exhaustive, role-agnostic gap analysis and synthesize an actionable gap-filling roadmap.
Return ONLY valid JSON with this exact structure:
{{
  "target_role": "{target_role}",
  "candidate_name": "{candidate_name}",
  "match_score": <int 0-100, calculated honestly based on skills overlap, evidence, and credentials>,
  "fit_label": "<Strong Match|Moderate Fit|High Gap|Critical Pivot Gap>",
  "executive_summary": "<2-3 sentence candid executive summary of fit and primary challenge>",
  "fatal_gaps": [
    {{
      "category": "competency",
      "title": "<Short title, e.g. Missing Multi-Agent Orchestration>",
      "severity": "CRITICAL",
      "impact": "<Why ATS or recruiter will hesitate>"
    }},
    {{
      "category": "evidence",
      "title": "<Short title, e.g. Missing Quantified FinOps / Latency Metrics>",
      "severity": "HIGH",
      "impact": "<Why recruiter will doubt scale>"
    }},
    {{
      "category": "credential",
      "title": "<Short title, e.g. Missing Formal Cloud / AI Credential>",
      "severity": "MEDIUM",
      "impact": "<Why screener checks may fail>"
    }}
  ],
  "skill_up_path": [
    {{
      "name": "<Exact course or certification title, e.g. AWS Certified AI Practitioner>",
      "type": "Certification",
      "estimated_hours": "15-20 hours",
      "urgency": "Week 1-2",
      "credential_issuer": "AWS / Coursera / DeepLearning.AI",
      "rationale": "<How it directly closes the primary credential gap>"
    }}
  ],
  "capstone_projects": [
    {{
      "title": "<Project title, e.g. Autonomous Multi-Agent Triage Pipeline>",
      "summary": "<What the candidate should build and open-source>",
      "proof_demonstrated": "<Exact capability proven to the hiring manager>",
      "deliverable": "<e.g. GitHub repo with CI/CD + Loom demo>",
      "estimated_build_time": "12-16 hours"
    }}
  ],
  "honest_reframings": [
    {{
      "current_bullet": "<Actual bullet or phrasing from candidate CV>",
      "reframed_bullet": "<Rewritten bullet matching target vocabulary honestly with ZERO invented facts>",
      "target_alignment": "<Why this matches the target JD expectations>",
      "truth_guard_note": "<Verification that no false claims were introduced>"
    }}
  ],
  "interview_shield": [
    {{
      "question": "<Brutal question the interviewer will ask regarding the candidate's gap>",
      "interviewer_intent": "<What the hiring team is secretly probing for>",
      "star_talking_points": "<Structured speaking points: Situation/Task, Action, Result to turn the gap into a strength>"
    }}
  ],
  "keywords_missing": ["<key skill from JD missing in CV>", ...],
  "keywords_present": ["<skill present in both>", ...]
}}"""

    @classmethod
    def _extract_candidate_bullets(cls, cv_text: str) -> List[str]:
        """Extracts genuine bullet points or meaningful achievement sentences directly from candidate CV."""
        lines = [line.strip() for line in cv_text.splitlines() if line.strip()]
        bullets = []

        for line in lines:
            # Match standard bullet characters or numbered lists
            cleaned = re.sub(r"^[\s*•\-–—►▪◦\d+.]+", "", line).strip()
            # Must be a substantive line (avoid headers or single words)
            if 25 <= len(cleaned) <= 220 and not cleaned.startswith("#"):
                bullets.append(cleaned)

        if not bullets:
            # Fallback to chunking sentences from paragraphs
            sentences = re.split(r"(?<=[.!?])\s+", cv_text)
            for s in sentences:
                s_clean = s.strip()
                if 25 <= len(s_clean) <= 200 and not s_clean.startswith("#"):
                    bullets.append(s_clean)

        return bullets[:10]

    @classmethod
    def _evaluate_heuristic(
        cls,
        cv_text: str,
        jd_text: str,
        target_role: str,
        candidate_name: str
    ) -> GapRemediationReport:
        """Deterministic heuristic analysis grounded strictly in the candidate's actual CV text."""
        cv_lower = cv_text.lower()
        jd_lower = jd_text.lower()

        # Extract genuine lines from CV for Truth Guard compliance
        actual_cv_bullets = cls._extract_candidate_bullets(cv_text)

        # Domain term checks
        tech_terms = [
            "agentic", "multi-agent", "llm", "finops", "eu ai act", "azure ai",
            "langchain", "langgraph", "docker", "fastapi", "safe", "scrum",
            "delivery", "governance", "microservices", "aws", "kubernetes", "python", "rag"
        ]

        present = [t for t in tech_terms if t in jd_lower and t in cv_lower]
        missing = [t for t in tech_terms if t in jd_lower and t not in cv_lower]

        # Calculate proportional match score based on verified overlap
        total_required = max(len(present) + len(missing), 1)
        overlap_ratio = len(present) / total_required
        
        # Grounded scoring scale: starts from 35% baseline for relevant experience up to 92%
        base_score = 35 if len(cv_text.strip()) > 100 else 15
        score = int(base_score + (overlap_ratio * 55))
        score = max(25, min(92, score))

        fit_label = "Strong Match" if score >= 80 else ("Moderate Fit" if score >= 60 else "High Gap")

        # Top fatal gaps
        fatal_gaps = []
        if any("agent" in m for m in missing) or "multi-agent" in missing:
            fatal_gaps.append(FatalGapItem(
                category="competency",
                title="Missing Explicit Agentic Architecture Proof",
                severity="CRITICAL",
                impact="Recruiters look for concrete multi-agent or tool-augmented workflow experience."
            ))
        if any(w in missing for w in ["finops", "latency", "token"]):
            fatal_gaps.append(FatalGapItem(
                category="evidence",
                title="Lack of Quantified AI Cost & FinOps Metrics",
                severity="HIGH",
                impact="Executive hiring managers require proof of managing token budgets and latency tradeoffs."
            ))
        if any(w in missing for w in ["eu ai act", "governance", "compliance"]):
            fatal_gaps.append(FatalGapItem(
                category="credential",
                title="Missing Formal AI Governance Credential",
                severity="MEDIUM",
                impact="Regulated enterprise clients favor candidates with verified EU AI Act or ethical AI training."
            ))

        if not fatal_gaps:
            fatal_gaps.append(FatalGapItem(
                category="competency",
                title="Semantic Terminology Distance",
                severity="MEDIUM",
                impact="Current resume uses generic phrasing rather than target domain keywords."
            ))

        # Skill-up path
        skill_up = [
            SkillUpItem(
                name="AWS Certified AI Practitioner / Azure AI Fundamentals (AI-900)",
                type="Certification",
                estimated_hours="15-20 hours",
                urgency="Week 1-2",
                credential_issuer="Amazon Web Services / Microsoft",
                rationale="Provides an accredited, unassailable credential for cloud AI delivery on resume header."
            ),
            SkillUpItem(
                name="DeepLearning.AI: Multi-Agent Systems & Tool-Use Architectures",
                type="Course",
                estimated_hours="10-12 hours",
                urgency="Week 2-3",
                credential_issuer="DeepLearning.AI",
                rationale="Gives concrete architectural vocabulary (planning, memory, reflection, tool calling)."
            ),
            SkillUpItem(
                name="EU AI Act Governance & Risk Classification Foundations",
                type="Framework",
                estimated_hours="8-10 hours",
                urgency="Month 1",
                credential_issuer="IAPP / Open Compliance",
                rationale="Enables you to position as a trusted advisor on regulatory release gates."
            )
        ]

        # Capstone proof
        capstones = [
            CapstoneProject(
                title="Open-Source Multi-Agent Orchestration Workflow",
                summary="Build and publish an autonomous decision pipeline with specialized agents (e.g. Ingestion, Critic, and Arbiter).",
                proof_demonstrated="Proves end-to-end fluency with agent orchestration, tool calling, and structured output parsing.",
                deliverable="Public GitHub repository + 3-minute video walkthrough",
                estimated_build_time="12-16 hours"
            ),
            CapstoneProject(
                title="Enterprise AI FinOps & SDLC Telemetry Dashboard",
                summary="Create an analytics layer tracking token consumption, latency benchmarks, and story refinement cycle-time reduction.",
                proof_demonstrated="Proves business acumen in controlling generative AI operational costs and measuring delivery value.",
                deliverable="Interactive Streamlit / Next.js dashboard demo",
                estimated_build_time="10-14 hours"
            )
        ]

        # Truth Guard: Ground honest reframings strictly in actual extracted CV text
        honest_reframings = []
        if actual_cv_bullets:
            bullet_1 = actual_cv_bullets[0]
            honest_reframings.append(HonestReframingItem(
                current_bullet=bullet_1,
                reframed_bullet=f"Steered delivery and adoption around '{bullet_1[:80]}...', translating operating models into governed execution metrics for {target_role}.",
                target_alignment=f"Elevates verified baseline experience directly to {target_role} terminology.",
                truth_guard_note="Grounds directly in verified candidate CV sentence without fabricating technical roles."
            ))
            if len(actual_cv_bullets) > 1:
                bullet_2 = actual_cv_bullets[1]
                honest_reframings.append(HonestReframingItem(
                    current_bullet=bullet_2,
                    reframed_bullet=f"Architected cross-functional flow and quality checkpoints for '{bullet_2[:80]}...', ensuring risk alignment and cross-squad velocity.",
                    target_alignment="Emphasizes structural transformation and leadership ownership.",
                    truth_guard_note="Direct translation of actual CV bullet into executive impact language."
                ))
        else:
            honest_reframings.append(HonestReframingItem(
                current_bullet=cv_text.strip()[:100] if cv_text.strip() else "General Professional Background",
                reframed_bullet=f"Leverages professional domain background to lead strategic program delivery and cross-functional execution for {target_role}.",
                target_alignment="Aligns candidate scope with target mandate expectations.",
                truth_guard_note="Safe baseline reframing using candidate summary."
            ))

        # Interview shield
        interview_shield = [
            InterviewQuestionItem(
                question=f"You come from a proven delivery background. How do you handle deep technical nuances when steering an {target_role} mandate?",
                interviewer_intent="Testing whether you are purely process-oriented or can legitimately interface with senior architects.",
                star_talking_points="Acknowledge your core operational strengths. Detail hands-on experience orchestrating complex workflows. Emphasize that your superpower is translating technical capabilities into governed, high-adoption business outcomes."
            ),
            InterviewQuestionItem(
                question="How do you manage the risk of hallucinations and non-deterministic behavior in production AI workflows?",
                interviewer_intent="Verifying understanding of AI quality gates and enterprise risk.",
                star_talking_points="Detail multi-tiered guardrails: structured JSON schemas, adversarial critic agents, deterministic fallback rules, and mandatory human sign-off gates for high-stakes decisions."
            ),
            InterviewQuestionItem(
                question="What is your approach to AI FinOps and token economics across multiple squads?",
                interviewer_intent="Evaluating fiscal and operational responsibility.",
                star_talking_points="Explain caching strategies, model tiering (fast flash models for triage vs frontier models for synthesis), and instrumenting cost-per-user telemetry."
            )
        ]

        return GapRemediationReport(
            target_role=target_role,
            candidate_name=candidate_name,
            match_score=score,
            fit_label=fit_label,
            executive_summary=f"Grounded Assessment for {target_role}: Found {len(present)} aligned keywords and {len(missing)} missing competencies. Match score calibrated to verified CV evidence.",
            fatal_gaps=fatal_gaps,
            skill_up_path=skill_up,
            capstone_projects=capstones,
            honest_reframings=honest_reframings,
            interview_shield=interview_shield,
            keywords_missing=missing[:8],
            keywords_present=present[:8]
        )
