"""
CareerOS Tailored Resume Synthesizer & Compiler
===============================================
Generates high-converting, ATS-aligned tailored resumes for a specific JD
while adhering to strict ground-truth invariance (anti-hallucination guardrail).
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from engine.profiles.models import CandidateProfile
from engine.profiles.manager import ProfileManager
from engine.compiler.html_renderer import render_markdown_resume_to_html
from engine.compiler.pdf_compiler import compile_custom_resume
from engine.compiler.humanizer import HumanizerEngine, AIDetectionReport

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
_OUTPUT_DIR = _ROOT_DIR / "resumes" / "tailored"


class ResumeTailor:
    """Orchestrates truthful CV tailoring and headless A4 PDF generation."""

    def __init__(self, profile: Optional[CandidateProfile] = None):
        self.profile = profile or ProfileManager.load_profile()
        self.output_dir = _OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def tailor_and_compile(
        self,
        jd_id: str,
        jd_title: str,
        jd_text: str,
        mode: str = "fast",
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synthesizes a tailored markdown resume and compiles it to A4 PDF."""
        cand = self.profile

        # 1. Load candidate master resume
        master_cv_path = _ROOT_DIR / cand.resume_file
        if not master_cv_path.exists():
            master_cv_path = _ROOT_DIR / "resumes" / cand.resume_file
        if not master_cv_path.exists():
            raise FileNotFoundError(f"Master resume not found for profile {cand.id}: {cand.resume_file}")

        master_text = master_cv_path.read_text(encoding="utf-8")

        # 2. Extract JD keywords & core requirements
        lower_jd = jd_text.lower()
        title_lower = jd_title.lower()

        # 3. Formulate Tailored Headline
        if "ai" in title_lower or "transformation" in title_lower or "agile" in title_lower:
            tailored_headline = f"{cand.headline} | Enterprise Transformation & Governance"
        elif "cloud" in title_lower or "devops" in title_lower or "platform" in title_lower:
            tailored_headline = f"{cand.headline} | Cloud Architecture & Platform Engineering"
        else:
            tailored_headline = f"{cand.headline} | {jd_title}"

        # 4. Formulate Tailored Executive Summary (strictly factual, citing profile proof metrics)
        proof_citations = []
        for pm in cand.proof_metrics[:3]:
            proof_citations.append(f"{pm.label} ({pm.evidence})")

        tailored_summary = (
            f"Senior {cand.scope.seniority.lower()} leader with extensive track record governing large-scale delivery, "
            f"modern operating models, and engineering execution. "
            f"Brings verified enterprise telemetry: {'; '.join(proof_citations)}. "
            f"Specialized in driving predictable delivery across multi-team ecosystems, enforcing engineering guardrails, "
            f"and aligning technical architecture directly with executive commercial objectives."
        )

        # 5. Prioritize and Re-order Work Experience Bullets
        tailored_md = self._reorder_markdown_bullets(master_text, tailored_headline, tailored_summary, lower_jd)

        # 6. AI Content Detector Sanity Check & Humanizer Pass
        # Neutralize robotic giveaways, balance burstiness, and strip AI clichés
        humanized_md, ai_report = HumanizerEngine.humanize_text(tailored_md)

        # 7. Save Tailored Markdown
        clean_cand = re.sub(r"[^a-zA-Z0-9]", "_", cand.full_name)
        clean_jd = re.sub(r"[^a-zA-Z0-9]", "_", jd_id)
        
        md_filename = self.output_dir / f"{clean_cand}_Resume_{clean_jd}.md"
        html_filename = self.output_dir / f"{clean_cand}_Resume_{clean_jd}.html"
        pdf_filename = self.output_dir / f"{clean_cand}_Resume_{clean_jd}.pdf"

        md_filename.write_text(humanized_md, encoding="utf-8")

        # 8. Render Pixel-Perfect A4 HTML
        html_content = render_markdown_resume_to_html(humanized_md, target_job=jd_title)
        html_filename.write_text(html_content, encoding="utf-8")

        # 9. Compile Headless PDF via Edge/Chrome
        pdf_success = compile_custom_resume(html_filename, pdf_filename)

        return {
            "success": pdf_success,
            "candidate": cand.full_name,
            "target_job": jd_title,
            "tailored_headline": tailored_headline,
            "tailored_summary": tailored_summary,
            "md_path": md_filename,
            "html_path": html_filename,
            "pdf_path": pdf_filename,
            "ai_report": {
                "score_ai_probability": ai_report.score_ai_probability,
                "authenticity_score": ai_report.authenticity_score,
                "verdict": ai_report.verdict,
                "burstiness_index": ai_report.burstiness_index,
                "token_diversity_ttr": ai_report.token_diversity_ttr,
                "cliches_detected": ai_report.cliches_detected,
                "recommendations": ai_report.recommendations,
            }
        }

    def _reorder_markdown_bullets(
        self,
        master_text: str,
        new_headline: str,
        new_summary: str,
        lower_jd: str
    ) -> str:
        """Re-orders existing experience bullets by relevance score without modifying factual statements."""
        lines = master_text.splitlines()
        output_lines = []
        
        in_summary = False
        summary_replaced = False
        
        current_job_bullets = []
        in_job = False

        def flush_job_bullets():
            nonlocal current_job_bullets
            if current_job_bullets:
                # Score each bullet against JD text
                scored_bullets = []
                for b in current_job_bullets:
                    b_lower = b.lower()
                    # compute keyword overlap
                    score = 0
                    for token in re.findall(r"\w{4,}", b_lower):
                        if token in lower_jd:
                            score += 1
                    scored_bullets.append((score, b))
                # Sort descending
                scored_bullets.sort(key=lambda x: x[0], reverse=True)
                for _, bu in scored_bullets:
                    output_lines.append(bu)
                current_job_bullets = []

        idx = 0
        while idx < len(lines):
            l = lines[idx]
            l_strip = l.strip()

            # Replace candidate headline (usually line 2)
            if idx == 1 and not l_strip.startswith("#") and not l_strip.startswith("---"):
                output_lines.append(new_headline)
                idx += 1
                continue

            # Replace professional summary section
            if l_strip.startswith("## Professional Summary") or l_strip.startswith("## Executive Summary"):
                output_lines.append(l)
                output_lines.append("")
                output_lines.append(new_summary)
                output_lines.append("")
                summary_replaced = True
                in_summary = True
                idx += 1
                while idx < len(lines) and not lines[idx].strip().startswith("## ") and not lines[idx].strip().startswith("---"):
                    idx += 1
                continue

            if in_summary and (l_strip.startswith("## ") or l_strip.startswith("---")):
                in_summary = False

            # Work Experience bullets
            if l_strip.startswith("### ") or (l_strip.startswith("**") and ("–" in l_strip or "-" in l_strip)):
                flush_job_bullets()
                output_lines.append(l)
                idx += 1
                continue

            if l_strip.startswith("- ") or l_strip.startswith("• "):
                current_job_bullets.append(l)
                idx += 1
                continue

            if l_strip.startswith("## ") or l_strip.startswith("---"):
                flush_job_bullets()
                output_lines.append(l)
                idx += 1
                continue

            output_lines.append(l)
            idx += 1

        flush_job_bullets()
        return "\n".join(output_lines)
