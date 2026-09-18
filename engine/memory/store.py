"""
CareerOS Episodic Memory Store
==============================
Thread-safe transactional store for episodic records, market learnings,
and precedent retrieval.
"""

import json
import shutil
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

from .models import (
    EpisodicRecord,
    FeedbackOutcome,
    ObjectionCategory,
    CompanyTrackRecord
)

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
_MEMORY_STORAGE_PATH = _ROOT_DIR / "cache" / "memory" / "episodic_memory.json"


class EpisodicMemoryStore:
    """Manages persistence and semantic querying of historical application precedents."""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or _MEMORY_STORAGE_PATH
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_storage()

    def _ensure_storage(self):
        if not self.storage_path.exists():
            self._save_raw([])

    def _load_raw(self) -> List[dict]:
        try:
            if not self.storage_path.exists():
                return []
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            return data.get("records", [])
        except Exception:
            return []

    def _save_raw(self, records_list: List[dict]):
        payload = {
            "version": "1.0",
            "last_updated_at": datetime.now().isoformat(),
            "total_records": len(records_list),
            "records": records_list
        }
        temp_file = self.storage_path.with_suffix(".tmp")
        temp_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        shutil.move(str(temp_file), str(self.storage_path))

    def record_feedback(
        self,
        opportunity_id: str,
        company: str,
        role_title: str,
        outcome: FeedbackOutcome,
        agency: Optional[str] = None,
        domain: str = "AI & Delivery",
        candidate_profile_id: str = "alaa_roucadi",
        objection_category: Optional[ObjectionCategory] = None,
        actual_rate_offered_eur: Optional[float] = None,
        notes: str = "",
        key_takeaways: Optional[List[str]] = None,
        successful_angles: Optional[List[str]] = None
    ) -> EpisodicRecord:
        """Records a structured market interaction event."""
        records = self._load_raw()
        record_id = f"MEM_{opportunity_id}_{len(records) + 1:02d}"

        takeaways = key_takeaways or []
        if not takeaways and notes:
            takeaways = [notes]

        angles = successful_angles or []

        rec = EpisodicRecord(
            id=record_id,
            opportunity_id=opportunity_id,
            company=company,
            agency=agency,
            role_title=role_title,
            domain=domain,
            candidate_profile_id=candidate_profile_id,
            outcome=outcome,
            objection_category=objection_category,
            actual_rate_offered_eur=actual_rate_offered_eur,
            notes=notes,
            key_takeaways=takeaways,
            successful_angles=angles,
            timestamp=datetime.now().isoformat()
        )

        records.append(rec.model_dump())
        self._save_raw(records)
        return rec

    def list_all(self) -> List[EpisodicRecord]:
        raw = self._load_raw()
        return [EpisodicRecord.model_validate(r) for r in raw]

    def query_precedents(
        self,
        company: Optional[str] = None,
        domain: Optional[str] = None,
        role_title: Optional[str] = None,
        limit: int = 5
    ) -> List[EpisodicRecord]:
        """Retrieves past precedent records matching company, domain, or role keywords."""
        all_records = self.list_all()
        matches = []

        comp_clean = (company or "").lower().strip()
        dom_clean = (domain or "").lower().strip()
        role_tokens = [t.lower() for t in re.findall(r"\w+", role_title or "") if len(t) > 3]

        for rec in reversed(all_records):  # Most recent first
            score = 0
            # Exact company or agency match
            if comp_clean and (comp_clean in rec.company.lower() or (rec.agency and comp_clean in rec.agency.lower())):
                score += 10
            # Domain match
            if dom_clean and dom_clean in rec.domain.lower():
                score += 4
            # Role token overlap
            for tok in role_tokens:
                if tok in rec.role_title.lower():
                    score += 2

            if score > 0:
                matches.append((score, rec))

        matches.sort(key=lambda x: x[0], reverse=True)
        return [m[1] for m in matches[:limit]]

    def get_company_track_record(self, company_name: str) -> CompanyTrackRecord:
        """Summarizes all historical interactions with a given employer or agency."""
        all_records = self.list_all()
        matching = [
            r for r in all_records
            if company_name.lower() in r.company.lower() or (r.agency and company_name.lower() in r.agency.lower())
        ]

        track = CompanyTrackRecord(company_name=company_name, total_interactions=len(matching))
        rates = []

        for m in matching:
            out_str = m.outcome.value
            track.outcomes_count[out_str] = track.outcomes_count.get(out_str, 0) + 1
            if m.actual_rate_offered_eur:
                rates.append(m.actual_rate_offered_eur)
            if m.objection_category:
                track.known_objections.append(f"{m.objection_category.value}: {m.notes}")
            for tk in m.key_takeaways:
                if tk not in track.strategic_rules:
                    track.strategic_rules.append(tk)

        if rates:
            track.average_rate_eur = sum(rates) / len(rates)

        return track

    def format_precedents_context(
        self,
        company: Optional[str] = None,
        domain: Optional[str] = None,
        role_title: Optional[str] = None
    ) -> str:
        """Formats matching precedents into an injection-ready prompt block."""
        precedents = self.query_precedents(company=company, domain=domain, role_title=role_title, limit=3)
        if not precedents:
            return "No prior historical precedents recorded for this company or role archetype."

        lines = ["Historical Precedents & Market Learnings (Episodic Memory):"]
        for p in precedents:
            comp_str = f"{p.company} ({p.agency})" if p.agency else p.company
            rate_str = f" | Disclosed Rate: {p.actual_rate_offered_eur:.0f} EUR/day" if p.actual_rate_offered_eur else ""
            lines.append(f"- [{p.outcome.value}] at {comp_str}{rate_str}:")
            if p.key_takeaways:
                for tk in p.key_takeaways:
                    lines.append(f"  • Warning/Learnings: {tk}")
            if p.successful_angles:
                for sa in p.successful_angles:
                    lines.append(f"  • Winning Angle: {sa}")
        return "\n".join(lines)
