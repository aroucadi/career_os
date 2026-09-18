"""
CareerOS Document, Artifact, and Tool Execution Endpoints
==========================================================
Provides real-time HTTP access to:
- Target Job Descriptions list (/api/documents/jds)
- Candidate Profiles list (/api/documents/profiles)
- Rendered HTML Resumes (/api/documents/view-html)
- Compiled A4 PDF Downloads & Previews (/api/documents/download-pdf)
- Direct Tool Execution (/api/documents/run-debate, /api/documents/run-tailor, /api/documents/run-benchmark)
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from engine.profiles.manager import ProfileManager
from engine.prompts.context_assembler import resolve_jd_file
from engine.evaluators.debate.runner import DebateRunner
from engine.compiler.tailor import ResumeTailor
from engine.evaluators.benchmark import BenchmarkRunner

router = APIRouter(prefix="/api/documents", tags=["Documents & Tools"])

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
_TARGET_JDS_DIR = _ROOT_DIR / "07_TARGET_JDS"
_TAILORED_DIR = _ROOT_DIR / "resumes" / "tailored"


@router.get("/jds")
def list_target_jds():
    """Lists all 30 target Job Descriptions with extracted executive metadata."""
    if not _TARGET_JDS_DIR.exists():
        return {"jds": []}

    jds = []
    for f in sorted(_TARGET_JDS_DIR.glob("*.md")):
        text = f.read_text(encoding="utf-8", errors="replace")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        snippet = " ".join(lines[:3])[:200] if lines else "No content"

        # Extract role / company from stem or text
        stem = f.stem
        rate_match = re.search(r"(?:(\d{3,4})\s*(?:€|eur|euros?)(?:\s*/\s*j(?:our)?)?)", text, re.IGNORECASE)
        rate = rate_match.group(0) if rate_match else None

        # Clean title
        parts = stem.split("_")
        jd_code = parts[0] + ("_" + parts[1] if len(parts) > 1 and parts[1].isdigit() else "")
        clean_title = stem.replace(jd_code + "_", "").replace("_", " ")

        jds.append({
            "id": stem,
            "code": jd_code,
            "filename": f.name,
            "title": clean_title,
            "rate": rate,
            "char_count": len(text),
            "snippet": snippet
        })

    return {"jds": jds, "total": len(jds)}


@router.get("/profiles")
def list_profiles():
    """Lists available candidate profiles and their calibration constraints."""
    profiles_dir = _ROOT_DIR / "profiles"
    results = []
    seen_ids = set()
    if profiles_dir.exists():
        for f in profiles_dir.glob("*.json"):
            if f.stem in ("default", "active_profile"):
                continue
            try:
                p = ProfileManager.load_profile(f.stem)
                if p.id not in seen_ids:
                    seen_ids.add(p.id)
                    results.append({
                        "id": p.id,
                        "full_name": p.full_name,
                        "headline": p.headline,
                        "target_tjm": p.commercials.freelance_tjm_eur,
                        "unacceptable_commutes": p.mobility.unacceptable_commutes,
                        "resume_file": p.resume_file
                    })
            except Exception:
                pass
    return {"profiles": results}


@router.get("/view-html", response_class=HTMLResponse)
def view_html_resume(path: str = Query(..., description="Relative or absolute path to HTML file")):
    """Renders a tailored HTML resume directly in the browser for iframe preview."""
    target = Path(path)
    if not target.is_absolute():
        target = _ROOT_DIR / path

    if not target.exists():
        # Search in tailored resumes
        cand = _TAILORED_DIR / target.name
        if cand.exists():
            target = cand
        else:
            raise HTTPException(status_code=404, detail=f"HTML document not found: {path}")

    if target.suffix.lower() != ".html":
        raise HTTPException(status_code=400, detail="File must be an HTML file")

    content = target.read_text(encoding="utf-8", errors="replace")
    return HTMLResponse(content=content, status_code=200, media_type="text/html; charset=utf-8")


@router.get("/download-pdf")
def download_pdf_resume(path: str = Query(..., description="Relative or absolute path to PDF file")):
    """Serves a compiled A4 PDF resume with inline headers for browser viewing and download."""
    target = Path(path)
    if not target.is_absolute():
        target = _ROOT_DIR / path

    if not target.exists():
        cand = _TAILORED_DIR / target.name
        if cand.exists():
            target = cand
        else:
            raise HTTPException(status_code=404, detail=f"PDF file not found: {path}")

    if target.suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF file")

    return FileResponse(
        path=str(target),
        media_type="application/pdf",
        filename=target.name,
        headers={"Content-Disposition": f"inline; filename={target.name}"}
    )


class DebateRequest(BaseModel):
    jd_id: str
    profile: Optional[str] = None


@router.post("/run-debate")
def execute_debate(payload: DebateRequest):
    """Directly triggers the Dialectic Debate Engine on a specific mandate."""
    cand = ProfileManager.load_profile(payload.profile)
    jd_path = resolve_jd_file(payload.jd_id)
    if not jd_path.exists():
        raise HTTPException(status_code=404, detail=f"Mandate not found: {payload.jd_id}")

    jd_text = jd_path.read_text(encoding="utf-8", errors="replace")
    jd_title = jd_path.stem.replace("_", " ")

    runner = DebateRunner(profile=cand)
    transcript = runner.run_fast_heuristic_debate(
        jd_id=jd_path.stem,
        jd_title=jd_title,
        jd_text=jd_text
    )

    return {
        "jd_id": jd_path.stem,
        "jd_title": jd_title,
        "indictment": {
            "verdict": transcript.indictment.prosecutor_verdict,
            "trap_score": transcript.indictment.trap_score,
            "fatal_dealbreakers": [d.dealbreaker_name for d in transcript.indictment.dealbreakers],
            "unspoken_red_flags": transcript.indictment.unspoken_red_flags,
            "summary": transcript.indictment.summary_indictment
        },
        "defense": {
            "verdict": transcript.defense.advocate_verdict,
            "target_positioning": transcript.defense.target_positioning,
            "rebuttal_points": transcript.defense.rebuttal_points,
            "grounded_proof_citations": transcript.defense.grounded_proof_citations,
            "negotiation_hook": transcript.defense.negotiation_hook
        },
        "arbitration": {
            "final_verdict": transcript.arbitration.final_verdict,
            "fit_score": transcript.arbitration.fit_score,
            "critic_quality_score": transcript.arbitration.critic_quality_score,
            "decision_rationale": transcript.arbitration.decision_rationale,
            "binding_conditions": transcript.arbitration.binding_conditions
        }
    }


class TailorRequest(BaseModel):
    jd_id: str
    profile: Optional[str] = None
    mode: Optional[str] = "fast"


@router.post("/run-tailor")
def execute_tailor(payload: TailorRequest):
    """Directly triggers the Ground-Truth Invariant Resume Tailor & Headless A4 PDF Compiler."""
    cand = ProfileManager.load_profile(payload.profile)
    jd_path = resolve_jd_file(payload.jd_id)
    if not jd_path.exists():
        raise HTTPException(status_code=404, detail=f"Mandate not found: {payload.jd_id}")

    jd_text = jd_path.read_text(encoding="utf-8", errors="replace")
    jd_title = jd_path.stem.replace("_", " ")

    tailor = ResumeTailor(profile=cand)
    res = tailor.tailor_and_compile(
        jd_id=jd_path.stem,
        jd_title=jd_title,
        jd_text=jd_text,
        mode=payload.mode or "fast"
    )

    pdf_rel = str(res["pdf_path"])
    html_rel = str(res["html_path"])
    md_rel = str(res["md_path"])

    return {
        "success": res.get("success", True),
        "candidate_name": cand.full_name,
        "jd_id": jd_path.stem,
        "tailored_headline": res.get("tailored_headline"),
        "tailored_summary": res.get("tailored_summary"),
        "pdf_path": pdf_rel,
        "html_path": html_rel,
        "md_path": md_rel,
        "pdf_url": f"/api/documents/download-pdf?path={Path(pdf_rel).name}",
        "html_url": f"/api/documents/view-html?path={Path(html_rel).name}",
        "ai_report": res.get("ai_report")
    }


@router.post("/run-benchmark")
def execute_benchmark():
    """Runs the 10-case evaluation benchmark harness and returns structured telemetry."""
    runner = BenchmarkRunner()
    result = runner.run_fast_heuristic_suite()
    return result


class URLIngestRequest(BaseModel):
    url: str
    profile: Optional[str] = None


@router.post("/ingest-url")
def execute_url_ingestion(payload: URLIngestRequest):
    """Scrapes a job posting from a live URL, structures into Markdown, registers in CRM, and runs debate."""
    from engine.url_ingest import URLJobIngestionEngine
    try:
        ingested = URLJobIngestionEngine.ingest_url(payload.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape and ingest URL: {e}")

    cand = ProfileManager.load_profile(payload.profile)
    runner = DebateRunner(profile=cand)
    transcript = runner.run_fast_heuristic_debate(
        jd_id=ingested["jd_id"],
        jd_title=f"{ingested['company']} - {ingested['title']}",
        jd_text=ingested["markdown_content"]
    )

    return {
        "success": True,
        "jd": ingested,
        "debate": {
            "jd_id": ingested["jd_id"],
            "jd_title": f"{ingested['company']} - {ingested['title']}",
            "indictment": {
                "verdict": transcript.indictment.prosecutor_verdict,
                "trap_score": transcript.indictment.trap_score,
                "fatal_dealbreakers": [d.dealbreaker_name for d in transcript.indictment.dealbreakers],
                "unspoken_red_flags": transcript.indictment.unspoken_red_flags,
                "summary": transcript.indictment.summary_indictment
            },
            "defense": {
                "verdict": transcript.defense.advocate_verdict,
                "target_positioning": transcript.defense.target_positioning,
                "rebuttal_points": transcript.defense.rebuttal_points,
                "grounded_proof_citations": transcript.defense.grounded_proof_citations,
                "negotiation_hook": transcript.defense.negotiation_hook
            },
            "arbitration": {
                "final_verdict": transcript.arbitration.final_verdict,
                "fit_score": transcript.arbitration.fit_score,
                "critic_quality_score": transcript.arbitration.critic_quality_score,
                "decision_rationale": transcript.arbitration.decision_rationale,
                "binding_conditions": transcript.arbitration.binding_conditions
            }
        }
    }

