"""Generic Web Job Scraper for CareerOS Job Radar."""
import hashlib
import logging
import re
from typing import Optional
import httpx
from bs4 import BeautifulSoup

from ..models import JobPosting

logger = logging.getLogger(__name__)

class GenericJobScraper:
    """Scrapes job descriptions from arbitrary web pages (Free-Work, Indeed, Career Sites)."""

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self.client = httpx.Client(headers=self.DEFAULT_HEADERS, timeout=self.timeout, follow_redirects=True)

    def fetch_from_url(self, url: str) -> Optional[JobPosting]:
        """Fetches and extracts a job posting from an arbitrary job board URL."""
        try:
            response = self.client.get(url)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {url} (Status: {response.status_code})")
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove noise elements
            for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
                tag.decompose()

            # Attempt title extraction
            title = "Job Opportunity"
            title_tag = soup.find("h1") or soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True)
                title = re.sub(r"\s*[-|]\s*.*$", "", title)  # Strip site name suffix

            # Attempt company extraction
            company = "Direct Employer"
            for selector in [".company-name", ".employer", "[data-company]", ".company"]:
                comp_tag = soup.select_one(selector)
                if comp_tag:
                    company = comp_tag.get_text(strip=True)
                    break

            # Attempt location extraction
            location = "Remote / Flexible"
            for selector in [".location", "[data-location]", ".job-location"]:
                loc_tag = soup.select_one(selector)
                if loc_tag:
                    location = loc_tag.get_text(strip=True)
                    break

            # Extract main content container
            content_container = (
                soup.find("article")
                or soup.find("main")
                or soup.find("div", class_=lambda c: c and any(k in c.lower() for k in ["job-desc", "description", "details", "content"]))
                or soup.body
            )

            lines = []
            if content_container:
                for elem in content_container.descendants:
                    if elem.name in ["h1", "h2", "h3"]:
                        lines.append(f"\n### {elem.get_text(strip=True)}\n")
                    elif elem.name == "li":
                        lines.append(f"\n- {elem.get_text(strip=True)}")
                    elif elem.name == "p":
                        lines.append(f"\n\n{elem.get_text(strip=True)}")
                description = "".join(lines).strip()
            else:
                description = soup.get_text("\n", strip=True)

            job_id = hashlib.md5(url.encode("utf-8")).hexdigest()[:12]

            return JobPosting(
                id=f"web_{job_id}",
                title=title,
                company=company,
                location=location,
                url=url,
                source="web",
                description=description[:15000],  # cap length
            )
        except Exception as e:
            logger.error(f"Error extracting generic job from {url}: {e}")
            return None

    def close(self):
        self.client.close()
