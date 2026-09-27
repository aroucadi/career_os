"""
Unit and regression test suite for SPEC-0046: Anonymous User Mode.
Verifies that:
1. Anonymous session IDs (anon_...) resolve to clean guest candidate profiles without leaking Alaa Roucadi PII.
2. ProfileManager creates and returns CandidateProfile with guest constraints.
3. Chat API handles anonymous profiles gracefully when no CV is attached vs when CV is attached.
"""

import pytest
import asyncio
from engine.profiles.manager import ProfileManager
from engine.profiles.models import CandidateProfile
from api.routers.chat import handle_chat_stream, ChatPayload, Message, Attachment

def test_profile_manager_anonymous_resolution():
    """Verify that an anon_ ID does not fall back to alaa_roucadi or default profile."""
    anon_id = "anon_9f8e7d6c5b4a3210"
    profile = ProfileManager.load_profile(anon_id)
    
    assert profile is not None
    assert profile.id == anon_id
    assert "Alaa" not in profile.full_name
    assert profile.full_name == "Guest Candidate"
    assert profile.resume_file == ""
    assert profile.contact_email == "guest@careeros.local"

def test_profile_manager_guest_slug():
    """Verify guest slug resolution."""
    profile = ProfileManager.load_profile("guest")
    assert profile.id == "guest"
    assert profile.full_name == "Guest Candidate"

@pytest.mark.asyncio
async def test_anonymous_chat_gap_without_cv():
    """Verify that calling /gap as an anonymous user without a CV prompts for CV ingestion."""
    payload = ChatPayload(
        messages=[Message(role="user", content="/gap Head of AI Delivery")],
        profile="anon_test_user_no_cv",
        career_mode="freelance"
    )
    
    response_stream = await handle_chat_stream(payload)
    output_text = ""
    async for chunk in response_stream.body_iterator:
        output_text += chunk.decode("utf-8") if isinstance(chunk, bytes) else str(chunk)
    
    assert "Resume Needed for Gap Remediation" in output_text
    assert "Import CV" in output_text

@pytest.mark.asyncio
async def test_anonymous_chat_gap_with_attached_cv():
    """Verify that calling /gap as an anonymous user with attached CV runs gap remediation."""
    sample_cv = """# Jane Doe - Senior Agile Coach
10+ years driving Scrum and Kanban across 15 software teams.
Certified Scrum Master (CSM), SAFe Program Consultant (SPC).
Led company-wide agile transformation reducing cycle time by 30%.
Looking to pivot into Enterprise AI Transformation Lead.
"""
    payload = ChatPayload(
        messages=[Message(role="user", content="/gap Enterprise AI Transformation Lead")],
        profile="anon_test_user_with_cv",
        career_mode="pivot",
        attachments=[
            Attachment(
                name="jane_doe_cv.md",
                content=sample_cv,
                type="text/markdown"
            )
        ]
    )
    
    response_stream = await handle_chat_stream(payload)
    output_text = ""
    async for chunk in response_stream.body_iterator:
        output_text += chunk.decode("utf-8") if isinstance(chunk, bytes) else str(chunk)
    
    # Check that GapAnalysisCard was triggered
    assert "GapAnalysisCard" in output_text
    assert "Jane Doe" in output_text or "Candidate" in output_text
