"""Scrapers module for CareerOS Job Radar."""
from .linkedin import LinkedInGuestScraper
from .generic import GenericJobScraper

__all__ = ["LinkedInGuestScraper", "GenericJobScraper"]
