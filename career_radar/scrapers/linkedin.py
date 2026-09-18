"""LinkedIn Public Guest Job Scraper for CareerOS Job Radar."""
import logging
import re
import time
import urllib.parse
from typing import Dict, List, Optional
import httpx
from bs4 import BeautifulSoup

from ..models import JobPosting

logger = logging.getLogger(__name__)

class LinkedInGuestScraper:
    """Scrapes LinkedIn jobs using the public guest API endpoints without authentication."""

    BASE_SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    BASE_POSTING_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    TIME_FILTERS = {
        "24h": "r86400",
        "1d": "r86400",
        "3d": "r259200",
        "week": "r604800",
        "7d": "r604800",
        "month": "r2592000",
    }

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.client = httpx.Client(headers=self.DEFAULT_HEADERS, timeout=self.timeout, follow_redirects=True)

    def _get_with_retry(self, url: str, params: Optional[dict] = None, max_retries: int = 3) -> Optional[httpx.Response]:
        """Performs GET with retry and exponential backoff."""
        for attempt in range(1, max_retries + 1):
            try:
                resp = self.client.get(url, params=params)
                if resp.status_code == 200:
                    return resp
                logger.warning(f"Request {url} returned status {resp.status_code} (attempt {attempt}/{max_retries})")
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                logger.warning(f"Network error on {url}: {e} (attempt {attempt}/{max_retries})")
            time.sleep(1.5 * attempt)
        return None

    def search_jobs(
        self,
        keywords: str = "AI Delivery Manager",
        location: str = "Worldwide",
        remote: bool = True,
        contract: bool = True,
        time_filter: str = "week",
        limit: int = 15,
    ) -> List[JobPosting]:
        """Search for job listings matching the criteria."""
        jobs: List[JobPosting] = []
        start = 0

        # Build query parameters
        params: Dict[str, str] = {
            "keywords": keywords,
            "location": location,
            "start": str(start),
        }

        if remote:
            # f_WT: 1 = On-site, 2 = Remote, 3 = Hybrid
            params["f_WT"] = "2"

        if contract:
            # f_JT: C = Contract / Freelance
            params["f_JT"] = "C"

        if time_filter in self.TIME_FILTERS:
            params["f_TPR"] = self.TIME_FILTERS[time_filter]

        while len(jobs) < limit:
            params["start"] = str(start)
            try:
                response = self._get_with_retry(self.BASE_SEARCH_URL, params=params)
                if not response or response.status_code != 200:
                    break

                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.find_all("div", class_=lambda c: c and "base-card" in c)
                if not cards:
                    # Alternative selector
                    cards = soup.find_all("li")

                batch_added = 0
                for card in cards:
                    if len(jobs) >= limit:
                        break

                    job_id = None
                    urn = card.get("data-entity-urn")
                    if urn and ":" in urn:
                        job_id = urn.split(":")[-1]

                    title_elem = card.find("h3", class_=lambda c: c and ("base-search-card__title" in c or "job-title" in c))
                    if not title_elem:
                        title_elem = card.find("h3")
                    title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"

                    company_elem = card.find("h4", class_=lambda c: c and ("base-search-card__subtitle" in c or "job-company" in c))
                    if not company_elem:
                        company_elem = card.find("h4")
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"

                    loc_elem = card.find("span", class_=lambda c: c and "job-search-card__location" in c)
                    location_text = loc_elem.get_text(strip=True) if loc_elem else location

                    link_elem = card.find("a", class_=lambda c: c and "base-card__full-link" in c)
                    if not link_elem:
                        link_elem = card.find("a")
                    url = link_elem.get("href") if link_elem else ""

                    if not job_id and url:
                        match = re.search(r"view/(\d+)", url) or re.search(r"currentJobId=(\d+)", url)
                        if match:
                            job_id = match.group(1)

                    if not job_id:
                        continue

                    # Clean tracking params from URL
                    clean_url = f"https://www.linkedin.com/jobs/view/{job_id}"

                    time_elem = card.find("time")
                    posted_date = time_elem.get("datetime") or time_elem.get_text(strip=True) if time_elem else None

                    posting = JobPosting(
                        id=job_id,
                        title=title,
                        company=company,
                        location=location_text,
                        url=clean_url,
                        source="linkedin",
                        employment_type="Contract" if contract else "Not Specified",
                        is_remote=remote,
                        posted_date=posted_date,
                    )
                    jobs.append(posting)
                    batch_added += 1

                if batch_added == 0:
                    break

                start += 25
            except Exception as e:
                logger.error(f"Error during LinkedIn search query: {e}")
                break

        return jobs

    def fetch_job_details(self, job_posting: JobPosting) -> JobPosting:
        """Fetches full job description HTML and transforms it into clean Markdown."""
        try:
            url = self.BASE_POSTING_URL.format(job_id=job_posting.id)
            response = self._get_with_retry(url)
            if not response or response.status_code != 200:
                logger.warning(f"Could not fetch details for job {job_posting.id}")
                return job_posting

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract full title and company
            title_elem = soup.find(class_=lambda c: c and ("topcard__title" in c or "top-card-layout__title" in c))
            if not title_elem:
                title_elem = soup.find("h2") or soup.find("h1")
            if title_elem:
                job_posting.title = title_elem.get_text(strip=True)

            flavor_row = soup.find(class_=lambda c: c and "topcard__flavor-row" in c)
            if flavor_row:
                comp_elem = flavor_row.find("a") or flavor_row.find(class_=lambda c: c and "topcard__flavor" in c)
                if comp_elem:
                    job_posting.company = comp_elem.get_text(strip=True)
                loc_elem = flavor_row.find(class_=lambda c: c and "topcard__flavor--bullet" in c)
                if loc_elem:
                    job_posting.location = loc_elem.get_text(strip=True)
            else:
                top_card = soup.find("div", class_=lambda c: c and "topcard__content-left" in c)
                if top_card:
                    c_elem = top_card.find("a")
                    if c_elem:
                        job_posting.company = c_elem.get_text(strip=True)

            # Extract criteria (Employment type, Seniority level, Job function, Industries)
            criteria_items = []
            criteria_list = soup.find("ul", class_=lambda c: c and "description__job-criteria-list" in c)
            if criteria_list:
                for item in criteria_list.find_all("li"):
                    subheader = item.find("h3")
                    val = item.find("span")
                    if subheader and val:
                        criteria_items.append(f"- **{subheader.get_text(strip=True)}**: {val.get_text(strip=True)}")

            # Extract main description
            desc_div = soup.find("div", class_=lambda c: c and "show-more-less-html__markup" in c)
            if not desc_div:
                desc_div = soup.find("section", class_=lambda c: c and "description" in c)

            if desc_div:
                # Clean and convert to markdown
                text_parts = []
                for elem in desc_div.descendants:
                    if elem.name in ["h1", "h2", "h3", "h4"]:
                        text_parts.append(f"\n### {elem.get_text(strip=True)}\n")
                    elif elem.name == "li":
                        text_parts.append(f"\n- {elem.get_text(strip=True)}")
                    elif elem.name == "p":
                        text_parts.append(f"\n\n{elem.get_text(strip=True)}")

                body_markdown = "".join(text_parts).strip()
                if not body_markdown:
                    body_markdown = desc_div.get_text("\n\n", strip=True)
            else:
                body_markdown = "No detailed description found."

            metadata_md = "\n".join(criteria_items) if criteria_items else ""
            full_description = f"{metadata_md}\n\n## Job Description\n\n{body_markdown}".strip()
            job_posting.description = full_description

        except Exception as e:
            logger.error(f"Failed to fetch details for job {job_posting.id}: {e}")

        return job_posting

    def fetch_from_url(self, url: str) -> Optional[JobPosting]:
        """Extracts job ID from a LinkedIn URL and fetches its full details."""
        match = re.search(r"view/(\d+)", url) or re.search(r"currentJobId=(\d+)", url) or re.search(r"/jobs/(\d+)", url)
        if not match:
            logger.error(f"Could not extract LinkedIn Job ID from URL: {url}")
            return None
        job_id = match.group(1)
        posting = JobPosting(
            id=job_id,
            title="Loading...",
            company="Loading...",
            location="Remote",
            url=f"https://www.linkedin.com/jobs/view/{job_id}",
            source="linkedin",
        )
        return self.fetch_job_details(posting)

    def close(self):
        self.client.close()
