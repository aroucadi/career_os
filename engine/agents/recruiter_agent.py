"""
CareerOS Recruiter Autonomous Sourcing Agent
============================================
S-Tier Autonomous ReAct Agent for enterprise recruiters & headhunters.
Takes loose hiring briefs, audio transcriptions, or JDs, parses requirements,
runs dense vector semantic search against the Talent Lake, generates custom
tactical interview questions, and orchestrates cryptographic Double Opt-In introductions.
Emits Vercel AI SDK SSE streaming tokens and Generative UI components.
"""

import os
import re
import json
import uuid
import asyncio
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from pathlib import Path
from dotenv import load_dotenv

from engine.storage.db import get_db_connection
from engine.storage.embeddings import EmbeddingsEngine
from engine.recruiter.models import CandidateMatchSlateItem, OptInStatus
from engine.recruiter.matcher import RequisitionMatcher
from engine.notifications.dispatcher import NotificationDispatcher
from engine.billing.recruiter_billing import RecruiterBillingManager, RecruiterPricing
from api.streaming import (
    format_text_delta,
    format_tool_call,
    format_tool_result,
    format_finish_message
)

logger = logging.getLogger("careeros.recruiter_agent")

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(_ROOT_DIR / ".env")


class RecruiterAgentTools:
    """Dynamic tools executed by the Autonomous Recruiter Agent."""

    @staticmethod
    def parse_and_decompose_brief(brief: str) -> Dict[str, Any]:
        """
        Decomposes unstructured natural language hiring briefs into structured parameters.
        Extracts target role, client company, key skills, eliminators, and multipliers.
        """
        clean_brief = brief.strip()
        lower = clean_brief.lower()

        # Job title heuristics
        job_title = "Executive Technology Leader"
        m_title = re.search(r"(?:looking for|hiring|role of|position of|seeking|need a|mandate for)\s+([A-Za-z0-9\s\-/]+?)(?:\.|\n|with|who|in|\bat\b)", clean_brief, re.IGNORECASE)
        if m_title:
            cand_title = m_title.group(1).strip()
            if len(cand_title) < 50:
                job_title = cand_title
        elif "ai adoption" in lower:
            job_title = "Head of AI Adoption"
        elif "delivery manager" in lower or "ai delivery" in lower:
            job_title = "AI Delivery Manager / Program Lead"
        elif "chief architect" in lower or "enterprise architect" in lower:
            job_title = "Enterprise AI Solutions Architect"
        elif "product manager" in lower:
            job_title = "Principal AI Product Manager"

        # Company heuristic
        company = "Client Enterprise"
        m_comp = re.search(r"(?:at|client|company|enterprise|bank)\s+([A-Z][A-Za-z0-9&]+)", clean_brief)
        if m_comp:
            company = m_comp.group(1).strip()
        elif "abu dhabi" in lower or "salt" in lower:
            company = "Salt Middle East (Abu Dhabi Client)"
        elif "bnp" in lower or "credit agricole" in lower or "banking" in lower:
            company = "Tier-1 Investment Bank"

        # Mandatory eliminators
        eliminators = []
        if any(w in lower for w in ["french", "francais"]):
            eliminators.append("Language: Mandatory French Professional Proficiency")
        if any(w in lower for w in ["clearance", "defense", "habilitation"]):
            eliminators.append("Compliance: Security Clearance Required")
        if any(w in lower for w in ["on-site 5 days", "full on-site", "no remote"]):
            eliminators.append("Commute: 100% On-site Required")

        # Value multipliers
        multipliers = []
        if any(w in lower for w in ["governance", "eu ai act", "compliance", "regulatory"]):
            multipliers.append("Governance: EU AI Act & High-Risk Model Auditing")
        if any(w in lower for w in ["scale", "squads", "enterprise", "banking"]):
            multipliers.append("Scale: Multi-squad enterprise engineering management")
        if any(w in lower for w in ["agent", "rag", "claude", "genai", "generative"]):
            multipliers.append("GenAI: Autonomous Agentic Architectures & Tool Use")

        return {
            "status": "SUCCESS",
            "job_title": job_title,
            "company": company,
            "mandatory_constraints": eliminators,
            "value_multipliers": multipliers,
            "raw_brief_length": len(clean_brief)
        }

    @staticmethod
    def semantic_talent_search(query: str, top_k: int = 5) -> Dict[str, Any]:
        """Runs 768-dim dense vector search over candidate talent embeddings in SQLite."""
        EmbeddingsEngine.seed_default_embeddings_if_empty()
        matches = EmbeddingsEngine.search_talent_semantic(query, top_k=top_k, min_similarity=0.35)
        return {
            "status": "SUCCESS",
            "query": query,
            "matches_count": len(matches),
            "top_candidates": matches
        }

    @staticmethod
    def rank_candidate_slate(job_title: str, jd_text: str, company: str = "Client Enterprise", min_score: float = 60.0) -> Dict[str, Any]:
        """Matches candidates against requisition using hybrid semantic + verified telemetry rubric."""
        slate = RequisitionMatcher.match_requisition(
            job_title=job_title,
            jd_text=jd_text,
            company=company,
            min_score=min_score
        )
        
        candidates_out = []
        for c in slate:
            candidates_out.append({
                "match_id": c.match_id,
                "candidate_id": c.candidate_id,
                "anonymized_alias": c.anonymized_alias,
                "headline": c.headline,
                "seniority": c.seniority,
                "overall_match_score": c.overall_match_score,
                "domain_fit_score": c.rubric_subscores.get("domain_fit", 80.0),
                "governance_score": c.rubric_subscores.get("governance", 85.0),
                "scale_match_score": c.rubric_subscores.get("scale", 80.0),
                "verified_proof_citations": c.key_leverage_points,
                "fit_summary": f"{c.seniority} matching mandate with {len(c.key_leverage_points)} verified leverage points.",
                "opt_in_status": c.opt_in_status.value if hasattr(c.opt_in_status, "value") else str(c.opt_in_status)
            })

        return {
            "status": "SUCCESS",
            "job_title": job_title,
            "total_matches": len(candidates_out),
            "candidates": candidates_out
        }

    @staticmethod
    def generate_interview_cheatsheet(candidate_alias: str, headline: str, job_title: str, proofs: Optional[List[str]] = None) -> Dict[str, Any]:
        """Synthesizes high-leverage tactical interview questions to stress-test claims."""
        proofs_list = proofs or []
        questions = [
            {
                "category": "Governance & AI Risk",
                "question": f"Given your work around {proofs_list[0] if proofs_list else 'enterprise AI governance'}, how do you enforce deterministic guardrails and prevent hallucination cascade in production?",
                "rationale": "Validates whether the candidate has hands-on experience or merely theoretical knowledge of high-risk AI deployments."
            },
            {
                "category": "Scale & Operational Cadence",
                "question": f"For a role like {job_title}, walk us through how you aligned 5+ engineering squads and cross-functional stakeholders on delivery milestones.",
                "rationale": "Tests leadership leverage, stakeholder management, and cross-team conflict resolution."
            },
            {
                "category": "Commercial & Economic ROI",
                "question": "What metrics do you use to prove that an agentic AI system delivered concrete economic ROI rather than just compute expenditure?",
                "rationale": "Verifies executive commercial discipline and accountability for business outcomes."
            }
        ]

        return {
            "status": "SUCCESS",
            "candidate_alias": candidate_alias,
            "headline": headline,
            "target_role": job_title,
            "tactical_questions": questions
        }

    @staticmethod
    def dispatch_double_opt_in(match_id: str, recruiter_notes: str = "") -> Dict[str, Any]:
        """Dispatches cryptographic Double Opt-In token to candidate and updates match status."""
        match = RequisitionMatcher.get_match(match_id)
        if not match:
            return {"status": "ERROR", "message": f"Match transaction {match_id} not found."}

        match.opt_in_status = OptInStatus.PENDING_CONSENT
        RequisitionMatcher.update_status(match_id, OptInStatus.PENDING_CONSENT)

        dispatch_res = NotificationDispatcher.dispatch_intro_request(
            candidate_alias=match.anonymized_alias,
            candidate_id=match.candidate_id,
            match_data=match.model_dump(),
            recruiter_notes=recruiter_notes
        )

        return {
            "status": "SUCCESS",
            "match_id": match_id,
            "candidate_id": match.candidate_id,
            "anonymized_alias": match.anonymized_alias,
            "opt_in_status": "PENDING_CONSENT",
            "token": dispatch_res.get("token"),
            "consent_url": dispatch_res.get("consent_url"),
            "message": f"Cryptographic Double Opt-In invitation dispatched to {match.anonymized_alias}."
        }


class RecruiterAutonomousAgent:
    """Autonomous B2B Sourcing Copilot for Recruiters and Headhunters."""

    def __init__(self, org_id: str = "org_default_test", api_key: str = "cr_live_test123"):
        self.org_id = org_id
        self.api_key = api_key

    async def execute_sourcing_stream(
        self,
        brief: str,
        auto_dispatch_top: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Executes autonomous sourcing workflow from natural language brief:
        1. Validates recruiter credits.
        2. Parses and decomposes requirements.
        3. Executes dense vector candidate matching.
        4. Synthesizes tactical interview questions.
        5. Dispatches double opt-in if requested.
        """
        # 1. Billing Gate
        ok, balance, msg = RecruiterBillingManager.consume_credits(
            self.api_key,
            cost=RecruiterPricing.MATCH_SLATE_COST,
            action="Autonomous Sourcing & Slate Match"
        )
        if not ok:
            yield format_text_delta(f"⚠️ **Recruiter Billing Notice**: {msg}\n")
            yield format_finish_message()
            return

        yield format_text_delta(f"🔍 **CareerOS Recruiter Sourcing Agent Activated** (Credits Remaining: **{balance}**)...\n\n")
        yield format_text_delta(f"📋 *Ingesting Hiring Brief*: \"{brief[:120]}...\"\n\n")
        await asyncio.sleep(0.02)

        # Step 1: Decompose Brief
        call_id_parse = f"call_{uuid.uuid4().hex[:8]}"
        yield format_tool_call(
            tool_call_id=call_id_parse,
            tool_name="RecruiterBriefDecompositionCard",
            args={"brief": brief[:300]}
        )
        parsed = RecruiterAgentTools.parse_and_decompose_brief(brief)
        yield format_tool_result(tool_call_id=call_id_parse, result=parsed)
        await asyncio.sleep(0.02)

        target_title = parsed["job_title"]
        target_company = parsed["company"]
        yield format_text_delta(f"🎯 **Target Mandate Formulated**: `{target_title}` at `{target_company}`.\n")
        yield format_text_delta(f"⚡ *Multipliers*: {', '.join(parsed['value_multipliers']) or 'None'}\n\n")

        # Step 2: Rank Candidate Slate
        call_id_slate = f"call_{uuid.uuid4().hex[:8]}"
        yield format_tool_call(
            tool_call_id=call_id_slate,
            tool_name="CandidateMatchSlateViewer",
            args={
                "job_title": target_title,
                "company": target_company,
                "min_score": 60.0
            }
        )
        slate_res = RecruiterAgentTools.rank_candidate_slate(
            job_title=target_title,
            jd_text=brief,
            company=target_company,
            min_score=60.0
        )
        yield format_tool_result(tool_call_id=call_id_slate, result=slate_res)
        await asyncio.sleep(0.02)

        candidates = slate_res.get("candidates", [])
        if not candidates:
            yield format_text_delta("⚠️ No candidates currently match the strict constraints in the Talent Intelligence Lake.\n")
            yield format_finish_message()
            return

        top_cand = candidates[0]
        yield format_text_delta(
            f"✅ **Match Slate Generated**: Found **{len(candidates)} verified candidate(s)**.\n"
            f"Top Match: **{top_cand['anonymized_alias']}** — Score: **{top_cand['overall_match_score']:.1f}%** ({top_cand['headline']}).\n\n"
        )

        # Step 3: Generate Tactical Interview Questions
        call_id_qa = f"call_{uuid.uuid4().hex[:8]}"
        yield format_tool_call(
            tool_call_id=call_id_qa,
            tool_name="InterviewTacticalQuestionsCard",
            args={
                "candidate_alias": top_cand["anonymized_alias"],
                "target_role": target_title,
                "proofs": top_cand.get("verified_proof_citations", [])
            }
        )
        qa_res = RecruiterAgentTools.generate_interview_cheatsheet(
            candidate_alias=top_cand["anonymized_alias"],
            headline=top_cand["headline"],
            job_title=target_title,
            proofs=top_cand.get("verified_proof_citations", [])
        )
        yield format_tool_result(tool_call_id=call_id_qa, result=qa_res)
        await asyncio.sleep(0.02)

        # Step 4: Dispatch Double Opt-In if requested
        lower_b = brief.lower()
        should_dispatch = auto_dispatch_top or any(w in lower_b for w in ["reach out", "request intro", "contact", "intro", "dispatch", "opt-in"])
        if should_dispatch and top_cand.get("match_id"):
            call_id_optin = f"call_{uuid.uuid4().hex[:8]}"
            yield format_tool_call(
                tool_call_id=call_id_optin,
                tool_name="DoubleOptInDispatchedCard",
                args={
                    "match_id": top_cand["match_id"],
                    "candidate_alias": top_cand["anonymized_alias"]
                }
            )
            optin_res = RecruiterAgentTools.dispatch_double_opt_in(
                match_id=top_cand["match_id"],
                recruiter_notes=f"Automated mandate sourcing for {target_title} at {target_company}"
            )
            yield format_tool_result(tool_call_id=call_id_optin, result=optin_res)
            yield format_text_delta(
                f"\n🚀 **Double Opt-In Dispatched**: A secure one-time cryptographic invitation has been sent to **{top_cand['anonymized_alias']}**.\n"
                f"*Candidate privacy is strictly preserved. Once {top_cand['anonymized_alias']} approves, full contact telemetry and unlocked Executive Dossier will be available.*\n"
            )

        yield format_text_delta("\n🏁 **Sourcing Workflow Complete**: Slate and custom interview telemetry are ready for your review.\n")
        yield format_finish_message()
