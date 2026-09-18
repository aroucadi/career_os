"""CareerOS Radar Agent Orchestrator."""
import logging
import time
from typing import Callable, List, Optional

from .analyzer import JobAnalyzer
from .models import JobPosting, ScoredJob
from .scrapers.generic import GenericJobScraper
from .scrapers.linkedin import LinkedInGuestScraper
from .storage import JobRepository

logger = logging.getLogger(__name__)

class RadarAgent:
    """Orchestrates job discovery, scraping, scoring, and alerting."""

    DEFAULT_QUERIES = [
        "AI Delivery Manager",
        "Agentic Delivery Manager",
        "AI Product Delivery Manager",
        "Technical Delivery Manager AI",
        "AI Agent Operations Manager",
    ]

    def __init__(self, repository: Optional[JobRepository] = None, analyzer: Optional[JobAnalyzer] = None):
        self.repo = repository or JobRepository()
        self.analyzer = analyzer or JobAnalyzer()
        self.linkedin_scraper = LinkedInGuestScraper()
        self.generic_scraper = GenericJobScraper()

    def process_url(self, url: str) -> Optional[ScoredJob]:
        """Fetches a single job URL, extracts content, scores it, and persists."""
        if "linkedin.com" in url:
            job = self.linkedin_scraper.fetch_from_url(url)
        else:
            job = self.generic_scraper.fetch_from_url(url)

        if not job or not job.description:
            logger.error(f"Could not extract description for URL: {url}")
            return None

        # Score the job
        scored = self.analyzer.analyze(job)

        # Save markdown JD and record
        jd_file = self.repo.save_jd_markdown(job)
        scored.saved_jd_file = jd_file
        self.repo.save_scraped_job(job, scored)
        self.repo.append_to_batch_scoring(scored, jd_file)

        return scored

    def scan_and_score(
        self,
        queries: Optional[List[str]] = None,
        location: str = "Worldwide",
        remote: bool = True,
        contract: bool = True,
        time_filter: str = "week",
        limit_per_query: int = 5,
        min_score_to_save: int = 60,
    ) -> List[ScoredJob]:
        """Runs a complete radar scan across queries, deduplicates, fetches details, and scores."""
        target_queries = queries or self.DEFAULT_QUERIES
        scored_jobs: List[ScoredJob] = []

        for query in target_queries:
            logger.info(f"Scanning LinkedIn for query: '{query}' (Remote={remote}, Contract={contract}, Time={time_filter})")
            listings = self.linkedin_scraper.search_jobs(
                keywords=query,
                location=location,
                remote=remote,
                contract=contract,
                time_filter=time_filter,
                limit=limit_per_query,
            )

            for job in listings:
                if self.repo.is_already_scraped(job.id):
                    logger.info(f"Skipping already processed job {job.id} ({job.title} at {job.company})")
                    continue

                logger.info(f"Fetching full JD for: {job.title} at {job.company}...")
                job_full = self.linkedin_scraper.fetch_job_details(job)

                if not job_full.description or len(job_full.description) < 100:
                    logger.warning(f"Skipping job {job.id} - empty or too short description")
                    continue

                scored = self.analyzer.analyze(job_full)

                # Persist to repository
                if scored.overall_match_score >= min_score_to_save:
                    jd_filename = self.repo.save_jd_markdown(job_full)
                    scored.saved_jd_file = jd_filename
                    self.repo.append_to_batch_scoring(scored, jd_filename)

                self.repo.save_scraped_job(job_full, scored)
                scored_jobs.append(scored)

                # Polite delay
                time.sleep(1.0)

        # Sort by match score descending
        scored_jobs.sort(key=lambda s: s.overall_match_score, reverse=True)
        return scored_jobs

    def run_continuous_radar(
        self,
        interval_seconds: int = 3600,
        callback: Optional[Callable[[ScoredJob], None]] = None,
        **scan_kwargs,
    ):
        """Runs radar continuously in the background at regular intervals."""
        logger.info(f"Starting continuous CareerOS Radar (Interval: {interval_seconds}s)...")
        while True:
            try:
                logger.info("Executing scheduled radar pulse...")
                results = self.scan_and_score(**scan_kwargs)
                for res in results:
                    if callback:
                        callback(res)
            except Exception as e:
                logger.error(f"Radar loop error: {e}")

            time.sleep(interval_seconds)

    def close(self):
        self.linkedin_scraper.close()
        self.generic_scraper.close()
