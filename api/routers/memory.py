"""
CareerOS API: Episodic Learning Memory Endpoints
================================================
REST endpoints for tracking recruiter feedback, objections, and company track records.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from engine.memory.store import EpisodicMemoryStore
from engine.memory.models import FeedbackOutcome, ObjectionCategory

router = APIRouter(prefix="/api/memory", tags=["Episodic Memory"])
mem_store = EpisodicMemoryStore()

class FeedbackPayload(BaseModel):
    opportunity_id: str
    company: str
    role_title: str
    outcome: str
    objection_category: Optional[str] = None
    actual_rate_offered_eur: Optional[float] = None
    notes: Optional[str] = ""

@router.get("/records")
def list_memory_records():
    """Returns all historical episodic learning records."""
    records = mem_store.list_all()
    return [r.model_dump() for r in records]

@router.get("/company/{name}")
def get_company_record(name: str):
    """Retrieves track record, average rates, and objections for a specific company."""
    track = mem_store.get_company_track_record(name)
    return track.model_dump()

@router.post("/feedback")
def log_feedback(payload: FeedbackPayload):
    """Ingests market feedback into episodic memory."""
    try:
        outcome_enum = FeedbackOutcome(payload.outcome.upper())
    except ValueError:
        valid_outcomes = [o.value for o in FeedbackOutcome]
        raise HTTPException(status_code=400, detail=f"Invalid outcome. Must be one of: {valid_outcomes}")
    
    obj_enum = None
    if payload.objection_category:
        try:
            obj_enum = ObjectionCategory(payload.objection_category.lower())
        except ValueError:
            pass

    takeaways = [t.strip() for t in payload.notes.split(";") if t.strip()] if payload.notes else []
    rec = mem_store.record_feedback(
        opportunity_id=payload.opportunity_id,
        company=payload.company,
        role_title=payload.role_title,
        outcome=outcome_enum,
        objection_category=obj_enum,
        actual_rate_offered_eur=payload.actual_rate_offered_eur,
        notes=payload.notes or "",
        key_takeaways=takeaways
    )
    return {"status": "success", "record": rec.model_dump()}
