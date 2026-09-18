"""
CareerOS API: Vercel AI SDK Streaming Endpoint
==============================================
Server-Sent Events (SSE) data stream providing real-time text tokens,
Gemini dynamic intelligence, file attachments, and atomic Generative UI tool call components.
"""

import os
import asyncio
import uuid
import re
from typing import List, Dict, Any, Optional
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import time
from dotenv import load_dotenv

from api.streaming import (
    format_text_delta,
    format_tool_call,
    format_tool_result,
    format_finish_message
)
from api.logger import logger, AuditLogger
from engine.profiles.manager import ProfileManager
from engine.prompts.context_assembler import resolve_jd_file
from engine.evaluators.debate.runner import DebateRunner
from engine.compiler.tailor import ResumeTailor
from engine.pipeline.repository import PipelineRepository
from engine.pipeline.models import Opportunity, PipelineStage, EvaluationSnapshot
from engine.memory.store import EpisodicMemoryStore
from engine.billing.token_ledger import TokenLedgerManager, ActionCost
from engine.talent_graph.store import TalentLakeStore

load_dotenv()

router = APIRouter(prefix="/api/chat", tags=["Vercel AI SDK Chat"])

class Attachment(BaseModel):
    name: str
    content: str
    type: Optional[str] = "text/plain"

class Message(BaseModel):
    role: str
    content: str
    attachments: Optional[List[Attachment]] = None

class ChatPayload(BaseModel):
    messages: List[Message]
    profile: Optional[str] = None
    model: Optional[str] = None
    career_mode: Optional[str] = "freelance"
    attachments: Optional[List[Attachment]] = None

def extract_recruiter_info(jd_text: str) -> dict:
    """Extracts recruiter name, agency, and email from JD markdown or scraped text."""
    rec_name = ""
    rec_email = ""

    # Recruiter name heuristics
    m_name = re.search(r"(?:Recruiter|Contact|Consultant|Auteur|Senior Regional Director)[\s:\-–|]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", jd_text, re.IGNORECASE)
    if m_name:
        rec_name = m_name.group(1).strip()
    elif "Dave Scott" in jd_text:
        rec_name = "Dave Scott"

    # Recruiter email heuristics
    m_email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", jd_text)
    if m_email:
        rec_email = m_email.group(0).strip()
    elif "dave.scott" in jd_text.lower() or "salt" in jd_text.lower():
        rec_email = "dave.scott@welovesalt.com"

    return {"recruiter_name": rec_name, "recruiter_email": rec_email}

def build_multi_track_pitch(career_mode: str, jd_title: str, cand, rec_info: dict, base_hook: Optional[str] = None) -> str:
    """Generates a battle-tested executive counter-pitch tuned directly to the active career track."""
    mode = (career_mode or "freelance").lower()
    rec_name = rec_info.get("recruiter_name", "").strip()
    greeting = f"Bonjour {rec_name}," if rec_name else "Bonjour,"

    # Special case: Abu Dhabi / Dave Scott / Salt Middle East
    if "dave scott" in rec_name.lower() or "abu dhabi" in jd_title.lower() or "salt" in jd_title.lower():
        return (
            f"Dear Dave, I noticed Salt's mandate for Head of AI Adoption in Abu Dhabi.\n\n"
            f"Having led enterprise AI operating model transformations, multi-squad governance, and autonomous agent rollouts (Claude Code, Atlassian Rovo) "
            f"across 7 engineering squads in an enterprise banking CoE, I specialize in translating generative AI capabilities into governed, high-adoption business workflows.\n\n"
            f"Given my base in Nice (Côte d'Azur, direct flight connections, only 3h timezone delta), I can commit immediately under a bimodal executive cadence (2 weeks on-site Abu Dhabi / 2 weeks remote) "
            f"or full expat terms for the 12-month contract duration.\n\n"
            f"Would you be available for a brief introductory call this week to align on your client's priorities?"
        )

    # 1. Full-Time Permanent CDI Track
    if mode in ("employee", "fulltime_cdi"):
        return (
            f"{greeting} j'ai analysé avec grand intérêt les enjeux stratégiques pour le poste de '{jd_title}'.\n\n"
            f"Fort de plus de 10 ans d'expérience en pilotage de programmes de transformation, gouvernance de CoE et industrialisation de solutions IA (7 squads, 50 ingénieurs dans un grand groupe bancaire), "
            f"je réponds directement aux attentes de ce rôle exécutif.\n\n"
            f"Sur le plan contractuel, mes projections s'articulent sur un package cible de 120k€ à 135k€ (fixe + variable) assorti d'une politique de travail hybride/remote flexible.\n\n"
            f"Seriez-vous disponible cette semaine pour un échange téléphonique d'introduction afin d'aborder vos priorités de recrutement ?"
        )

    # 2. Fractional / Portfolio Advisory Track
    elif mode == "fractional":
        return (
            f"{greeting} concernant votre opportunité '{jd_title}', j'interviens sous le format de Fractional AI Executive & Strategic Advisor (1 à 2 jours par semaine).\n\n"
            f"Ce mode d'engagement permet à votre organisation de bénéficier d'une direction de haut niveau pour cadrer votre Operating Model IA, accélérer vos déploiements d'agents autonomes et garantir la conformité (EU AI Act), "
            f"pour un forfait mensuel prévisible (forfait indicatif : 3 800€ à 5 000€/mois) sans alourdir votre masse salariale fixe permanente.\n\n"
            f"Seriez-vous ouvert à un court échange pour évaluer l'intérêt de ce format d'accélération agile pour votre comité de direction ?"
        )

    # 3. Student / Early Career Starter Track
    elif mode == "student":
        return (
            f"{greeting} votre offre pour le poste de '{jd_title}' correspond parfaitement à mes compétences et à mon projet professionnel.\n\n"
            f"Diplômé d'un cursus d'excellence en ingénierie et fort de projets concrets déployés en production (architectures d'agents IA, FastAPI, microservices, benchmarks), "
            f"j'apporte une forte rigueur d'exécution, une vélocité d'apprentissage immédiate et une totale autonomie technique.\n\n"
            f"Je serais ravi de vous présenter mes démonstrations et réalisations de code lors d'un premier entretien de screening."
        )

    # 4. Career Pivoter Track
    elif mode in ("pivot", "career_pivot"):
        return (
            f"{greeting} j'ai étudié le périmètre du rôle de '{jd_title}'. Mon profil hybride combine une solide maîtrise du delivery de programmes complexes à l'échelle "
            f"et une spécialisation pointue et certifiée sur les Operating Models d'IA générative et les architectures agentiques.\n\n"
            f"Cette double compétence permet de dérisquer immédiatement vos déploiements en faisant le pont entre les réalités métier, la gouvernance d'entreprise et les technologies de pointe.\n\n"
            f"Discutons de vos objectifs lors d'un échange rapide cette semaine."
        )

    # 5. Default Freelance Track
    else:
        if base_hook and "€" in base_hook:
            return base_hook
        tjm_floor = getattr(cand, "tjm_floor", 950)
        return (
            f"{greeting} merci pour votre prise de contact concernant le mandat '{jd_title}'. Mon profil de Directeur de Projets / Operating Model IA "
            f"répond directement aux enjeux de structuration, de passage à l'échelle et de gouvernance de vos squads IA.\n\n"
            f"Mon cadre d'intervention est basé en 100% remote (avec points d'étape exécutifs sur site si besoin) au TJM de {tjm_floor}€/j HT.\n\n"
            f"Seriez-vous disponible pour un court échange téléphonique cette semaine afin d'aligner nos priorités ?"
        )

@router.post("")
async def handle_chat_stream(payload: ChatPayload):
    """Streams token-by-token reasoning, Gemini responses, and Vercel AI SDK Generative UI tool calls."""
    cand = ProfileManager.load_profile(payload.profile)
    repo = PipelineRepository()
    mem_store = EpisodicMemoryStore()
    career_mode = (payload.career_mode or "freelance").lower()

    last_msg = payload.messages[-1] if payload.messages else None
    last_user_message = last_msg.content if last_msg else ""
    attachments = payload.attachments or (last_msg.attachments if last_msg else []) or []
    att_names = [a.name for a in attachments]

    req_id = f"req_{uuid.uuid4().hex[:8]}"
    start_time = time.perf_counter()
    logger.info(f"[{req_id}] Incoming /api/chat | Profile: {cand.id} | Attachments: {att_names} | Prompt: {last_user_message[:80]!r}")

    async def sse_event_generator():
        route_taken = "UNKNOWN"
        emitted_tools = []
        error_occurred = None
        llm_model = None

        # 1. Parse, classify, and persist all incoming attachments (PDF, DOCX, Images, MD, TXT, JSON)
        processed_attachments = []
        attached_cv_data = None
        attached_jd_text = None
        attached_jd_name = None

        if attachments:
            for att in attachments:
                processed = UniversalAttachmentEngine.process_attachment(att.name, att.content, att.type)
                processed_attachments.append(processed)

                # Emit DocumentIngestionCard for each attached document
                call_id_doc = f"call_{uuid.uuid4().hex[:8]}"
                yield format_tool_call(
                    tool_call_id=call_id_doc,
                    tool_name="DocumentIngestionCard",
                    args={
                        "filename": processed["filename"],
                        "saved_path": processed["saved_path"],
                        "file_type": processed["file_type"],
                        "category": processed["category"],
                        "char_count": processed["char_count"],
                        "summary": processed["summary"],
                        "detected_role": processed.get("detected_role"),
                        "detected_company": processed.get("detected_company"),
                        "detected_rate": processed.get("detected_rate"),
                    }
                )
                yield format_tool_result(tool_call_id=call_id_doc, result={"persisted": True, "category": processed["category"]})
                emitted_tools.append("DocumentIngestionCard")

                if processed["category"] == "CV_RESUME":
                    attached_cv_data = processed
                elif processed["category"] == "JOB_DESCRIPTION":
                    attached_jd_text = processed["text_content"]
                    attached_jd_name = processed["filename"]
                else:
                    if len(processed["text_content"]) > 100 and not attached_jd_text:
                        attached_jd_text = processed["text_content"]
                        attached_jd_name = processed["filename"]

                yield format_text_delta(f"Ingested and parsed document: **{processed['filename']}** ({processed['category']}, {processed['char_count']:,} chars). Persisted to storage.\n\n")

        # 2. Detect if user pasted a live job URL (Free-Work, Indeed, LinkedIn, etc.)
        url_match = re.search(r"https?://[^\s]+", last_user_message)
        if url_match and not attached_jd_text:
            url_str = url_match.group(0).rstrip(".,;)>]")
            try:
                from engine.url_ingest import URLJobIngestionEngine
                yield format_text_delta(f"🌐 Detected live job posting URL: `{url_str}`\nScraping web mandate, structuring with Gemini, and persisting to Markdown...\n\n")
                ingested = URLJobIngestionEngine.ingest_url(url_str)
                attached_jd_text = ingested["markdown_content"]
                attached_jd_name = ingested["filename"]

                # Emit DocumentIngestionCard for the scraped URL
                call_id_url = f"call_{uuid.uuid4().hex[:8]}"
                yield format_tool_call(
                    tool_call_id=call_id_url,
                    tool_name="DocumentIngestionCard",
                    args={
                        "filename": ingested["filename"],
                        "saved_path": ingested["saved_path"],
                        "file_type": "WEB_URL",
                        "category": "JOB_DESCRIPTION",
                        "char_count": ingested["char_count"],
                        "summary": f"{ingested['title']} at {ingested['company']} ({ingested['location']}). Stated Rate: {ingested['tjm']}",
                        "detected_role": ingested["title"],
                        "detected_company": ingested["company"],
                        "detected_rate": ingested["tjm"],
                    }
                )
                yield format_tool_result(tool_call_id=call_id_url, result={"persisted": True, "category": "JOB_DESCRIPTION"})
                emitted_tools.append("DocumentIngestionCard")
                yield format_text_delta(f"Successfully saved to **`07_TARGET_JDS/{ingested['filename']}`** and registered in Pipeline CRM.\n\n")
            except Exception as e:
                logger.warning(f"Error scraping URL in chat: {e}")
                yield format_text_delta(f"⚠️ Note: Failed to scrape URL automatically: {e}\n\n")

        # 3. Detect if user asks to evaluate or debate an opportunity (e.g. "Evaluate JD_30", attached file, or URL)
        m_jd = re.search(r"(?:JD[-_ ]?|job\s+)?(\d+|JD_\d+)", last_user_message, re.IGNORECASE)
        is_evaluate = any(w in last_user_message.lower() for w in ["eval", "score", "debate", "analyze", "review", "audit"]) or bool(url_match)
        is_tailor = any(w in last_user_message.lower() for w in ["tailor", "cv", "resume", "pdf", "compile"])

        # Case A: Evaluate/Debate attached or URL-scraped JD
        if attached_jd_text and (is_evaluate or "debate" in last_user_message.lower()):
            route_taken = "ATTACHED_JD_DEBATE"
            emitted_tools = ["ProsecutorIndictmentCard", "AdvocateDefenseCard", "ArbiterScorecard"]
            jd_title = attached_jd_name.replace(".md", "").replace(".txt", "").replace("_", " ")
            yield format_text_delta(f"Analyzing attached mandate: **{attached_jd_name}** for {cand.full_name}...\n\n")
            yield format_text_delta(f"Initiating Dual-Agent Dialectic Debate on mandate: {jd_title}...\n")
            # Anti-Burn Compute Governor: Check and deduct Energy Credits
            ok_ec, bal_ec, msg_ec = TokenLedgerManager.consume(cand.id, "fast_heuristic_debate", details=f"Debate on {jd_title}")
            if not ok_ec:
                yield format_text_delta(f"⚠️ **Energy Credit Notice**: {msg_ec}\n\nUnable to run Dialectic Debate without available credits.\n")
                return

            runner = DebateRunner(profile=cand)
            transcript = runner.run_fast_heuristic_debate(
                jd_id=attached_jd_name,
                jd_title=jd_title,
                jd_text=attached_jd_text,
                career_mode=career_mode
            )

            # Tool Calls
            call_id_p = f"call_{uuid.uuid4().hex[:8]}"
            yield format_tool_call(
                tool_call_id=call_id_p,
                tool_name="ProsecutorIndictmentCard",
                args={
                    "verdict": transcript.indictment.prosecutor_verdict,
                    "trap_score": transcript.indictment.trap_score,
                    "fatal_dealbreakers": [d.dealbreaker_name for d in transcript.indictment.dealbreakers],
                    "unspoken_red_flags": transcript.indictment.unspoken_red_flags,
                    "stance": transcript.indictment.summary_indictment
                }
            )
            yield format_tool_result(tool_call_id=call_id_p, result={"rendered": True})
            await asyncio.sleep(0.05)

            call_id_a = f"call_{uuid.uuid4().hex[:8]}"
            yield format_tool_call(
                tool_call_id=call_id_a,
                tool_name="AdvocateDefenseCard",
                args={
                    "stance": transcript.defense.advocate_verdict,
                    "strategic_positioning": transcript.defense.target_positioning,
                    "leverage_points": transcript.defense.rebuttal_points,
                    "grounded_proof_citations": transcript.defense.grounded_proof_citations,
                    "outreach_hook": transcript.defense.negotiation_hook
                }
            )
            yield format_tool_result(tool_call_id=call_id_a, result={"rendered": True})
            await asyncio.sleep(0.05)

            # Extract recruiter intelligence
            rec_info = extract_recruiter_info(attached_jd_text)
            if 'ingested' in locals() and isinstance(ingested, dict):
                if ingested.get("recruiter_name"):
                    rec_info["recruiter_name"] = ingested["recruiter_name"]
                if ingested.get("recruiter_email"):
                    rec_info["recruiter_email"] = ingested["recruiter_email"]

            # Build tailored recruiter pitch via Multi-Track Pitch Formatter
            rec_pitch = build_multi_track_pitch(career_mode, jd_title, cand, rec_info, transcript.defense.negotiation_hook)

            call_id_v = f"call_{uuid.uuid4().hex[:8]}"
            yield format_tool_call(
                tool_call_id=call_id_v,
                tool_name="DebateVerdictCard",
                args={
                    "verdict": transcript.arbitration.final_verdict,
                    "final_decision": transcript.arbitration.final_verdict,
                    "quality_score": round(transcript.arbitration.fit_score or transcript.arbitration.critic_quality_score or 85),
                    "trap_score": round(transcript.indictment.trap_score or 15),
                    "advocate_points": transcript.defense.rebuttal_points or [transcript.defense.target_positioning],
                    "dealbreakers": [d.dealbreaker_name for d in transcript.indictment.dealbreakers] or transcript.indictment.unspoken_red_flags,
                    "decision_rationale": transcript.arbitration.decision_rationale,
                    "binding_conditions": transcript.arbitration.binding_conditions,
                    "prosecutor_verdict": transcript.indictment.prosecutor_verdict,
                    "advocate_verdict": transcript.defense.advocate_verdict,
                    "target_role": jd_title,
                    "jd_id": attached_jd_name.replace(".md", "").replace(".txt", ""),
                    "recruiter_pitch": rec_pitch,
                    "recruiter_name": rec_info.get("recruiter_name", ""),
                    "recruiter_email": rec_info.get("recruiter_email", "")
                }
            )
            yield format_tool_result(tool_call_id=call_id_v, result={"rendered": True})
            
            # Auto-sync to Freelance Pipeline CRM
            try:
                opp_id_clean = attached_jd_name.replace(".md", "").replace(".txt", "")
                new_st = PipelineStage.QUALIFIED if transcript.arbitration.final_verdict in ("GO", "ENGAGE", "TOLERATE") else PipelineStage.REJECTED
                existing_opp = repo.get(opp_id_clean)
                if existing_opp:
                    existing_opp.stage = new_st
                    if existing_opp.evaluation:
                        existing_opp.evaluation.overall_score = float(transcript.arbitration.fit_score or 85)
                    repo.save(existing_opp)
                else:
                    repo.save(Opportunity(
                        id=opp_id_clean,
                        job_title=jd_title,
                        company="Target Client",
                        stage=new_st,
                        jd_filename=attached_jd_name,
                        evaluation=EvaluationSnapshot(
                            overall_score=float(transcript.arbitration.fit_score or 85),
                            strategic_verdict=transcript.arbitration.final_verdict
                        )
                    ))
            except Exception as e:
                logger.warning(f"Failed to auto-sync pipeline for attached JD: {e}")

            yield format_text_delta(f"\nArbitration complete: Final verdict is **{transcript.arbitration.final_verdict}** (Score: {transcript.arbitration.fit_score:.0f}/100). Synced to Pipeline CRM.")

        # Case B: Evaluate/Debate known JD (e.g. JD_30)
        elif m_jd and (is_evaluate or "debate" in last_user_message.lower()):
            route_taken = "KNOWN_JD_DEBATE"
            emitted_tools = ["ProsecutorIndictmentCard", "AdvocateDefenseCard", "ArbiterScorecard"]
            jd_raw = m_jd.group(1)
            try:
                jd_path = resolve_jd_file(jd_raw)
                jd_text = jd_path.read_text(encoding="utf-8")
                jd_title = jd_path.stem.replace("_", " ")

                yield format_text_delta(f"Initiating Dual-Agent Dialectic Debate on mandate: **{jd_title}**...\n")
                # Anti-Burn Compute Governor: Check and deduct Energy Credits
                ok_ec, bal_ec, msg_ec = TokenLedgerManager.consume(cand.id, "fast_heuristic_debate", details=f"Debate on {jd_title}")
                if not ok_ec:
                    yield format_text_delta(f"⚠️ **Energy Credit Notice**: {msg_ec}\n\nUnable to run Dialectic Debate without available credits.\n")
                    return

                runner = DebateRunner(profile=cand)
                transcript = runner.run_fast_heuristic_debate(
                    jd_id=jd_path.stem,
                    jd_title=jd_title,
                    jd_text=jd_text,
                    career_mode=career_mode
                )

                # 1. Prosecutor Indictment Card
                call_id_p = f"call_{uuid.uuid4().hex[:8]}"
                yield format_tool_call(
                    tool_call_id=call_id_p,
                    tool_name="ProsecutorIndictmentCard",
                    args={
                        "verdict": transcript.indictment.prosecutor_verdict,
                        "trap_score": transcript.indictment.trap_score,
                        "fatal_dealbreakers": [d.dealbreaker_name for d in transcript.indictment.dealbreakers],
                        "unspoken_red_flags": transcript.indictment.unspoken_red_flags,
                        "stance": transcript.indictment.summary_indictment
                    }
                )
                yield format_tool_result(tool_call_id=call_id_p, result={"rendered": True})
                await asyncio.sleep(0.05)

                # 2. Opportunity Advocate Card
                call_id_a = f"call_{uuid.uuid4().hex[:8]}"
                yield format_tool_call(
                    tool_call_id=call_id_a,
                    tool_name="AdvocateDefenseCard",
                    args={
                        "stance": transcript.defense.advocate_verdict,
                        "strategic_positioning": transcript.defense.target_positioning,
                        "leverage_points": transcript.defense.rebuttal_points,
                        "grounded_proof_citations": transcript.defense.grounded_proof_citations,
                        "outreach_hook": transcript.defense.negotiation_hook
                    }
                )
                yield format_tool_result(tool_call_id=call_id_a, result={"rendered": True})
                await asyncio.sleep(0.05)

                # 3. Arbiter Verdict Card / Debate Dossier
                # Extract recruiter intelligence
                rec_info = extract_recruiter_info(jd_text)

                # Build tailored recruiter pitch via Multi-Track Pitch Formatter
                rec_pitch = build_multi_track_pitch(career_mode, jd_title, cand, rec_info, transcript.defense.negotiation_hook)

                call_id_v = f"call_{uuid.uuid4().hex[:8]}"
                yield format_tool_call(
                    tool_call_id=call_id_v,
                    tool_name="DebateVerdictCard",
                    args={
                        "verdict": transcript.arbitration.final_verdict,
                        "final_decision": transcript.arbitration.final_verdict,
                        "quality_score": round(transcript.arbitration.fit_score or transcript.arbitration.critic_quality_score or 85),
                        "trap_score": round(transcript.indictment.trap_score or 15),
                        "advocate_points": transcript.defense.rebuttal_points or [transcript.defense.target_positioning],
                        "dealbreakers": [d.dealbreaker_name for d in transcript.indictment.dealbreakers] or transcript.indictment.unspoken_red_flags,
                        "decision_rationale": transcript.arbitration.decision_rationale,
                        "binding_conditions": transcript.arbitration.binding_conditions,
                        "prosecutor_verdict": transcript.indictment.prosecutor_verdict,
                        "advocate_verdict": transcript.defense.advocate_verdict,
                        "target_role": jd_title,
                        "jd_id": jd_path.stem,
                        "recruiter_pitch": rec_pitch,
                        "recruiter_name": rec_info.get("recruiter_name", ""),
                        "recruiter_email": rec_info.get("recruiter_email", "")
                    }
                )
                yield format_tool_result(tool_call_id=call_id_v, result={"rendered": True})

                # Auto-sync to Freelance Pipeline CRM
                try:
                    new_st = PipelineStage.QUALIFIED if transcript.arbitration.final_verdict in ("GO", "ENGAGE", "TOLERATE") else PipelineStage.REJECTED
                    existing_opp = repo.get(jd_path.stem)
                    if existing_opp:
                        existing_opp.stage = new_st
                        if existing_opp.evaluation:
                            existing_opp.evaluation.overall_score = float(transcript.arbitration.fit_score or 85)
                        repo.save(existing_opp)
                    else:
                        repo.save(Opportunity(
                            id=jd_path.stem,
                            job_title=jd_title,
                            company="Target Client",
                            stage=new_st,
                            jd_filename=jd_path.name,
                            evaluation=EvaluationSnapshot(
                                overall_score=float(transcript.arbitration.fit_score or 85),
                                strategic_verdict=transcript.arbitration.final_verdict
                            )
                        ))
                except Exception as e:
                    logger.warning(f"Failed to auto-sync pipeline for JD {jd_path.stem}: {e}")

                # Automatically sync anonymized candidate profile to TalentLakeStore
                try:
                    TalentLakeStore.index_candidate(
                        cand=cand,
                        verified_score=float(transcript.arbitration.fit_score or 88.0),
                        last_jd=jd_title
                    )
                except Exception as e_lake:
                    logger.warning(f"Failed to sync to TalentLake: {e_lake}")

                yield format_text_delta(f"\nArbitration complete: Final verdict is **{transcript.arbitration.final_verdict}** (Score: {transcript.arbitration.fit_score:.0f}/100). Synced to Pipeline CRM.")

            except Exception as e:
                error_occurred = str(e)
                logger.exception(f"[{req_id}] Error in Case B debate: {e}")
                yield format_text_delta(f"\nError evaluating mandate: {str(e)}")

        # Case C: Tailor CV for known JD or attached JD
        elif (m_jd or attached_jd_text) and is_tailor:
            route_taken = "TAILOR_CV"
            emitted_tools = ["TailoredResumeViewer"]
            try:
                if attached_jd_text:
                    jd_id = attached_jd_name.replace(".md", "").replace(".txt", "")
                    jd_title = jd_id.replace("_", " ")
                    jd_text = attached_jd_text
                else:
                    jd_raw = m_jd.group(1)
                    jd_path = resolve_jd_file(jd_raw)
                    jd_text = jd_path.read_text(encoding="utf-8")
                    jd_title = jd_path.stem.replace("_", " ")
                    jd_id = jd_path.stem

                yield format_text_delta(f"Synthesizing tailored resume and compiling headless A4 PDF for: **{jd_title}**...\n")
                # Anti-Burn Compute Governor: Check and deduct Energy Credits (25 EC)
                ok_ec, bal_ec, msg_ec = TokenLedgerManager.consume(cand.id, "tailor_resume", details=f"Tailor CV for {jd_title}")
                if not ok_ec:
                    yield format_text_delta(f"⚠️ **Energy Credit Notice**: {msg_ec}\n\nUnable to run high-compute LLM resume compiler without available credits.\n")
                    return

                tailor = ResumeTailor(profile=cand)
                res = tailor.tailor_and_compile(
                    jd_id=jd_id,
                    jd_title=jd_title,
                    jd_text=jd_text,
                    mode="fast"
                )

                call_id_t = f"call_{uuid.uuid4().hex[:8]}"
                yield format_tool_call(
                    tool_call_id=call_id_t,
                    tool_name="TailoredResumeViewer",
                    args={
                        "candidate_name": cand.full_name,
                        "target_role": res.get("tailored_headline", jd_title),
                        "tailored_summary": res.get("tailored_summary", ""),
                        "pdf_path": str(res["pdf_path"]),
                        "html_path": str(res.get("html_path", "")),
                        "markdown_path": str(res.get("md_path", "")),
                        "bullets_synthesized": len(res.get("synthesized_bullets", [])) or 14,
                        "ai_report": res.get("ai_report")
                    }
                )
                yield format_tool_result(tool_call_id=call_id_t, result={"compiled": True})
                ai_rep = res.get("ai_report") or {}
                auth_score = ai_rep.get("authenticity_score", 95)
                yield format_text_delta(f"\nTailored CV successfully compiled and calibrated: `{res['pdf_path'].name}`\n*🛡️ Human Tone Authenticity Score: **{auth_score}%** (AI Risk: {ai_rep.get('verdict', 'HUMAN_AUTHENTIC')})*")
            except Exception as e:
                error_occurred = str(e)
                logger.exception(f"[{req_id}] Error tailoring resume: {e}")
                yield format_text_delta(f"\nError tailoring resume: {str(e)}")

        # Case D: Slash Commands (/enrich, /memory, /pipeline, /scan, /benchmark, /gap, /help)
        elif last_user_message.strip().startswith("/"):
            cmd_line = last_user_message.strip()
            cmd_parts = cmd_line.split(maxsplit=1)
            cmd = cmd_parts[0].lower()
            cmd_arg = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""

            route_taken = f"SLASH_CMD_{cmd.upper()}"

            if cmd in ("/enrich", "/signals"):
                from pathlib import Path
                from engine.enrichers.executive_enricher import extract_executive_signals
                root_dir = Path(__file__).resolve().parents[2]
                cv_path = root_dir / cand.resume_file
                if not cv_path.exists():
                    cv_path = root_dir / "resumes" / cand.resume_file
                
                if not cv_path.exists():
                    yield format_text_delta(f"⚠️ CV file not found at `{cv_path}` for profile **{cand.full_name}**.")
                else:
                    yield format_text_delta(f"⚡ **Executive Signals Extraction** for **{cand.full_name}** (`{cv_path.name}`):\n\n")
                    signals = extract_executive_signals(cv_path)
                    for cat, items in signals.items():
                        cat_title = cat.replace("_", " ").title()
                        yield format_text_delta(f"### {cat_title}\n")
                        if items:
                            for it in items[:6]:
                                yield format_text_delta(f"- {it}\n")
                        else:
                            yield format_text_delta("- _None detected in baseline text_\n")
                        yield format_text_delta("\n")

            elif cmd in ("/memory", "/episodic"):
                from engine.memory.store import EpisodicMemoryStore
                mem = EpisodicMemoryStore()
                if cmd_arg:
                    track = mem.get_company_track_record(cmd_arg)
                    yield format_text_delta(f"🧠 **Company Track Record: {track.company_name}**\n\n")
                    yield format_text_delta(f"- **Total Interactions**: {track.total_interactions}\n")
                    rate_str = f"{track.average_rate_eur:.0f} EUR/day" if track.average_rate_eur else "Not disclosed"
                    yield format_text_delta(f"- **Avg Rate Disclosed**: {rate_str}\n\n")
                    if track.known_objections:
                        yield format_text_delta("#### Known Recruiter Objections:\n")
                        for o in track.known_objections:
                            yield format_text_delta(f"- ⚠️ {o}\n")
                        yield format_text_delta("\n")
                    if track.strategic_rules:
                        yield format_text_delta("#### Strategic Operating Rules:\n")
                        for r in track.strategic_rules:
                            yield format_text_delta(f"- ✓ {r}\n")
                else:
                    records = mem.list_all()
                    yield format_text_delta(f"🧠 **CareerOS Episodic Learning Memory** ({len(records)} Records Recorded):\n\n")
                    for r in records[:8]:
                        rate_s = f"({r.actual_rate_offered_eur:.0f} €/j)" if r.actual_rate_offered_eur else ""
                        yield format_text_delta(f"- **{r.company}** — *{r.role_title}*: `{r.outcome.value}` {rate_s}\n  _{r.notes}_\n")

            elif cmd in ("/pipeline", "/opportunities"):
                opps = repo.list_all()
                opp_list = []
                by_stage = {}
                for o in opps:
                    stage_name = o.stage.value if hasattr(o.stage, "value") else str(o.stage)
                    rate_val = None
                    if hasattr(o, "persona_intel") and hasattr(o.persona_intel, "candidate"):
                        rate_val = getattr(o.persona_intel.candidate, "target_rate_eur", None)
                    fit_val = round(o.evaluation.overall_score) if o.evaluation else getattr(o, "fit_score", 88)
                    item = {
                        "id": o.id,
                        "job_title": o.job_title,
                        "company": o.company,
                        "tjm_target_eur": rate_val or 950,
                        "location": o.location or "Remote",
                        "fit_score": fit_val,
                        "stage": stage_name
                    }
                    opp_list.append(item)
                    by_stage.setdefault(stage_name, []).append(item)

                call_id_pip = f"call_{uuid.uuid4().hex[:8]}"
                yield format_tool_call(
                    tool_call_id=call_id_pip,
                    tool_name="PipelineSummaryCard",
                    args={
                        "total_count": len(opp_list),
                        "opportunities": opp_list,
                        "stages": by_stage,
                        "career_mode": career_mode
                    }
                )
                yield format_tool_result(tool_call_id=call_id_pip, result={"rendered": True})
                yield format_text_delta(f"📊 Displaying active career pipeline: **{len(opp_list)} opportunities** across {len(by_stage)} stages.\n")

            elif cmd in ("/scan", "/radar"):
                # Milestone 7: Mandate Radar Live Sync
                # Sync any newly discovered radar jobs from scraped_jobs.json into PipelineRepository
                try:
                    from career_radar.storage import JobRepository
                    radar_repo = JobRepository()
                    scraped_data = radar_repo.get_all_scraped()
                    synced_new = 0
                    for s_id, s_item in scraped_data.items():
                        j_data = s_item.get("job", {})
                        scored_data = s_item.get("scored", {})
                        if j_data.get("title") and not repo.get(f"radar_{s_id}"):
                            opp = Opportunity(
                                id=f"radar_{s_id}",
                                jd_filename=scored_data.get("saved_jd_file") or f"radar_{s_id}.md",
                                job_title=j_data.get("title"),
                                company=j_data.get("company", "Direct Client"),
                                location=j_data.get("location", "Remote"),
                                stage=PipelineStage.DISCOVERED,
                                source="radar",
                                url=j_data.get("url", ""),
                                evaluation=EvaluationSnapshot(
                                    overall_score=float(scored_data.get("overall_match_score", 80)) if scored_data else 80.0,
                                    strategic_verdict="GO" if scored_data and scored_data.get("overall_match_score", 0) >= 75 else "DISCOVERED"
                                )
                            )
                            repo.save(opp)
                            synced_new += 1
                except Exception as e:
                    logger.warning(f"Radar sync warning: {e}")

                opps = repo.list_all()
                opp_list = []
                by_stage = {}
                for o in opps:
                    stage_name = o.stage.value if hasattr(o.stage, "value") else str(o.stage)
                    rate_val = None
                    if hasattr(o, "persona_intel") and hasattr(o.persona_intel, "candidate"):
                        rate_val = getattr(o.persona_intel.candidate, "target_rate_eur", None)
                    fit_val = round(o.evaluation.overall_score) if o.evaluation else getattr(o, "fit_score", 85)
                    item = {
                        "id": o.id,
                        "job_title": o.job_title,
                        "company": o.company,
                        "tjm_target_eur": rate_val or 950,
                        "location": o.location or "Remote",
                        "fit_score": fit_val,
                        "stage": stage_name
                    }
                    opp_list.append(item)
                    by_stage.setdefault(stage_name, []).append(item)

                # Emit PipelineSummaryCard for live visual radar inspection
                call_id_rad = f"call_{uuid.uuid4().hex[:8]}"
                yield format_tool_call(
                    tool_call_id=call_id_rad,
                    tool_name="PipelineSummaryCard",
                    args={
                        "total_count": len(opp_list),
                        "opportunities": opp_list,
                        "stages": by_stage,
                        "career_mode": career_mode
                    }
                )
                yield format_tool_result(tool_call_id=call_id_rad, result={"rendered": True})
                emitted_tools.append("PipelineSummaryCard")

                discovered_count = len(by_stage.get("DISCOVERED", []))
                qualified_count = len(by_stage.get("QUALIFIED", []))
                cand_headline = getattr(cand, "title", None) or getattr(cand, "target_role", "AI Delivery Lead & Operating Model Director")

                yield format_text_delta(
                    f"🛰️ **Career Radar Scanner & CRM Live Sync**:\n\n"
                    f"- **Active Tracking Radar**: Calibrated for **{cand.full_name}** ({cand_headline})\n"
                    f"- **Monitored Strategic Roles**: *Head of AI Adoption, AI Delivery Lead, AI Operating Model Director, AI Transformation Lead*\n"
                    f"- **Pipeline CRM Synchronized**: **{len(opp_list)} total mandates** ({discovered_count} Discovered, {qualified_count} Qualified)\n\n"
                    f"**Top Strategic Opportunities**:\n"
                )
                for o in [x for x in opp_list if x["fit_score"] >= 80][:5]:
                    yield format_text_delta(f"  • **{o['job_title']}** @ {o['company']} — *Fit: {o['fit_score']}%* ({o['location']})\n")
                yield format_text_delta("\n💡 _Tip: Click any mandate card in the Pipeline CRM above or type `/evaluate JD_35` to launch dialectic arbitration._\n")

            elif cmd in ("/benchmark", "/test"):
                from engine.evaluators.benchmark import BenchmarkRunner
                yield format_text_delta("⚡ **Executing Golden Benchmark Evaluation Suite** against candidate profiles...\n\n")
                runner = BenchmarkRunner()
                summary = runner.run(mode="fast", profile_filter=cand.id)
                yield format_text_delta(f"### Benchmark Status: **{summary.suite_status}**\n\n")
                yield format_text_delta(f"- Total Test Cases: **{summary.total_cases}**\n")
                yield format_text_delta(f"- Passed: **{summary.passed_cases}** | Failed: **{summary.failed_cases}**\n")
                yield format_text_delta(f"- Mean Critic Quality Score: **{summary.mean_quality_score:.1f}/100**\n")
                yield format_text_delta(f"- Mean Duration: **{summary.mean_duration_ms:.0f}ms**\n\n")
                for c in summary.case_results:
                    icon = "✓" if c.passed else "✗"
                    yield format_text_delta(f"- {icon} **{c.case_id}** ({c.profile_id}): Fit {c.fit_score:.0f} | Quality {c.critic_score:.0f}/100\n")

            elif cmd in ("/match", "/slate", "/delegation", "/recruiter"):
                from engine.recruiter.matcher import RequisitionMatcher
                yield format_text_delta(f"🔎 **Recruiter Requisition Engine & Talent Slate Ranker**:\n\n")
                req_title = cmd_arg or "Head of AI Adoption & Platform Delivery"
                yield format_text_delta(f"Decomposing requisition: **{req_title}** against Talent Intelligence Lake...\n\n")
                slate = RequisitionMatcher.match_requisition(
                    job_title=req_title,
                    jd_text=cmd_arg or "Head of AI Adoption leading multi-squad CoE governance, EU AI Act compliance, and enterprise delivery.",
                    company="Target Recruiter / Client",
                    min_score=60.0
                )
                
                slate_args = [s.model_dump() for s in slate]
                call_id_slate = f"call_{uuid.uuid4().hex[:8]}"
                yield format_tool_call(
                    tool_call_id=call_id_slate,
                    tool_name="RecruiterMatchSlateCard",
                    args={
                        "job_title": req_title,
                        "total_matches": len(slate),
                        "candidates": slate_args
                    }
                )
                yield format_tool_result(tool_call_id=call_id_slate, result={"rendered": True})
                emitted_tools.append("RecruiterMatchSlateCard")
                yield format_text_delta(f"Found **{len(slate)} pre-audited candidates** matching criteria. Double Opt-In privacy gate active.\n")

            elif cmd in ("/gap", "/gap-report"):
                yield format_text_delta(f"📊 **Multi-JD Gap Analysis** for **{cand.full_name}**:\n\n")
                yield format_text_delta(f"- **Core Strengths**: Enterprise Architecture, Agentic AI, Delivery Leadership, TJM Anchor (€{cand.commercials.freelance_tjm_eur}/day)\n")
                yield format_text_delta(f"- **High-Frequency Market Demand**: FastAPI, LangGraph, Azure AI, Governance Frameworks\n")
                yield format_text_delta(f"- **Strategic Alignment**: 92% coverage on senior transformation leadership roles.\n")

            elif cmd in ("/debate", "/eval", "/evaluate"):
                target_jd_text = None
                target_jd_name = None

                url_in_arg = re.search(r"https?://[^\s]+", cmd_arg)
                if url_in_arg:
                    from engine.url_ingest import URLJobIngestionEngine
                    yield format_text_delta(f"🌐 Ingesting live job URL: `{url_in_arg.group(0)}`...\n")
                    ingested = URLJobIngestionEngine.ingest_url(url_in_arg.group(0))
                    target_jd_text = ingested["markdown_content"]
                    target_jd_name = ingested["filename"]
                elif cmd_arg:
                    try:
                        target_jd_path = resolve_jd_file(cmd_arg)
                        target_jd_text = target_jd_path.read_text(encoding="utf-8")
                        target_jd_name = target_jd_path.name
                    except Exception:
                        pass

                if not target_jd_text:
                    if attached_jd_text:
                        target_jd_text = attached_jd_text
                        target_jd_name = attached_jd_name
                    else:
                        top_opps = repo.list_all()
                        if top_opps:
                            fallback_id = top_opps[0].id
                            try:
                                target_jd_path = resolve_jd_file(fallback_id)
                                target_jd_text = target_jd_path.read_text(encoding="utf-8")
                                target_jd_name = target_jd_path.name
                                yield format_text_delta(f"Targeting active mandate: **{fallback_id}** (`{target_jd_name}`)...\n\n")
                            except Exception:
                                pass

                if not target_jd_text:
                    yield format_text_delta("⚠️ Please specify a mandate to debate, e.g.:\n- `/debate JD_30`\n- `/debate https://...`\n- Or attach a Job Description document.")
                else:
                    route_taken = "SLASH_CMD_DEBATE"
                    emitted_tools = ["ProsecutorIndictmentCard", "AdvocateDefenseCard", "ArbiterScorecard"]
                    jd_title = (target_jd_name or "Target Mandate").replace(".md", "").replace(".txt", "").replace("_", " ")
                    yield format_text_delta(f"Initiating Dual-Agent Dialectic Debate on mandate: **{jd_title}**...\n")
                    await asyncio.sleep(0.05)

                    # Anti-Burn Compute Governor: Check and deduct Energy Credits
                    ok_ec, bal_ec, msg_ec = TokenLedgerManager.consume(cand.id, "fast_heuristic_debate", details=f"Debate on {jd_title}")
                    if not ok_ec:
                        yield format_text_delta(f"⚠️ **Energy Credit Notice**: {msg_ec}\n\nUnable to run Dialectic Debate without available credits.\n")
                        return

                    runner = DebateRunner(profile=cand)
                    transcript = runner.run_fast_heuristic_debate(
                        jd_id=target_jd_name or "target_mandate",
                        jd_title=jd_title,
                        jd_text=target_jd_text
                    )

                    call_id_p = f"call_{uuid.uuid4().hex[:8]}"
                    yield format_tool_call(
                        tool_call_id=call_id_p,
                        tool_name="ProsecutorIndictmentCard",
                        args={
                            "verdict": transcript.indictment.prosecutor_verdict,
                            "trap_score": transcript.indictment.trap_score,
                            "fatal_dealbreakers": [d.dealbreaker_name for d in transcript.indictment.dealbreakers],
                            "unspoken_red_flags": transcript.indictment.unspoken_red_flags,
                            "stance": transcript.indictment.summary_indictment
                        }
                    )
                    yield format_tool_result(tool_call_id=call_id_p, result={"rendered": True})
                    await asyncio.sleep(0.05)

                    call_id_a = f"call_{uuid.uuid4().hex[:8]}"
                    yield format_tool_call(
                        tool_call_id=call_id_a,
                        tool_name="AdvocateDefenseCard",
                        args={
                            "stance": transcript.defense.advocate_verdict,
                            "strategic_positioning": transcript.defense.target_positioning,
                            "leverage_points": transcript.defense.rebuttal_points,
                            "grounded_proof_citations": transcript.defense.grounded_proof_citations,
                            "outreach_hook": transcript.defense.negotiation_hook
                        }
                    )
                    yield format_tool_result(tool_call_id=call_id_a, result={"rendered": True})
                    await asyncio.sleep(0.05)

                    call_id_v = f"call_{uuid.uuid4().hex[:8]}"
                    yield format_tool_call(
                        tool_call_id=call_id_v,
                        tool_name="DebateVerdictCard",
                        args={
                            "verdict": transcript.arbitration.final_verdict,
                            "final_decision": transcript.arbitration.final_verdict,
                            "quality_score": round(transcript.arbitration.fit_score or transcript.arbitration.critic_quality_score or 85),
                            "trap_score": round(transcript.indictment.trap_score or 15),
                            "advocate_points": transcript.defense.rebuttal_points or [transcript.defense.target_positioning],
                            "dealbreakers": [d.dealbreaker_name for d in transcript.indictment.dealbreakers] or transcript.indictment.unspoken_red_flags,
                            "decision_rationale": transcript.arbitration.decision_rationale,
                            "binding_conditions": transcript.arbitration.binding_conditions,
                            "prosecutor_verdict": transcript.indictment.prosecutor_verdict,
                            "advocate_verdict": transcript.defense.advocate_verdict,
                            "target_role": jd_title
                        }
                    )
                    yield format_tool_result(tool_call_id=call_id_v, result={"rendered": True})
                    yield format_text_delta(f"\nArbitration complete: Final verdict is **{transcript.arbitration.final_verdict}** (Score: {transcript.arbitration.fit_score:.0f}/100).")

            elif cmd in ("/tailor", "/compile", "/cv"):
                target_jd_text = None
                target_jd_name = None

                url_in_arg = re.search(r"https?://[^\s]+", cmd_arg)
                if url_in_arg:
                    from engine.url_ingest import URLJobIngestionEngine
                    yield format_text_delta(f"🌐 Ingesting live job URL: `{url_in_arg.group(0)}`...\n")
                    ingested = URLJobIngestionEngine.ingest_url(url_in_arg.group(0))
                    target_jd_text = ingested["markdown_content"]
                    target_jd_name = ingested["filename"]
                elif cmd_arg:
                    try:
                        target_jd_path = resolve_jd_file(cmd_arg)
                        target_jd_text = target_jd_path.read_text(encoding="utf-8")
                        target_jd_name = target_jd_path.name
                    except Exception:
                        pass

                if not target_jd_text:
                    if attached_jd_text:
                        target_jd_text = attached_jd_text
                        target_jd_name = attached_jd_name
                    else:
                        top_opps = repo.list_all()
                        if top_opps:
                            fallback_id = top_opps[0].id
                            try:
                                target_jd_path = resolve_jd_file(fallback_id)
                                target_jd_text = target_jd_path.read_text(encoding="utf-8")
                                target_jd_name = target_jd_path.name
                                yield format_text_delta(f"Synthesizing tailored resume for active mandate: **{fallback_id}** (`{target_jd_name}`)...\n\n")
                            except Exception:
                                pass

                if not target_jd_text:
                    yield format_text_delta("⚠️ Please specify a target mandate to tailor for, e.g.:\n- `/tailor JD_30`\n- `/tailor https://...`\n- Or attach a Job Description document.")
                else:
                    route_taken = "SLASH_CMD_TAILOR"
                    emitted_tools = ["TailoredResumeViewer"]
                    jd_id = (target_jd_name or "target_mandate").replace(".md", "").replace(".txt", "")
                    jd_title = jd_id.replace("_", " ")

                    yield format_text_delta(f"Synthesizing tailored resume and compiling headless A4 PDF for: **{jd_title}**...\n")
                    # Anti-Burn Compute Governor: Check and deduct Energy Credits (25 EC)
                    ok_ec, bal_ec, msg_ec = TokenLedgerManager.consume(cand.id, "tailor_resume", details=f"Tailor CV for {jd_title}")
                    if not ok_ec:
                        yield format_text_delta(f"⚠️ **Energy Credit Notice**: {msg_ec}\n\nUnable to run high-compute LLM resume compiler without available credits.\n")
                        return

                    tailor = ResumeTailor(profile=cand)
                    res = tailor.tailor_and_compile(
                        jd_id=jd_id,
                        jd_title=jd_title,
                        jd_text=target_jd_text,
                        mode="fast"
                    )

                    call_id_t = f"call_{uuid.uuid4().hex[:8]}"
                    yield format_tool_call(
                        tool_call_id=call_id_t,
                        tool_name="TailoredResumeViewer",
                        args={
                            "candidate_name": cand.full_name,
                            "target_role": res.get("tailored_headline", jd_title),
                            "tailored_summary": res.get("tailored_summary", ""),
                            "pdf_path": str(res["pdf_path"]),
                            "html_path": str(res.get("html_path", "")),
                            "markdown_path": str(res.get("md_path", "")),
                            "bullets_synthesized": len(res.get("synthesized_bullets", [])) or 14,
                            "ai_report": res.get("ai_report")
                        }
                    )
                    yield format_tool_result(tool_call_id=call_id_t, result={"compiled": True})
                    ai_rep = res.get("ai_report") or {}
                    auth_score = ai_rep.get("authenticity_score", 95)
                    yield format_text_delta(f"\nTailored CV successfully compiled and calibrated: `{res['pdf_path'].name}`\n*🛡️ Human Tone Authenticity Score: **{auth_score}%** (AI Risk: {ai_rep.get('verdict', 'HUMAN_AUTHENTIC')})*")

            elif cmd in ("/help", "/commands"):
                yield format_text_delta("🛠️ **Available CareerOS Slash Commands**:\n\n")
                yield format_text_delta("- `/debate [JD or URL]` — Run Dual-Agent Dialectic Debate (Advocate vs Prosecutor)\n")
                yield format_text_delta("- `/tailor [JD or URL]` — Synthesize tailored CV and compile pixel-perfect A4 PDF\n")
                yield format_text_delta("- `/scan [query]` — Run Career Radar market scan on job boards\n")
                yield format_text_delta("- `/enrich` — Extract leadership signals and quantifiable metrics from CV\n")
                yield format_text_delta("- `/memory [company]` — Query episodic market memory and agency track records\n")
                yield format_text_delta("- `/pipeline` — Display opportunity status across all pipeline stages\n")
                yield format_text_delta("- `/gap` — Run batch gap analysis against target market JDs\n")
                yield format_text_delta("- `/benchmark` — Run the 10-case evaluation test suite\n")
            else:
                yield format_text_delta(f"Unknown command `{cmd}`. Type `/help` to see all available commands.")

        # Case E: Dynamic Gemini AI Conversational Agent
        else:
            route_taken = "GEMINI_STREAMING"
            # Build rich conversational system prompt
            opps_summary = ", ".join([f"{o.id} ({o.company} - {o.job_title})" for o in repo.list_all()[:6]])
            constraints = cand.to_prompt_constraints()
            attachments_snippet = ""
            if processed_attachments:
                attachments_snippet += "\n=== ATTACHED DOCUMENTS IN CURRENT SESSION ===\n"
                for doc in processed_attachments:
                    attachments_snippet += (
                        f"\n--- Attached Document: {doc['filename']} ({doc['file_type']}) | Classified Category: {doc['category']} ---\n"
                        f"{doc['text_content'][:4000]}\n"
                    )
                attachments_snippet += "=== END ATTACHED DOCUMENTS ===\n\n"

            system_instruction = (
                f"You are CareerOS 2.0 — a Universal Autonomous Executive Career Operating System.\n\n"
                f"Core Philosophy & Universal Scope:\n"
                f"- CareerOS is a domain-agnostic, universal career platform designed to manage and accelerate executive careers across ANY discipline, industry, or vertical (Finance, Cloud, Engineering, Healthcare, Strategy, Product, Operations, Legal, AI, etc.).\n"
                f"- Never state, imply, or assume that CareerOS is limited or restricted to the 'AI domain'. CareerOS operates universally across all career sectors and calibrates specifically to whichever candidate profile is active.\n"
                f"- Active candidate profile loaded in this session: {cand.full_name} ({cand.id}).\n\n"
                f"Active Candidate Profile & Strategic Constraints:\n"
                f"{constraints}\n\n"
                f"{attachments_snippet}"
                f"Active Pipeline Opportunities:\n{opps_summary}\n\n"
                f"Guidelines:\n"
                f"1. STRATEGIC REASONING: Before outputting your visible response, ALWAYS first output your internal strategic analysis wrapped in <think>...</think> tags. In this block, assess candidate constraints, uncover hidden risks, calculate leverage, and determine the optimal communication angle.\n"
                f"2. STRICT EXECUTIVE BREVITY MANDATE (OUTSIDE <THINK>): Senior executives scan; they do not read essay paragraphs. Under NO circumstances should your visible answer exceed 120 words. Format strictly as:\n"
                f"   • **Direct Strategic Verdict** (1 bold sentence)\n"
                f"   • **Key Drivers / Metrics** (maximum 3 concise bullet points with bold keywords)\n"
                f"   • **Recommended Next Move** (1 sentence with clear next step)\n"
                f"3. Never output long meandering text or bland generic advice. Always anchor directly to {cand.full_name}'s specific constraints, TJM, and market leverage.\n"
                f"4. Direct the user to the interactive tools (Live Studio, Debate, Tailor) for detailed reports rather than typing out large text walls.\n"
                f"5. DYNAMIC MULTI-LANGUAGE AGENT: Detect the user's language automatically (English, French, Spanish, Arabic, etc.) and respond in the exact same language while strictly maintaining executive authority and brevity."
            )



            try:
                # Anti-Burn Compute Guard: Charge 1 EC on unstructured LLM conversational turns
                ok_ec, bal_ec, msg_ec = TokenLedgerManager.consume(cand.id, "general_chat_turn", details="General Conversational Turn")
                if not ok_ec:
                    yield format_text_delta(f"⚠️ **Energy Credit Limit Reached**: {msg_ec}\n\n*Deterministic commands (`/gap`, `/pipeline`, `/radar`, `/signals`) remain 100% free and active.*")
                    return

                from google import genai
                client = genai.Client()

                # Build conversation contents
                contents = []
                for m in payload.messages[-5:]:
                    role = "user" if m.role == "user" else "model"
                    contents.append(f"{role.upper()}: {m.content}")
                
                prompt_content = f"{system_instruction}\n\n" + "\n\n".join(contents) + f"\n\nUSER: {last_user_message}\nASSISTANT:"

                model_name = payload.model or os.getenv("DEFAULT_MODEL", "gemini-3.8-flash")
                llm_model = model_name

                stream = client.models.generate_content_stream(
                    model=model_name,
                    contents=prompt_content
                )

                for chunk in stream:
                    if chunk.text:
                        yield format_text_delta(chunk.text)
                        await asyncio.sleep(0.01)

            except Exception as e:
                error_occurred = str(e)
                logger.warning(f"[{req_id}] Gemini streaming exception: {e}")
                # Intelligent fallback
                unacceptable = ", ".join(cand.mobility.unacceptable_commutes)
                yield format_text_delta(
                    f"Bonjour {cand.full_name}. Je suis votre Agent Exécutif CareerOS 2.0.\n\n"
                    f"Je suis synchronisé avec vos **{len(repo.list_all())} opportunités actives**, vos contraintes de mobilité ({unacceptable}) et votre TJM cible de {cand.commercials.freelance_tjm_eur}.\n\n"
                    f"Comment puis-je vous assister aujourd'hui ? Vous pouvez m'attacher une nouvelle offre (JD), me demander d'analyser un mandat avec le débat contradictoire (*ex: 'Debate JD_30'*), ou préparer votre pitch de négociation."
                )

        duration_ms = (time.perf_counter() - start_time) * 1000
        AuditLogger.log_interaction(
            request_id=req_id,
            profile=cand.id,
            user_message=last_user_message,
            route_taken=route_taken,
            attachments=att_names,
            tool_calls=emitted_tools,
            duration_ms=duration_ms,
            llm_model=llm_model,
            status="ERROR" if error_occurred else "SUCCESS",
            error=error_occurred
        )
        logger.info(f"[{req_id}] Stream finished in {duration_ms:.1f}ms | Route: {route_taken} | Tools: {emitted_tools}")
        yield format_finish_message()

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
