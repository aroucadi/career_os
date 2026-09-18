"""Storage and Persistence Manager for CareerOS Job Radar."""
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

from .models import JobPosting, ScoredJob

logger = logging.getLogger(__name__)

class JobRepository:
    """Manages persistence for scraped jobs, target JDs, and scoring results."""

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            self.base_dir = Path(__file__).resolve().parent.parent
        else:
            self.base_dir = Path(base_dir)

        self.scraped_file = self.base_dir / "scraped_jobs.json"
        self.batch_scoring_file = self.base_dir / "batch_jd_scoring_results.json"
        self.target_jds_dir = self.base_dir / "07_TARGET_JDS"
        self.target_jds_dir.mkdir(parents=True, exist_ok=True)

        self._init_storage()

    def _init_storage(self):
        if not self.scraped_file.exists():
            self.scraped_file.write_text("{}", encoding="utf-8")

    def _load_scraped(self) -> Dict[str, dict]:
        try:
            return json.loads(self.scraped_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def get_all_scraped(self) -> Dict[str, dict]:
        """Returns all scraped jobs mapped by job id."""
        return self._load_scraped()

    def is_already_scraped(self, job_id: str) -> bool:
        """Returns True if job has already been scraped and stored."""
        data = self._load_scraped()
        return job_id in data

    def save_scraped_job(self, job: JobPosting, scored: Optional[ScoredJob] = None):
        """Saves or updates job in scraped_jobs.json."""
        data = self._load_scraped()
        item = {
            "job": job.to_dict(),
            "scored": scored.to_dict() if scored else None,
        }
        data[job.id] = item
        self.scraped_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def save_jd_markdown(self, job: JobPosting) -> str:
        """Saves clean JD into 07_TARGET_JDS/ following repo conventions."""
        existing_files = list(self.target_jds_dir.glob("JD_*.md"))
        max_num = 0
        for f in existing_files:
            match = re.search(r"JD_(\d+)", f.name)
            if match:
                max_num = max(max_num, int(match.group(1)))

        next_num = max_num + 1
        safe_company = re.sub(r"[^\w\-_]", "_", job.company)[:20].strip("_")
        safe_title = re.sub(r"[^\w\-_]", "_", job.title)[:30].strip("_")
        filename = f"JD_{next_num:02d}_{safe_company}_{safe_title}.md"
        target_path = self.target_jds_dir / filename

        content = (
            f"# {job.title} — {job.company}\n\n"
            f"- **URL**: {job.url}\n"
            f"- **Location**: {job.location}\n"
            f"- **Employment Type**: {job.employment_type}\n"
            f"- **Source**: {job.source}\n"
            f"- **Discovered**: {job.discovered_at}\n\n"
            f"---\n\n"
            f"{job.description}\n"
        )
        target_path.write_text(content, encoding="utf-8")
        return filename

    def append_to_batch_scoring(self, scored: ScoredJob, jd_filename: str):
        """Appends result to batch_jd_scoring_results.json matching standard schema."""
        try:
            results = []
            if self.batch_scoring_file.exists():
                results = json.loads(self.batch_scoring_file.read_text(encoding="utf-8"))

            entry = {
                "jd_file": jd_filename,
                "job_title": scored.job_title,
                "employer": scored.company,
                "overall_match_score": scored.overall_match_score,
                "scores": {
                    k: {
                        "score": v.score,
                        "max": int(v.max_score),
                        "evidence": v.evidence,
                    }
                    for k, v in scored.scores.items()
                },
                "bonus_points": {
                    "total": scored.bonus_points,
                    "breakdown": "EU AI Act Governance, banking CoE validation.",
                },
                "deductions": {
                    "total": scored.deductions,
                    "reasons": "Pre-sales / commercial bidding weighting penalty if applicable.",
                },
                "ats_keyword_gaps": scored.ats_keyword_gaps,
                "competency_gaps": scored.competency_gaps,
                "recommended_actions": scored.recommended_actions,
                "recruiter_pitch_hook": scored.recruiter_pitch_hook,
            }

            # Avoid duplicate jd_file entry
            results = [r for r in results if r.get("jd_file") != jd_filename]
            results.append(entry)

            self.batch_scoring_file.write_text(
                json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"Failed to append to batch_jd_scoring_results.json: {e}")
