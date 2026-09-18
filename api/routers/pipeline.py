"""
CareerOS API: Pipeline CRM Endpoints
====================================
REST endpoints for managing opportunities, viewing persona briefings,
and advancing lifecycle states.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from engine.pipeline.repository import PipelineRepository
from engine.pipeline.state_machine import PipelineStateMachine, TransitionError
from engine.pipeline.models import PipelineStage, Opportunity
from engine.profiles.manager import ProfileManager

router = APIRouter(prefix="/api/pipeline", tags=["Pipeline"])
repo = PipelineRepository()

class TransitionRequest(BaseModel):
    target_stage: str
    notes: Optional[str] = ""
    actor: Optional[str] = "api_user"

@router.get("/opportunities", response_model=List[dict])
def list_opportunities(stage: Optional[str] = Query(None, description="Filter by stage")):
    """Returns all opportunities in the CareerOS pipeline."""
    opps = repo.list_all(stage_filter=stage)
    return [o.model_dump() for o in opps]

@router.get("/opportunities/{opp_id}")
def get_opportunity(opp_id: str, profile: Optional[str] = None):
    """Retrieves an opportunity with dynamic candidate persona briefings."""
    opp = repo.get(opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail=f"Opportunity '{opp_id}' not found")
    
    cand = ProfileManager.load_profile(profile)
    return {
        "opportunity": opp.model_dump(),
        "candidate": {
            "id": cand.id,
            "name": cand.full_name,
            "headline": cand.headline
        }
    }

@router.post("/opportunities/{opp_id}/advance")
def advance_opportunity(opp_id: str, payload: TransitionRequest):
    """Transitions an opportunity to a new lifecycle stage via the state machine."""
    opp = repo.get(opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail=f"Opportunity '{opp_id}' not found")
    
    try:
        stage_enum = PipelineStage(payload.target_stage.upper())
    except ValueError:
        valid_stages = [s.value for s in PipelineStage]
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of: {valid_stages}")
    
    try:
        PipelineStateMachine.transition(opp, stage_enum, notes=payload.notes or "", actor=payload.actor or "api")
        repo.save(opp)
        return {"status": "success", "new_stage": opp.stage.value, "history_events": len(opp.history)}
    except TransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
