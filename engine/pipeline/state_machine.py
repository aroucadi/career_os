"""
Pipeline State Machine
======================
Enforces deterministic lifecycle transitions, validates business rules,
and logs immutable audit events.
"""

from typing import Dict, Set, Optional, List
from .models import PipelineStage, Opportunity, HistoryEvent


class TransitionError(Exception):
    """Raised when an illegal stage transition is attempted."""
    pass


# Valid forward and sideways transitions
VALID_TRANSITIONS: Dict[PipelineStage, Set[PipelineStage]] = {
    PipelineStage.DISCOVERED: {
        PipelineStage.QUALIFIED,
        PipelineStage.REJECTED,
        PipelineStage.ARCHIVED
    },
    PipelineStage.QUALIFIED: {
        PipelineStage.PITCH_READY,
        PipelineStage.APPLIED,
        PipelineStage.REJECTED,
        PipelineStage.ARCHIVED
    },
    PipelineStage.PITCH_READY: {
        PipelineStage.APPLIED,
        PipelineStage.REJECTED,
        PipelineStage.ARCHIVED
    },
    PipelineStage.APPLIED: {
        PipelineStage.SCREENING_SCHEDULED,
        PipelineStage.INTERVIEWING,
        PipelineStage.REJECTED,
        PipelineStage.ARCHIVED
    },
    PipelineStage.SCREENING_SCHEDULED: {
        PipelineStage.INTERVIEWING,
        PipelineStage.REJECTED,
        PipelineStage.ARCHIVED
    },
    PipelineStage.INTERVIEWING: {
        PipelineStage.OFFER_EXTENDED,
        PipelineStage.REJECTED,
        PipelineStage.ARCHIVED
    },
    PipelineStage.OFFER_EXTENDED: {
        PipelineStage.NEGOTIATING,
        PipelineStage.ACCEPTED,
        PipelineStage.REJECTED,
        PipelineStage.ARCHIVED
    },
    PipelineStage.NEGOTIATING: {
        PipelineStage.ACCEPTED,
        PipelineStage.REJECTED,
        PipelineStage.ARCHIVED
    },
    PipelineStage.ACCEPTED: {
        PipelineStage.ARCHIVED
    },
    PipelineStage.REJECTED: {
        PipelineStage.ARCHIVED,
        PipelineStage.QUALIFIED  # Can be re-opened upon renegotiation
    },
    PipelineStage.ARCHIVED: {
        PipelineStage.DISCOVERED,
        PipelineStage.QUALIFIED
    },
}


class PipelineStateMachine:
    """Manages stage transitions and ensures audit trails."""

    @staticmethod
    def can_transition(current_stage: PipelineStage, target_stage: PipelineStage) -> bool:
        if current_stage == target_stage:
            return True
        allowed = VALID_TRANSITIONS.get(current_stage, set())
        return target_stage in allowed

    @classmethod
    def transition(
        cls,
        opportunity: Opportunity,
        target_stage: PipelineStage,
        notes: str = "",
        actor: str = "user",
        follow_up_date: Optional[str] = None,
        force: bool = False
    ) -> Opportunity:
        """Transitions an opportunity to a new lifecycle stage."""
        from datetime import datetime

        if not force and not cls.can_transition(opportunity.stage, target_stage):
            raise TransitionError(
                f"Invalid transition from '{opportunity.stage.value}' to '{target_stage.value}'. "
                f"Allowed target stages: {[s.value for s in VALID_TRANSITIONS.get(opportunity.stage, set())]}"
            )

        event = HistoryEvent(
            from_stage=opportunity.stage,
            to_stage=target_stage,
            actor=actor,
            notes=notes,
            follow_up_date=follow_up_date
        )

        opportunity.history.append(event)
        opportunity.stage = target_stage
        opportunity.last_updated_at = datetime.now().isoformat()
        if follow_up_date:
            opportunity.next_follow_up = follow_up_date

        return opportunity
