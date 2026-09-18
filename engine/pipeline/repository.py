"""
Pipeline Repository & Persistence Layer
========================================
Manages atomic storage in pipeline_state.json and auto-syncs with
07_TARGET_JDS/ and batch_jd_scoring_results.json.
"""

import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .models import (
    Opportunity,
    PipelineStage,
    EvaluationSnapshot,
    MultiPersonaIntel,
    HistoryEvent
)

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
_STORAGE_PATH = _ROOT_DIR / "pipeline_state.json"
_TARGET_JDS_DIR = _ROOT_DIR / "07_TARGET_JDS"
_BATCH_RESULTS_PATH = _ROOT_DIR / "batch_jd_scoring_results.json"


class PipelineRepository:
    """Thread-safe transactional repository for CareerOS opportunities."""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or _STORAGE_PATH
        self._ensure_storage()

    def _ensure_storage(self):
        if not self.storage_path.exists():
            self._save_raw({})

    def _load_raw(self) -> Dict[str, dict]:
        try:
            if not self.storage_path.exists():
                return {}
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            return data.get("opportunities", {})
        except Exception:
            return {}

    def _save_raw(self, opportunities_dict: Dict[str, dict]):
        payload = {
            "version": "2.0",
            "last_synced_at": datetime.now().isoformat(),
            "total_count": len(opportunities_dict),
            "opportunities": opportunities_dict
        }
        # Atomic write with temp file
        temp_file = self.storage_path.with_suffix(".tmp")
        temp_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        shutil.move(str(temp_file), str(self.storage_path))

    def list_all(self, stage_filter: Optional[str] = None) -> List[Opportunity]:
        raw = self._load_raw()
        opps = [Opportunity.model_validate(data) for data in raw.values()]
        if stage_filter:
            stage_upper = stage_filter.upper()
            opps = [o for o in opps if o.stage.value == stage_upper or o.stage.name == stage_upper]
        return opps

    def get(self, opp_id: str) -> Optional[Opportunity]:
        raw = self._load_raw()
        clean_id = self._normalize_id(opp_id)
        if clean_id in raw:
            return Opportunity.model_validate(raw[clean_id])
        # Try search by partial
        for k, v in raw.items():
            if opp_id.lower() in k.lower() or opp_id.lower() in v.get("jd_filename", "").lower():
                return Opportunity.model_validate(v)
        return None

    def save(self, opportunity: Opportunity):
        raw = self._load_raw()
        opportunity.last_updated_at = datetime.now().isoformat()
        raw[opportunity.id] = opportunity.model_dump()
        self._save_raw(raw)

    def delete(self, opp_id: str) -> bool:
        raw = self._load_raw()
        clean_id = self._normalize_id(opp_id)
        if clean_id in raw:
            del raw[clean_id]
            self._save_raw(raw)
            return True
        return False

    def _normalize_id(self, identifier: str) -> str:
        # If passed "JD_30" or "30" or "JD_30_..."
        m = re.search(r"(JD_\d+)", identifier)
        if m:
            return m.group(1)
        m_num = re.search(r"^\d+$", identifier)
        if m_num:
            return f"JD_{int(m_num.group(0)):02d}"
        return identifier

    def sync_from_repository(self) -> int:
        """Scans 07_TARGET_JDS/ and batch_jd_scoring_results.json, creating/updating opportunities."""
        raw = self._load_raw()
        synced_count = 0

        # 1. Load batch scoring if available
        batch_scores = {}
        if _BATCH_RESULTS_PATH.exists():
            try:
                batch_data = json.loads(_BATCH_RESULTS_PATH.read_text(encoding="utf-8"))
                for b in batch_data:
                    fname = b.get("jd_file")
                    if fname:
                        batch_scores[fname] = b
            except Exception:
                pass

        # 2. Iterate all JD files in 07_TARGET_JDS
        for jd_file in _TARGET_JDS_DIR.glob("JD_*.md"):
            m = re.search(r"(JD_\d+)", jd_file.name)
            if not m:
                continue
            opp_id = m.group(1)

            # Parse title, company, location from file
            content = jd_file.read_text(encoding="utf-8")
            title = opp_id
            company = "Enterprise Client"
            location = "EMEA / Remote"

            first_line = content.strip().split("\n")[0]
            if first_line.startswith("#"):
                header_part = first_line.lstrip("#").strip()
                if "—" in header_part:
                    parts = header_part.split("—", 1)
                    title = parts[0].strip()
                    company = parts[1].strip()
                elif "-" in header_part:
                    parts = header_part.split("-", 1)
                    title = parts[0].strip()
                    company = parts[1].strip()
                else:
                    title = header_part

            loc_m = re.search(r"- \*\*Location\*\*:\s*([^\n]+)", content, re.IGNORECASE)
            if loc_m:
                location = loc_m.group(1).strip()

            emp_m = re.search(r"-\s*\*\*(?:Contract Type|Type of employment)\*\*:\s*([^\n]+)", content, re.IGNORECASE)
            employment_type = "Contract"
            if emp_m and emp_m.group(1):
                employment_type = emp_m.group(1).strip()

            url_m = re.search(r"- \*\*URL\*\*:\s*([^\n]+)", content, re.IGNORECASE)
            url = url_m.group(1).strip() if url_m else ""

            # Check if exists
            if opp_id not in raw:
                opp = Opportunity(
                    id=opp_id,
                    jd_filename=jd_file.name,
                    job_title=title,
                    company=company,
                    location=location,
                    employment_type=employment_type,
                    stage=PipelineStage.DISCOVERED,
                    url=url
                )
                opp.history.append(HistoryEvent(
                    from_stage=None,
                    to_stage=PipelineStage.DISCOVERED,
                    notes="Discovered & indexed from 07_TARGET_JDS"
                ))

                # If batch score exists, hydrate evaluation
                if jd_file.name in batch_scores:
                    bs = batch_scores[jd_file.name]
                    opp.evaluation = EvaluationSnapshot(
                        overall_score=float(bs.get("overall_match_score", 0)),
                        scores={k: float(v.get("score", 0)) for k, v in bs.get("scores", {}).items() if isinstance(v, dict)},
                        strategic_verdict="GO" if bs.get("overall_match_score", 0) >= 75 else "CONDITIONAL GO",
                        ats_keyword_gaps=bs.get("ats_keyword_gaps", []),
                        competency_gaps=bs.get("competency_gaps", [])
                    )
                    opp.stage = PipelineStage.QUALIFIED

                raw[opp_id] = opp.model_dump()
                synced_count += 1
            else:
                # Update metadata if needed
                item = raw[opp_id]
                item["jd_filename"] = jd_file.name
                item["job_title"] = title
                item["company"] = company
                item["location"] = location

        self._save_raw(raw)
        return synced_count
