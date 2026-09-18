"""
CareerOS Recruiter Delegation & Double Opt-In API Router
========================================================
Exposes requisition matching, candidate slate ranking,
double opt-in candidate consent, and executive dossier unlocking.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from engine.recruiter.models import (
    CandidateMatchSlateItem,
    ExecutiveDossier,
    OptInStatus,
    RequisitionSpec
)
from engine.recruiter.matcher import RequisitionMatcher
from engine.recruiter.dossier import ExecutiveDossierCompiler
from engine.agents.recruiter_agent import RecruiterAutonomousAgent

router = APIRouter(prefix="/api/recruiter", tags=["Recruiter Delegation"])
candidate_router = APIRouter(prefix="/api/candidates", tags=["Candidate Portal"])

class RecruiterAgentSourcingRequest(BaseModel):
    brief: str = Field(description="Natural language hiring brief, requirements, or JD")
    org_id: Optional[str] = Field(default="org_default_test")
    api_key: Optional[str] = Field(default="cr_live_test123")
    auto_dispatch_top: Optional[bool] = Field(default=False)

@router.post("/agent/source")
async def stream_recruiter_sourcing_agent(payload: RecruiterAgentSourcingRequest):
    """
    S-Tier Autonomous Recruiter Agent:
    Decomposes natural language brief, searches talent lake via 768-dim embeddings,
    generates candidate match slate, synthesizes tailored tactical interview cheatsheets,
    and optionally initiates cryptographic double opt-in.
    Streams Vercel AI SDK SSE protocol.
    """
    if not payload.brief or not payload.brief.strip():
        raise HTTPException(status_code=400, detail="A non-empty hiring brief is required.")

    agent = RecruiterAutonomousAgent(
        org_id=payload.org_id or "org_default_test",
        api_key=payload.api_key or "cr_live_test123"
    )

    return StreamingResponse(
        agent.execute_sourcing_stream(
            brief=payload.brief,
            auto_dispatch_top=bool(payload.auto_dispatch_top)
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

class RequisitionMatchRequest(BaseModel):
    job_title: str = Field(description="Title of requisition, e.g. 'Head of AI Adoption'")
    jd_text: str = Field(description="Full text or scraped body of the job description")
    company: Optional[str] = Field(default="Hiring Enterprise", description="Client name")
    min_score: Optional[float] = Field(default=60.0, description="Minimum overall match threshold")

class RequestIntroPayload(BaseModel):
    match_id: str
    recruiter_notes: Optional[str] = None

class CandidateConsentPayload(BaseModel):
    match_id: str
    decision: str = Field(description="'APPROVE' to consent and unlock dossier, or 'DECLINE'")

@router.post("/match", response_model=List[CandidateMatchSlateItem])
async def match_requisition(payload: RequisitionMatchRequest):
    """
    Submits a recruiter job requisition and returns a ranked slate of candidates
    scored against domain fit, governance, scale, and compensation bounds.
    """
    if not payload.job_title or not payload.jd_text:
        raise HTTPException(status_code=400, detail="Both 'job_title' and 'jd_text' are required.")
    
    slate = RequisitionMatcher.match_requisition(
        job_title=payload.job_title,
        jd_text=payload.jd_text,
        company=payload.company or "Hiring Enterprise",
        min_score=payload.min_score or 60.0
    )
    return slate

@router.post("/request-intro")
async def request_candidate_introduction(payload: RequestIntroPayload):
    """
    Recruiter requests warm double opt-in introduction to a matched candidate.
    Dispatches a notification to the candidate while preserving candidate privacy.
    """
    match = RequisitionMatcher.get_match(payload.match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match transaction not found.")
    
    match.opt_in_status = OptInStatus.PENDING_CONSENT
    RequisitionMatcher.update_status(payload.match_id, OptInStatus.PENDING_CONSENT)
    
    # Dispatch real-time Double Opt-In alert via NotificationDispatcher
    from engine.notifications.dispatcher import NotificationDispatcher
    dispatch_res = NotificationDispatcher.dispatch_intro_request(
        candidate_alias=match.anonymized_alias,
        candidate_id=match.candidate_id,
        match_data=match.model_dump(),
        recruiter_notes=payload.recruiter_notes
    )

    return {
        "status": "INTRODUCTION_REQUESTED",
        "match_id": payload.match_id,
        "anonymized_alias": match.anonymized_alias,
        "token": dispatch_res.get("token"),
        "consent_url": dispatch_res.get("consent_url"),
        "message": f"Introduction request dispatched to {match.anonymized_alias}. Awaiting Double Opt-In candidate consent."
    }

@router.post("/billing/checkout")
async def create_recruiter_checkout(org_id: str = Query("org_default_test"), pack: str = Query("starter")):
    """Generates a billing checkout session stub for headhunters."""
    from engine.billing.recruiter_billing import RecruiterBillingManager
    return RecruiterBillingManager.create_checkout_session(org_id=org_id, pack=pack)

@router.get("/billing/balance")
async def get_recruiter_balance(api_key: str = Query("cr_live_test123")):
    """Returns organization credit balance."""
    from engine.billing.recruiter_billing import RecruiterBillingManager
    org = RecruiterBillingManager.authenticate_key(api_key)
    if not org:
        raise HTTPException(status_code=401, detail="Invalid API Key.")
    return {
        "org_id": org["org_id"],
        "name": org["name"],
        "credits_balance": org["credits_balance"],
        "tier": org["tier"]
    }

class StripeWebhookPayload(BaseModel):
    event: str = Field(default="checkout.session.completed", description="Stripe event type")
    org_id: str = Field(default="org_default_test")
    credits_added: int = Field(default=50, ge=1)
    customer_email: Optional[str] = None
    session_id: Optional[str] = None

@router.post("/billing/webhook")
async def stripe_billing_webhook(payload: StripeWebhookPayload):
    """
    Fulfills recruiter organization credit top-ups automatically upon Stripe webhook confirmation.
    """
    from engine.storage.db import get_db_connection
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT credits_balance, name FROM recruiter_orgs WHERE org_id = ?", (payload.org_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Recruiter organization '{payload.org_id}' not found.")

        new_bal = row["credits_balance"] + payload.credits_added
        conn.execute("UPDATE recruiter_orgs SET credits_balance = ? WHERE org_id = ?", (new_bal, payload.org_id))

    return {
        "status": "FULFILLED",
        "event": payload.event,
        "org_id": payload.org_id,
        "credits_added": payload.credits_added,
        "new_balance": new_bal,
        "message": f"Successfully credited {payload.credits_added} credits to {row['name']}."
    }

@candidate_router.post("/opt-in")
@router.post("/opt-in")
async def candidate_consent_decision(payload: CandidateConsentPayload):
    """
    Candidate grants or declines consent for a recruiter introduction.
    Only upon 'APPROVE' is the Executive Dossier with PII unlocked.
    """
    match = RequisitionMatcher.get_match(payload.match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match transaction not found.")

    decision_norm = payload.decision.strip().upper()
    if decision_norm in ("APPROVE", "CONSENT", "ACCEPT"):
        RequisitionMatcher.update_status(payload.match_id, OptInStatus.APPROVED)
        dossier = ExecutiveDossierCompiler.compile_dossier(match)
        return {
            "status": "APPROVED",
            "match_id": payload.match_id,
            "message": "Candidate consented! Executive Dossier and direct contact telemetry are now UNLOCKED for the recruiter.",
            "dossier": dossier
        }
    else:
        RequisitionMatcher.update_status(payload.match_id, OptInStatus.DECLINED)
        return {
            "status": "DECLINED",
            "match_id": payload.match_id,
            "message": "Candidate declined the introduction. Profile PII remains strictly locked."
        }

@router.get("/dossier/{match_id}", response_model=ExecutiveDossier)
async def get_executive_dossier(match_id: str):
    """
    Retrieves the Executive Dossier for a match.
    If the candidate has not consented, contact details are omitted and access_status is 'LOCKED'.
    """
    match = RequisitionMatcher.get_match(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match transaction not found.")
    
    return ExecutiveDossierCompiler.compile_dossier(match)

@router.get("/matches", response_model=List[CandidateMatchSlateItem])
async def list_recent_matches():
    """Lists all stored candidate match transactions."""
    RequisitionMatcher._ensure_loaded()
    with RequisitionMatcher._matcher_lock:
        return list(RequisitionMatcher._matches.values())
