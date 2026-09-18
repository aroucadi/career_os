"""
CareerOS Opportunity Lifecycle & Multi-Persona Pipeline Engine
"""
from .models import PipelineStage, Opportunity, HistoryEvent, MultiPersonaIntel, EvaluationSnapshot
from .state_machine import PipelineStateMachine, TransitionError
from .repository import PipelineRepository
from .views import render_pipeline_table, render_persona_view
