"""
CareerOS Universal Attachment Processing Engine
================================================
Parses, classifies, and extracts text telemetry from uploaded attachments
(PDF, DOCX, Markdown, Text) in chat messages.
"""

import io
import re
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class UniversalAttachmentEngine:
    """Universal attachment ingester for chat messages."""

    @classmethod
    def process_attachment(cls, name: str, content: str, file_type: Optional[str] = "text/plain") -> Dict[str, Any]:
        """Processes an attachment string or base64 data, extracts plain text, and classifies category."""
        filename = Path(name).name
        ext = Path(filename).suffix.lower()
        text = ""

        # Decode base64 data URI if present
        if content.startswith("data:") and ";base64," in content:
            header, b64_data = content.split(";base64,", 1)
            raw_bytes = base64.b64decode(b64_data)
            try:
                from engine.profiles.extractor import ResumeExtractor
                text = ResumeExtractor.extract_text_from_bytes(filename, raw_bytes)
            except Exception as e:
                logger.warning(f"Failed to parse binary attachment {filename}: {e}")
                text = raw_bytes.decode("utf-8", errors="replace")
        else:
            text = content

        char_count = len(text)

        # Heuristic classification: CV/Resume vs Job Description vs Reference
        name_lower = filename.lower()
        text_lower = text[:1000].lower()
        
        cv_indicators = ["cv", "resume", "curriculum", "profil", "candidate", "formation", "experience", "compétences"]
        jd_indicators = ["job", "jd", "role", "description", "mission", "requisition", "responsabilités", "mandat", "tjm"]

        if any(ind in name_lower for ind in ["cv", "resume"]):
            category = "CV_RESUME"
        elif any(ind in name_lower for ind in ["jd", "job", "mandate", "mission"]):
            category = "JOB_DESCRIPTION"
        elif any(ind in text_lower for ind in ["curriculum vitae", "work experience", "expériences professionnelles"]):
            category = "CV_RESUME"
        elif any(ind in text_lower for ind in ["job description", "responsibilities", "requirements", "about the role"]):
            category = "JOB_DESCRIPTION"
        else:
            # Default to CV if short or personal, otherwise JD
            category = "CV_RESUME" if "summary" in text_lower or "skills" in text_lower else "JOB_DESCRIPTION"

        # Heuristic role / company / rate extraction
        detected_role = None
        detected_company = None
        detected_rate = None

        m_role = re.search(r"(?:Role|Title|Poste|Position)[\s:\-–]+([^\n\r]+)", text, re.IGNORECASE)
        if m_role:
            detected_role = m_role.group(1).strip()[:60]

        m_rate = re.search(r"(\d{3,4})\s*(?:€|EUR)", text)
        if m_rate:
            detected_rate = f"{m_rate.group(1)} EUR"

        summary = f"{filename} ({char_count:,} characters) - Classified as {category}."

        return {
            "filename": filename,
            "saved_path": f"storage/attachments/{filename}",
            "file_type": file_type or ext or "text/plain",
            "category": category,
            "char_count": char_count,
            "summary": summary,
            "text_content": text,
            "detected_role": detected_role,
            "detected_company": detected_company,
            "detected_rate": detected_rate
        }
