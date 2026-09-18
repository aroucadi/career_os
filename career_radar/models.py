"""Data models for CareerOS Job Radar."""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class JobPosting:
    id: str
    title: str
    company: str
    location: str = "Unknown"
    url: str = ""
    source: str = "linkedin"
    employment_type: str = "Contract"
    is_remote: bool = True
    posted_date: Optional[str] = None
    description: str = ""
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class RubricPillarScore:
    score: float
    max_score: float
    evidence: str

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class ScoredJob:
    job_id: str
    job_title: str
    company: str
    url: str
    overall_match_score: int
    scores: Dict[str, RubricPillarScore]
    bonus_points: int = 0
    deductions: int = 0
    ats_keyword_gaps: List[str] = field(default_factory=list)
    competency_gaps: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    recruiter_pitch_hook: str = ""
    saved_jd_file: Optional[str] = None
    scored_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)
