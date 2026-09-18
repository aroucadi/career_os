"""
CareerOS Talent Intelligence Lake & Anonymization Tests
======================================================
Verifies GDPR-compliant anonymization, PII stripping,
governance tagging, and talent lake storage.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from engine.profiles.manager import ProfileManager
from engine.talent_graph.models import TalentGraphProfile, ReadinessStatus
from engine.talent_graph.store import TalentLakeStore

client = TestClient(app)

@pytest.fixture
def sample_candidate():
    return ProfileManager.load_profile("alaa_roucadi")

def test_anonymized_profile_conversion(sample_candidate):
    anon = TalentGraphProfile.from_candidate_profile(sample_candidate, verified_score=92.0, last_jd="Head of AI Adoption")

    # Verify PII Stripping
    assert sample_candidate.full_name not in anon.anonymized_alias
    assert sample_candidate.full_name not in anon.headline
    assert "@" not in str(anon.model_dump())  # Zero email addresses leaked
    assert "Candidate #" in anon.anonymized_alias

    # Verify Hard Competencies & Governance Tags
    assert len(anon.governance_tags) > 0
    assert any("EU AI Act" in t or "Banking" in t or "Architecture" in t for t in anon.governance_tags)
    assert anon.readiness_status == ReadinessStatus.ACTIVE_VERIFIED
    assert anon.verified_composite_score == 92.0
    assert anon.last_evaluated_jd == "Head of AI Adoption"

def test_talent_lake_store_operations(sample_candidate):
    anon = TalentLakeStore.index_candidate(sample_candidate, verified_score=90.0, last_jd="Lead Cloud Architect")
    
    # Retrieval
    retrieved = TalentLakeStore.get_profile(anon.profile_id)
    assert retrieved is not None
    assert retrieved.profile_id == anon.profile_id
    assert retrieved.anonymized_alias == anon.anonymized_alias

    # Filtering by governance tag
    all_profiles = TalentLakeStore.list_profiles()
    assert len(all_profiles) >= 1
    
    filtered = TalentLakeStore.list_profiles(governance_tag="AI")
    assert len(filtered) >= 1

def test_api_talent_lake_endpoint(sample_candidate):
    TalentLakeStore.index_candidate(sample_candidate, verified_score=88.0)
    response = client.get("/api/tokens/talent-lake")
    assert response.status_code == 200
    profiles = response.json()
    assert isinstance(profiles, list)
    assert len(profiles) >= 1
    first = profiles[0]
    assert "anonymized_alias" in first
    assert "governance_tags" in first
    assert "verified_proof_metrics" in first
    # Guarantee no PII in API output
    assert sample_candidate.full_name not in str(first)
