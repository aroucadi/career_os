"""
Executive signals extraction module.
Extracts high-level leadership metrics, governance frameworks, P&L scale, and org headcount
from structured JSONResume objects or raw markdown/text to augment executive evaluations.
"""

import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Optional import of JSONResume
try:
    _ENGINE_DIR = Path(__file__).resolve().parent.parent
    if str(_ENGINE_DIR) not in sys.path:
        sys.path.insert(0, str(_ENGINE_DIR))
    from models import JSONResume
except ImportError:
    JSONResume = Any


class ExecutiveEnricher:
    """Extracts executive and leadership signals from a JSONResume or raw text/markdown."""

    def __init__(self, resume_data: Union[Any, str, Path]):
        if isinstance(resume_data, Path):
            self.raw_text = resume_data.read_text(encoding="utf-8")
            self.resume_data = None
        elif isinstance(resume_data, str) and ("\n" in resume_data or resume_data.endswith(".md")):
            if Path(resume_data).is_file():
                self.raw_text = Path(resume_data).read_text(encoding="utf-8")
                self.resume_data = None
            else:
                self.raw_text = resume_data
                self.resume_data = None
        else:
            self.resume_data = resume_data
            self.raw_text = None

    def extract_signals(self) -> Dict[str, Any]:
        """Extract structured leadership signals from work experience and summary."""
        full_text = self._build_full_text()

        signals = {
            "pnl_and_budget_scale": self._extract_budgets(full_text),
            "org_scale_and_headcount": self._extract_headcounts(full_text),
            "governance_and_compliance": self._extract_governance(full_text),
            "c_level_and_board_exposure": self._extract_c_suite_signals(full_text),
            "custom_apps_and_innovation": self._extract_innovations(full_text),
        }
        return signals

    def _build_full_text(self) -> str:
        if self.raw_text is not None:
            return self.raw_text

        text_parts = []
        if hasattr(self.resume_data, "basics") and self.resume_data.basics:
            if getattr(self.resume_data.basics, "summary", None):
                text_parts.append(self.resume_data.basics.summary)
        if hasattr(self.resume_data, "work") and self.resume_data.work:
            for w in self.resume_data.work:
                if getattr(w, "summary", None):
                    text_parts.append(w.summary)
                if getattr(w, "highlights", None):
                    text_parts.extend(w.highlights)
        return "\n".join(text_parts)

    def _extract_budgets(self, text: str) -> List[str]:
        patterns = [
            r"\$\d+(?:\.\d+)?(?:M|B|K|\s+million|\s+billion|\s+thousand)",
            r"€\d+(?:\.\d+)?(?:M|B|K|\s+million|\s+billion|\s+thousand)",
            r"budget[s]?\s+of\s+[^,\.\n]+",
            r"P&L[^\.\n]+",
        ]
        matches = []
        for p in patterns:
            found = re.findall(p, text, re.IGNORECASE)
            matches.extend(found)
        return list(set(matches))

    def _extract_headcounts(self, text: str) -> List[str]:
        patterns = [
            r"\d+\+?\s+(?:squads|teams|engineers|developers|direct reports|members|people|staff|agencies)",
            r"(?:managed|led|coached|supporting)\s+\d+\+?\s+[^,\.\n]+",
            r"scaled\s+[^,\.\n]+",
        ]
        matches = []
        for p in patterns:
            found = re.findall(p, text, re.IGNORECASE)
            matches.extend(found)
        return list(set(matches))

    def _extract_governance(self, text: str) -> List[str]:
        governance_keywords = [
            "EU AI Act", "AIGP", "AI FinOps", "ISO/IEC 42001", "AI Governance",
            "Risk Classification", "GDPR", "Model Bias", "Security & Data Privacy",
            "Human-in-the-loop", "Model Governance", "Spec-Driven Development", "SDD"
        ]
        found = []
        for kw in governance_keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE):
                found.append(kw)
        return list(set(found))

    def _extract_c_suite_signals(self, text: str) -> List[str]:
        keywords = [
            "C-Level", "CTO", "CIO", "CEO", "VP of Engineering", "VP of Product",
            "Board", "Executive Committee", "Steering Committee", "Stakeholder Alignment",
            "leadership"
        ]
        found = []
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE):
                found.append(kw)
        return list(set(found))

    def _extract_innovations(self, text: str) -> List[str]:
        patterns = [
            r"developed\s+[^,\.\n]+\s+app",
            r"created\s+[^,\.\n]+\s+framework",
            r"in-house\s+[^,\.\n]+",
            r"patent[s]?",
            r"Alignify",
            r"custom\s+[^,\.\n]+\s+app",
        ]
        matches = []
        for p in patterns:
            found = re.findall(p, text, re.IGNORECASE)
            matches.extend(found)
        return list(set(matches))


def extract_executive_signals(resume_data: Union[Any, str, Path]) -> Dict[str, Any]:
    """Helper function to extract executive signals."""
    enricher = ExecutiveEnricher(resume_data)
    return enricher.extract_signals()


if __name__ == "__main__":
    test_cv = Path(__file__).resolve().parent.parent.parent / "Alaa_Eddine_Roucadi_Resume_v12.md"
    if test_cv.exists():
        signals = extract_executive_signals(test_cv)
        print("Executive Signals Extracted from v12:")
        import json
        print(json.dumps(signals, indent=2, ensure_ascii=False))
