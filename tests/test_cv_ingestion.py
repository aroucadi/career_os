"""
CareerOS Candidate Self-Serve Ingestion Test Suite
===================================================
Verifies the Release 2.2 self-serve onboarding engine (SPEC-0045):
1. Resume text heuristic parsing into structured CandidateProfile.
2. Persistence into profiles/{slug}.json and active_profile.json.
3. Indexing into SQLite talent_profiles table with governance tags.
4. REST API endpoints /api/candidates/upload-cv and /api/candidates/upload-cv-json.
"""

import io
import pytest
from fastapi.testclient import TestClient
from api.main import app
from engine.profiles.extractor import ResumeExtractor
from engine.storage.db import get_db_connection

client = TestClient(app)

SAMPLE_CV_TEXT = """
Jean-Luc Picard
Senior AI Transformation Director & Enterprise Delivery Lead
jean-luc.picard@starfleet.org | +33 6 98 76 54 32 | Paris, France
LinkedIn: https://linkedin.com/in/jeanluc-picard

SUMMARY
Executive leader with 15+ years delivering mission-critical AI operating models, multi-squad agile transformations,
and high-concurrency cloud architectures.

KEY METRICS & SCALE
- Led 8 engineering squads and 60+ engineers delivering generative AI copilot systems.
- Supervised €45M operating budget with 99.99% system availability.
- Established enterprise EU AI Act & Responsible AI risk compliance framework across European banking units.

COMMERCIALS
Target Freelance TJM: 1100 €/jour
Target Permanent Salary: 140k EUR
"""

def test_resume_extractor_parsing():
    """Verifies heuristic telemetry extraction from plain text."""
    profile = ResumeExtractor.parse_profile_from_text(SAMPLE_CV_TEXT, preferred_mode="freelance")
    
    assert profile.full_name == "Jean-Luc Picard"
    assert "jean-luc.picard@starfleet.org" in profile.contact_email
    assert "Paris" in profile.mobility.base_location
    assert "1100 EUR / day" in profile.commercials.freelance_tjm_eur
    assert any("EU AI Act" in p.evidence for p in profile.proof_metrics)

def test_resume_ingest_and_sqlite_indexing():
    """Verifies profile is saved to disk and indexed into SQLite talent_profiles."""
    profile = ResumeExtractor.ingest_and_save(SAMPLE_CV_TEXT, preferred_mode="freelance")
    
    assert profile.id.startswith("jean_luc_picard")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT profile_id, headline, readiness_status FROM talent_profiles WHERE profile_id = ?", (profile.id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["readiness_status"] == "ACTIVE_VERIFIED"

def test_upload_cv_json_endpoint():
    """Verifies candidate upload via JSON REST endpoint."""
    res = client.post("/api/candidates/upload-cv-json", json={
        "text": SAMPLE_CV_TEXT,
        "filename": "picard_resume.txt",
        "preferred_mode": "employee"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["full_name"] == "Jean-Luc Picard"
    assert data["proof_metrics_count"] >= 1

def test_upload_cv_multipart_endpoint():
    """Verifies candidate file upload via multipart form-data."""
    file_content = SAMPLE_CV_TEXT.encode("utf-8")
    files = {"file": ("test_resume.txt", io.BytesIO(file_content), "text/plain")}
    data = {"preferred_mode": "fractional"}

    res = client.post("/api/candidates/upload-cv", files=files, data=data)
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["status"] == "SUCCESS"
    assert res_json["full_name"] == "Jean-Luc Picard"
