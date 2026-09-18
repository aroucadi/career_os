"""
CareerOS Candidate Inbound Requests & Public Double Opt-In Router
=================================================================
Provides the candidate-facing portal for reviewing inbound headhunter requests
and approving/declining introductions via cryptographic one-time tokens.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel, Field

from engine.storage.db import get_db_connection
from engine.notifications.dispatcher import NotificationDispatcher
from engine.recruiter.models import OptInStatus
from engine.recruiter.matcher import RequisitionMatcher
from engine.recruiter.dossier import ExecutiveDossierCompiler

router = APIRouter(prefix="/api/candidates", tags=["Candidate Inbound Portal"])

class ConsentSubmitPayload(BaseModel):
    token: str = Field(description="Cryptographic one-time consent token (cst_...)")
    decision: str = Field(description="'APPROVE' or 'DECLINE'")

@router.get("/inbound")
async def list_inbound_requests(candidate_id: Optional[str] = Query("cand_6f234c")):
    """Lists all pending and historical recruiter intro requests for this candidate."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT ct.token, ct.match_id, ct.status, ct.expires_at, ct.created_at,
               rm.job_title, rm.overall_score, rm.data_json
        FROM consent_tokens ct
        JOIN recruiter_matches rm ON ct.match_id = rm.match_id
        ORDER BY ct.created_at DESC
        LIMIT 20
        """)
        rows = cursor.fetchall()
        
        inbound = []
        for r in rows:
            data = dict(r)
            inbound.append({
                "token": data["token"],
                "match_id": data["match_id"],
                "status": data["status"],
                "job_title": data["job_title"],
                "match_score": data["overall_score"],
                "expires_at": data["expires_at"],
                "created_at": data["created_at"]
            })
        return inbound

@router.get("/consent-preview")
async def preview_consent_mandate(token: str = Query(...)):
    """Validates cryptographic token and previews requisition details without requiring login."""
    verified = NotificationDispatcher.verify_token(token)
    if not verified:
        raise HTTPException(status_code=400, detail="Invalid or expired consent token.")

    match = RequisitionMatcher.get_match(verified["match_id"])
    if not match:
        raise HTTPException(status_code=404, detail="Match details not found.")

    return {
        "token": token,
        "match_id": match.match_id,
        "job_title": match.headline or "Executive Leadership Mandate",
        "match_score": match.overall_match_score,
        "subscores": match.rubric_subscores,
        "key_leverage_points": match.key_leverage_points,
        "target_compensation": match.target_compensation,
        "governance_tags": match.governance_tags,
        "status": verified["status"],
        "expires_at": verified["expires_at"]
    }

@router.post("/consent-submit")
async def submit_token_consent(payload: ConsentSubmitPayload):
    """Submits candidate approval or decline using one-time signed token."""
    verified = NotificationDispatcher.verify_token(payload.token)
    if not verified:
        raise HTTPException(status_code=400, detail="Invalid, expired, or already used consent token.")

    match_id = verified["match_id"]
    match = RequisitionMatcher.get_match(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Associated match not found.")

    decision_norm = payload.decision.strip().upper()
    new_status = "APPROVED" if decision_norm in ("APPROVE", "CONSENT", "ACCEPT") else "DECLINED"

    with get_db_connection() as conn:
        conn.execute("UPDATE consent_tokens SET status = ? WHERE token = ?", (new_status, payload.token))
        conn.execute("UPDATE recruiter_matches SET opt_in_status = ? WHERE match_id = ?", (new_status, match_id))

    if new_status == "APPROVED":
        RequisitionMatcher.update_status(match_id, OptInStatus.APPROVED)
        dossier = ExecutiveDossierCompiler.compile_dossier(match)
        return {
            "status": "APPROVED",
            "decision": "APPROVE",
            "match_id": match_id,
            "message": "Introduction approved. Contact information unlocked for the hiring enterprise.",
            "dossier": dossier
        }
    else:
        RequisitionMatcher.update_status(match_id, OptInStatus.DECLINED)
        return {
            "status": "DECLINED",
            "decision": "DECLINE",
            "match_id": match_id,
            "message": "Introduction declined. Your profile remains permanently locked."
        }

from fastapi import UploadFile, File, Form
from engine.profiles.extractor import ResumeExtractor

class ResumeTextPayload(BaseModel):
    text: str = Field(description="Raw text content of the candidate resume")
    filename: Optional[str] = "pasted_cv.txt"
    preferred_mode: Optional[str] = "freelance"

@router.post("/upload-cv")
async def upload_candidate_cv(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    preferred_mode: Optional[str] = Form("freelance")
):
    """
    Ingests and parses a candidate resume (.pdf, .docx, or plain text),
    constructs a verified CandidateProfile, and saves to SQLite talent_profiles.
    """
    if file:
        file_bytes = await file.read()
        text = ResumeExtractor.extract_text_from_bytes(file.filename or "uploaded_cv.pdf", file_bytes)
        filename = file.filename or "uploaded_cv.pdf"
    elif raw_text and raw_text.strip():
        text = raw_text.strip()
        filename = "pasted_resume.txt"
    else:
        raise HTTPException(status_code=400, detail="Either a file upload or raw_text is required.")

    profile = ResumeExtractor.ingest_and_save(
        text=text,
        filename=filename,
        preferred_mode=preferred_mode or "freelance"
    )

    return {
        "status": "SUCCESS",
        "profile_id": profile.id,
        "full_name": profile.full_name,
        "headline": profile.headline,
        "email": profile.contact_email,
        "primary_titles": profile.scope.primary_titles,
        "proof_metrics_count": len(profile.proof_metrics),
        "message": f"Profile '{profile.full_name}' successfully parsed and activated."
    }

@router.post("/upload-cv-json")
async def upload_candidate_cv_json(payload: ResumeTextPayload):
    """Ingests raw CV text via standard JSON payload."""
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")
    profile = ResumeExtractor.ingest_and_save(
        text=payload.text,
        filename=payload.filename or "pasted_cv.txt",
        preferred_mode=payload.preferred_mode or "freelance"
    )
    return {
        "status": "SUCCESS",
        "profile_id": profile.id,
        "full_name": profile.full_name,
        "headline": profile.headline,
        "email": profile.contact_email,
        "primary_titles": profile.scope.primary_titles,
        "proof_metrics_count": len(profile.proof_metrics),
        "message": f"Profile '{profile.full_name}' successfully parsed and activated."
    }

