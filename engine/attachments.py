"""
CareerOS Universal Multimodal Attachment Engine
==============================================
Parses, persists, classifies, and analyzes ANY document format attached by the user:
- PDF (.pdf) via pypdf
- Word documents (.docx, .doc) via python-docx
- Images (.png, .jpg, .jpeg, .webp) via Gemini 3.8 Flash Vision OCR
- Markdown, Text, JSON (.md, .txt, .json)
- Automatic document classification (CV, Job Description, Recruiter Message, Contract, General)
- Central persistence to storage/attachments/
"""

import os
import io
import re
import json
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

import pypdf
import docx

_ROOT_DIR = Path(__file__).resolve().parent.parent
_STORAGE_DIR = _ROOT_DIR / "storage" / "attachments"
_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

_RESUMES_UPLOADS = _ROOT_DIR / "resumes" / "uploads"
_RESUMES_UPLOADS.mkdir(parents=True, exist_ok=True)

_TARGET_JDS = _ROOT_DIR / "07_TARGET_JDS"
_TARGET_JDS.mkdir(parents=True, exist_ok=True)


class UniversalAttachmentEngine:
    """Intelligently ingests, parses, persists, and classifies any attached file."""

    @classmethod
    def extract_text_from_docx(cls, file_bytes: bytes) -> str:
        """Extracts text from a .docx file."""
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text.strip())
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_text:
                        full_text.append(" | ".join(row_text))
            return "\n\n".join(full_text)
        except Exception as e:
            return f"[Error parsing DOCX: {e}]"

    @classmethod
    def extract_text_from_pdf(cls, file_bytes: bytes) -> str:
        """Extracts text from a PDF file using pypdf."""
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            pages_text = []
            for p in reader.pages:
                txt = p.extract_text()
                if txt:
                    pages_text.append(txt.strip())
            return "\n\n".join(pages_text)
        except Exception as e:
            return f"[Error parsing PDF: {e}]"

    @classmethod
    def ocr_and_analyze_image(cls, file_bytes: bytes, mime_type: str = "image/png") -> str:
        """Uses Gemini 3.8 Flash Vision to transcribe and extract text from an attached image."""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client()
            part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
            prompt = (
                "You are an expert document OCR engine. Transcribe the entire text from this image accurately. "
                "Preserve titles, bullet points, company names, rates, dates, and requirements."
            )

            res = client.models.generate_content(
                model=os.getenv("DEFAULT_MODEL", "gemini-3.8-flash"),
                contents=[prompt, part]
            )
            return res.text or "[Image contained no readable text]"
        except Exception as e:
            return f"[Error extracting text from image via Gemini Vision: {e}]"

    @classmethod
    def classify_document(cls, filename: str, text: str) -> Dict[str, Any]:
        """Classifies the document into a semantic category and extracts salient entities."""
        name_lower = filename.lower()
        text_lower = text.lower()[:4000]

        # 1. CV / Resume indicators
        cv_indicators = ["curriculum vitae", "resume", "cv", "experience", "expérience", "education", "formation", "compétences", "skills", "certifications", "employment history"]
        cv_score = sum(2 for w in ["cv", "resume", "curriculum", "bio"] if w in name_lower) + sum(1 for w in cv_indicators if w in text_lower)

        # 2. Job Description indicators
        jd_indicators = ["responsibilities", "responsabilités", "requirements", "profil recherché", "about the role", "missions", "stack technique", "tjm", "daily rate", "hiring", "job description", "mandat"]
        jd_score = sum(2 for w in ["jd", "job", "offer", "mandat", "poste", "offre"] if w in name_lower) + sum(1 for w in jd_indicators if w in text_lower)

        # 3. Recruiter Message / Communication
        recruiter_indicators = ["inmail", "cher alaa", "bonjour", "hello", "suite à votre", "candidature", "entretien", "disponibilité", "merci pour", "retour client", "rejet", "proposition"]
        recruiter_score = sum(2 for w in ["message", "mail", "inmail", "feedback", "reponse"] if w in name_lower) + sum(1 for w in recruiter_indicators if w in text_lower)

        # 4. Contract / Proposal
        contract_indicators = ["contrat", "accord", "clause", "tjm", "nda", "facturation", "pénalités", "termes", "conditions générales"]
        contract_score = sum(1 for w in contract_indicators if w in text_lower)

        # Determine winner
        scores = {
            "CV_RESUME": cv_score,
            "JOB_DESCRIPTION": jd_score,
            "RECRUITER_MESSAGE": recruiter_score,
            "CONTRACT_OR_PROPOSAL": contract_score
        }
        best_category = max(scores, key=scores.get)
        if scores[best_category] < 2:
            best_category = "GENERAL_DOCUMENT"

        # Entity extraction
        role_match = re.search(r"(?:role|poste|title|titre|position)\s*[:\-]\s*([^\n\r]+)", text, re.IGNORECASE)
        company_match = re.search(r"(?:company|entreprise|client|société)\s*[:\-]\s*([^\n\r]+)", text, re.IGNORECASE)
        rate_match = re.search(r"(?:(\d{3,4})\s*(?:€|eur|euros?)(?:\s*/\s*j(?:our)?)?)", text, re.IGNORECASE)

        return {
            "category": best_category,
            "confidence_scores": scores,
            "detected_role": role_match.group(1).strip() if role_match else None,
            "detected_company": company_match.group(1).strip() if company_match else None,
            "detected_rate": rate_match.group(1).strip() if rate_match else None
        }

    @classmethod
    def process_attachment(cls, filename: str, content: str, mime_type: Optional[str] = None) -> Dict[str, Any]:
        """Unified ingest pipeline: decodes, extracts text, classifies, and persists any document."""
        safe_name = re.sub(r"[^\w\.-]", "_", filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_name = f"{timestamp}_{safe_name}"
        saved_path = _STORAGE_DIR / target_name

        extracted_text = ""
        file_ext = Path(filename).suffix.lower()

        # Is content base64 encoded?
        is_base64 = False
        raw_bytes = None
        if "base64," in content:
            content = content.split("base64,")[1]
            is_base64 = True
        elif file_ext in [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".docx", ".doc"]:
            # Try base64 decoding
            try:
                raw_bytes = base64.b64decode(content)
                is_base64 = True
            except Exception:
                is_base64 = False

        if is_base64 and raw_bytes is None:
            raw_bytes = base64.b64decode(content)

        # 1. Process by Extension
        if file_ext == ".pdf":
            saved_path.write_bytes(raw_bytes if raw_bytes else content.encode())
            extracted_text = cls.extract_text_from_pdf(raw_bytes if raw_bytes else content.encode())

        elif file_ext in [".docx", ".doc"]:
            saved_path.write_bytes(raw_bytes if raw_bytes else content.encode())
            extracted_text = cls.extract_text_from_docx(raw_bytes if raw_bytes else content.encode())

        elif file_ext in [".png", ".jpg", ".jpeg", ".webp"]:
            saved_path.write_bytes(raw_bytes)
            m_type = mime_type or f"image/{file_ext.replace('.', '')}"
            extracted_text = cls.ocr_and_analyze_image(raw_bytes, m_type)

        else:
            # Text, Markdown, JSON
            extracted_text = content
            saved_path.write_text(extracted_text, encoding="utf-8", errors="replace")

        # 2. Autonomous Classification
        classification = cls.classify_document(filename, extracted_text)
        cat = classification["category"]

        # 3. Categorized Mirroring / Secondary Persistence
        if cat == "CV_RESUME":
            mirror_path = _RESUMES_UPLOADS / target_name
            if raw_bytes:
                mirror_path.write_bytes(raw_bytes)
            else:
                mirror_path.write_text(extracted_text, encoding="utf-8", errors="replace")

        elif cat == "JOB_DESCRIPTION":
            clean_stem = Path(filename).stem
            mirror_path = _TARGET_JDS / f"{clean_stem}.md"
            mirror_path.write_text(extracted_text, encoding="utf-8", errors="replace")

        # 4. Generate 2-line Executive Summary
        lines = [l.strip() for l in extracted_text.splitlines() if l.strip()]
        preview_summary = " ".join(lines[:3])[:200] if lines else "Document ingested without text body."

        return {
            "filename": filename,
            "saved_path": str(saved_path),
            "file_type": file_ext.replace(".", "").upper() or "TEXT",
            "category": cat,
            "char_count": len(extracted_text),
            "text_content": extracted_text,
            "summary": preview_summary,
            "detected_role": classification.get("detected_role"),
            "detected_company": classification.get("detected_company"),
            "detected_rate": classification.get("detected_rate"),
            "raw_lines_count": len(lines)
        }


# Backwards compatibility alias
AttachmentManager = UniversalAttachmentEngine

