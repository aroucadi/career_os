"""
CareerOS Universal Web Job Ingestion Engine
===========================================
Fetches, scrapes, structures, and persists Job Descriptions directly from web URLs:
- Free-Work, LinkedIn, Welcome to the Jungle, Indeed, Apec, or arbitrary employer career sites.
- Extracts Title, Company, Location, Remote Policy, TJM / Salary, and Full JD text.
- Formats into standardized CareerOS Markdown and saves to 07_TARGET_JDS/.
- Registers the new mandate in the Pipeline CRM.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from engine.pipeline.repository import PipelineRepository
from engine.pipeline.models import Opportunity, PipelineStage

load_dotenv()
logger = logging.getLogger(__name__)

_ROOT_DIR = Path(__file__).resolve().parent.parent
_TARGET_JDS_DIR = _ROOT_DIR / "07_TARGET_JDS"
_TARGET_JDS_DIR.mkdir(parents=True, exist_ok=True)


class URLJobIngestionEngine:
    """Scrapes and converts any live job URL into a persisted CareerOS Markdown mandate."""

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    @classmethod
    def get_next_jd_number(cls) -> int:
        """Finds the next incremental JD index (e.g. JD_31 if JD_30 is current max)."""
        max_idx = 30
        for f in _TARGET_JDS_DIR.glob("JD_*.md"):
            m = re.search(r"JD_(\d+)", f.name)
            if m:
                idx = int(m.group(1))
                if idx > max_idx:
                    max_idx = idx
        return max_idx + 1

    @classmethod
    def ingest_url(cls, url: str) -> Dict[str, Any]:
        """Fetches, cleans, structures, and persists a job posting from a URL."""
        # 1. Fetch HTML content
        with httpx.Client(headers=cls.DEFAULT_HEADERS, follow_redirects=True, timeout=20.0) as client:
            response = client.get(url)
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch URL ({response.status_code}): {url}")
            html_text = response.text

        soup = BeautifulSoup(html_text, "html.parser")

        # 2. Extract JSON-LD if present
        json_ld_data = None
        for s in soup.find_all("script", type="application/ld+json"):
            try:
                d = json.loads(s.string)
                if isinstance(d, dict) and d.get("@type") == "JobPosting":
                    json_ld_data = d
                    break
            except Exception:
                pass

        # 3. Clean noise tags
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
            tag.decompose()

        main_elem = soup.find("main") or soup.find("article") or soup.body
        body_text = main_elem.get_text("\n", strip=True) if main_elem else soup.get_text("\n", strip=True)
        raw_snippet = body_text[:8000]

        # 4. Use Gemini 3.8 Flash to structure and extract high-fidelity entities
        title = "Executive Opportunity"
        company = "Direct Client"
        location = "Remote / Flexible"
        tjm = "To be negotiated"
        markdown_body = ""
        recruiter_name = None
        recruiter_email = None

        try:
            from google import genai
            client = genai.Client()
            model_name = os.getenv("DEFAULT_MODEL", "gemini-3.8-flash")

            struct_prompt = (
                "You are an expert CareerOS Job Description Extraction Engine.\n"
                "Extract and standardize the following scraped job posting into high-caliber Markdown.\n\n"
                "Return a valid JSON object with the following fields:\n"
                "{\n"
                '  "title": "Standardized job title",\n'
                '  "company": "Company or recruitment agency name",\n'
                '  "location": "Location & remote policy (e.g. Paris / Île-de-France - Mode hybride)",\n'
                '  "tjm_or_salary": "Stated or estimated daily rate or compensation",\n'
                '  "recruiter_name": "Name of recruiter or hiring contact if mentioned, or null",\n'
                '  "recruiter_email": "Direct email address of recruiter or contact if mentioned, or null",\n'
                '  "key_missions": ["mission 1", "mission 2", "mission 3"],\n'
                '  "required_skills": ["skill 1", "skill 2", "skill 3"],\n'
                '  "markdown_content": "Full, beautiful Markdown document formatted with headers, context, missions, profile, and tech stack."\n'
                "}\n\n"
                f"URL: {url}\n"
                f"JSON-LD Context (if any): {json.dumps(json_ld_data) if json_ld_data else 'None'}\n"
                f"Raw Scraped Text:\n{raw_snippet}"
            )

            res = client.models.generate_content(
                model=model_name,
                contents=struct_prompt
            )

            text_resp = res.text or ""
            json_match = re.search(r"\{[\s\S]*\}", text_resp)
            if json_match:
                extracted = json.loads(json_match.group(0))
                title = extracted.get("title", title)
                company = extracted.get("company", company)
                location = extracted.get("location", location)
                tjm = extracted.get("tjm_or_salary", tjm)
                recruiter_name = extracted.get("recruiter_name")
                recruiter_email = extracted.get("recruiter_email")
                markdown_body = extracted.get("markdown_content", "")
        except Exception as e:
            logger.warning(f"Gemini structuring failed, using heuristic extraction: {e}")

        # Heuristic email check if not found
        if not recruiter_email:
            m_email = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", raw_snippet)
            if m_email:
                recruiter_email = m_email.group(0)

        # Fallback markdown if not generated
        if not markdown_body or len(markdown_body) < 100:
            markdown_body = (
                f"# Mandat: {title}\n\n"
                f"**Entreprise / Cabinet:** {company}\n"
                f"**Localisation:** {location}\n"
                f"**Rémunération / TJM:** {tjm}\n"
                f"**Source URL:** [{url}]({url})\n\n"
                f"## Description du Poste\n\n"
                f"{raw_snippet[:4000]}\n"
            )

        # 5. Determine Next JD Index & Target Filename
        next_num = cls.get_next_jd_number()
        safe_company = re.sub(r"[^\w]+", "_", company).strip("_") or "Cabinet"
        safe_title = re.sub(r"[^\w]+", "_", title).strip("_")[:40] or "Opportunite"
        jd_id = f"JD_{next_num:02d}"
        filename = f"{jd_id}_{safe_company}_{safe_title}.md"
        target_path = _TARGET_JDS_DIR / filename

        # 6. Save to 07_TARGET_JDS/
        full_md_content = (
            f"---\n"
            f"id: {jd_id}\n"
            f"title: \"{title}\"\n"
            f"company: \"{company}\"\n"
            f"location: \"{location}\"\n"
            f"rate: \"{tjm}\"\n"
            f"source_url: \"{url}\"\n"
            f"---\n\n"
            f"{markdown_body}\n"
        )
        target_path.write_text(full_md_content, encoding="utf-8", errors="replace")
        logger.info(f"Successfully saved scraped job from {url} to {target_path}")

        # 7. Register in Pipeline CRM
        try:
            repo = PipelineRepository()
            opp = Opportunity(
                id=jd_id,
                jd_filename=filename,
                company=company,
                job_title=title,
                location=location,
                stage=PipelineStage.DISCOVERED,
                url=url
            )
            repo.save(opp)

            logger.info(f"Registered {opp.id} into Pipeline CRM")
        except Exception as e:
            logger.warning(f"Pipeline CRM registration note: {e}")

        return {
            "success": True,
            "jd_id": jd_id,
            "filename": filename,
            "saved_path": str(target_path),
            "title": title,
            "company": company,
            "location": location,
            "tjm": tjm,
            "recruiter_name": recruiter_name,
            "recruiter_email": recruiter_email,
            "source_url": url,
            "char_count": len(full_md_content),
            "markdown_content": full_md_content
        }
