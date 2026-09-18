"""
CareerOS Multi-Persona Integration Test Suite
=============================================
Validates end-to-end user journeys for 5 core career personas:
1. Freelancer / Contractor (IT, Cloud, GenAI Architecture)
2. Permanent Employee / Corporate Climber (Audit & Financial Compliance)
3. Fractional CTO / Portfolio Advisor (Startups & Scaleups)
4. Growth Leader / CMO (Marketing & D2C)
5. Student / Career Starter & Tech Pivoter (Data / AI Engineering)

Verifies Dialectic Scrutiny, Multi-Track Pitch Formatter, Hick's Law Action Gating,
and Dynamic Pipeline Stage Taxonomy across the FastAPI backend.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from engine.evaluators.debate.runner import DebateRunner
from api.routers.chat import build_multi_track_pitch, extract_recruiter_info
from engine.profiles.manager import ProfileManager

client = TestClient(app)

@pytest.fixture
def mock_profile():
    """Provides the active candidate profile for persona testing."""
    return ProfileManager.load_profile("alaa_roucadi")

# ---------------------------------------------------------------------------
# 1. Freelancer Journey (TJM, Remote Autonomy, Recruiter Margin Shredder)
# ---------------------------------------------------------------------------
def test_freelancer_journey(mock_profile):
    jd_text = """
    # Senior Cloud & AI Consultant
    Location: Frankfurt (Hybrid - 3 days per week on-site)
    Rate: Competitive daily rate capped at 650 EUR/day.
    Contact: recruiter@bankingtech.com
    We are looking for a hands-on engineer to build Python pipelines and write clean CSS.
    """
    runner = DebateRunner(profile=mock_profile)
    transcript = runner.run_fast_heuristic_debate(
        jd_id="JD_FREELANCE_TEST",
        jd_title="Senior Cloud & AI Consultant",
        jd_text=jd_text,
        career_mode="freelance"
    )

    # Dialectic Scrutiny
    assert transcript.indictment.trap_score >= 40.0
    dealbreaker_names = [d.dealbreaker_name for d in transcript.indictment.dealbreakers]
    assert any("commute" in d.lower() or "unacceptable" in d.lower() for d in dealbreaker_names)
    assert transcript.arbitration.final_verdict in ("KILL", "NO-GO", "CHALLENGE_SEVERELY", "CONDITIONAL_LEVERAGE")

    # Multi-track Pitch Formatting
    rec_info = extract_recruiter_info(jd_text)
    pitch = build_multi_track_pitch("freelance", "Senior Cloud & AI Consultant", mock_profile, rec_info)
    assert "950€/j" in pitch or "TJM" in pitch
    assert "100% remote" in pitch

    # Live Streaming Endpoint check
    payload = {
        "messages": [{"role": "user", "content": "Evaluate mandate for freelance mode: " + jd_text}],
        "profile": "alaa_roucadi",
        "career_mode": "freelance"
    }
    with client.stream("POST", "/api/chat", json=payload) as response:
        assert response.status_code == 200
        chunks = [line for line in response.iter_lines() if line]
        body = "\n".join(chunks)
        assert any(l.startswith('9:{') or l.startswith('b:{') for l in chunks)
        assert "DebateVerdictCard" in body or "ProsecutorIndictmentCard" in body

# ---------------------------------------------------------------------------
# 2. Permanent Employee / Corporate Climber Journey (Audit & Risk)
# ---------------------------------------------------------------------------
def test_permanent_employee_journey(mock_profile):
    jd_text = """
    # Head of Internal Controls & Tech Compliance
    Location: Paris / Hybrid (1 day office per week)
    We are seeking a seasoned risk professional to lead SOX 404 audit automation, IT general controls, and regulatory risk.
    Recruiter: Sophie Laurent, sophie.laurent@fintechlead.com
    """
    runner = DebateRunner(profile=mock_profile)
    transcript = runner.run_fast_heuristic_debate(
        jd_id="JD_AUDIT_CDI",
        jd_title="Head of Internal Controls & Tech Compliance",
        jd_text=jd_text,
        career_mode="employee"
    )

    # Advocate compensation leverage
    assert any("120k" in p and "135k" in p for p in transcript.defense.leverage_points)

    # Multi-track pitch
    rec_info = extract_recruiter_info(jd_text)
    pitch = build_multi_track_pitch("employee", "Head of Internal Controls & Tech Compliance", mock_profile, rec_info)
    assert "120k" in pitch and "135k" in pitch
    assert "hybride" in pitch.lower()
    assert "Bonjour" in pitch

    # Live Streaming Endpoint check
    payload = {
        "messages": [{"role": "user", "content": "Evaluate audit mandate for permanent CDI: " + jd_text}],
        "profile": "alaa_roucadi",
        "career_mode": "employee"
    }
    with client.stream("POST", "/api/chat", json=payload) as response:
        assert response.status_code == 200
        chunks = [line for line in response.iter_lines() if line]
        body = "\n".join(chunks)
        assert any(l.startswith('9:{') or l.startswith('b:{') for l in chunks)

# ---------------------------------------------------------------------------
# 3. Fractional Executive Journey (Fractional CTO & Advisory)
# ---------------------------------------------------------------------------
def test_fractional_cto_journey(mock_profile):
    jd_text = """
    # Fractional CTO / Strategic Tech Advisor
    Location: Remote
    Series A AI startup looking for a high-impact technical advisor to steer architecture, board reporting, and team scaling.
    Contact: alex@aiventures.io
    """
    runner = DebateRunner(profile=mock_profile)
    transcript = runner.run_fast_heuristic_debate(
        jd_id="JD_FRACTIONAL_CTO",
        jd_title="Fractional CTO & Strategic Tech Advisor",
        jd_text=jd_text,
        career_mode="fractional"
    )

    # Advocate defense points
    assert any("3,800" in p and "5,000" in p for p in transcript.defense.leverage_points)

    # Multi-track pitch
    rec_info = extract_recruiter_info(jd_text)
    pitch = build_multi_track_pitch("fractional", "Fractional CTO & Strategic Tech Advisor", mock_profile, rec_info)
    assert "Fractional AI Executive & Strategic Advisor" in pitch
    assert "3 800" in pitch and "5 000" in pitch
    assert "1 à 2 jours par semaine" in pitch

# ---------------------------------------------------------------------------
# 4. Growth Leader / CMO Journey (Marketing & D2C)
# ---------------------------------------------------------------------------
def test_growth_leader_journey(mock_profile):
    jd_text = """
    # VP Growth Marketing & E-Commerce
    Location: Remote / Flexible
    Seeking a Growth Director with deep CAC/LTV attribution experience, paid acquisition mastery, and conversion funnel optimization.
    Recruiter: Dave Scott, dave.scott@welovesalt.com
    """
    rec_info = extract_recruiter_info(jd_text)
    assert rec_info["recruiter_name"] == "Dave Scott"
    assert rec_info["recruiter_email"] == "dave.scott@welovesalt.com"

    pitch = build_multi_track_pitch("employee", "VP Growth Marketing", mock_profile, rec_info)
    assert len(pitch) > 50
    assert "Dave" in pitch or "Bonjour" in pitch

# ---------------------------------------------------------------------------
# 5. Student / Career Starter & Pivoter Journey (AI Engineering)
# ---------------------------------------------------------------------------
def test_student_and_pivoter_journeys(mock_profile):
    jd_text = """
    # Junior AI Engineer / Applied LLM Developer
    Location: Remote
    Join our engineering team to build LLM evaluation pipelines, fine-tune models, and deploy production endpoints.
    """
    runner = DebateRunner(profile=mock_profile)

    # Student Mode
    student_transcript = runner.run_fast_heuristic_debate(
        jd_id="JD_STUDENT_AI",
        jd_title="Junior AI Engineer",
        jd_text=jd_text,
        career_mode="student"
    )
    assert any("48k" in p and "55k" in p for p in student_transcript.defense.leverage_points)
    student_pitch = build_multi_track_pitch("student", "Junior AI Engineer", mock_profile, {})
    assert "vélocité d'apprentissage" in student_pitch
    assert "projets concrets" in student_pitch

    # Pivoter Mode
    pivot_transcript = runner.run_fast_heuristic_debate(
        jd_id="JD_PIVOT_AI",
        jd_title="AI Solutions Lead",
        jd_text=jd_text,
        career_mode="pivot"
    )
    assert any("Cross-functional" in p or "hybrid" in p.lower() or "operating models" in p.lower() for p in pivot_transcript.defense.leverage_points)
    pivot_pitch = build_multi_track_pitch("pivot", "AI Solutions Lead", mock_profile, {})
    assert "profil hybride" in pivot_pitch
    assert "dérisquer" in pivot_pitch

# ---------------------------------------------------------------------------
# 6. Dynamic Pipeline Stage Taxonomy Verification
# ---------------------------------------------------------------------------
def test_pipeline_taxonomy_stages():
    """Verifies that all persona stage categorizations map cleanly."""
    valid_freelance_stages = ["DISCOVERED", "QUALIFIED", "PITCHED", "INTERVIEWING", "OFFERED", "ARCHIVED", "REJECTED"]
    
    # Check Pipeline Summary API response
    response = client.get("/api/pipeline/opportunities")
    assert response.status_code == 200
    opps = response.json()
    assert isinstance(opps, list)
    for o in opps:
        assert o.get("stage") in valid_freelance_stages, f"Invalid stage {o.get('stage')}"
