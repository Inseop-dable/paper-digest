"""arXiv API client for fetching papers"""

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import Any

import feedparser
import requests


ARXIV_API_URL = "http://export.arxiv.org/api/query"


@dataclass
class Paper:
    """Paper information from arXiv"""

    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    categories: list[str]
    published: str  # ISO format string
    updated: str    # ISO format string
    arxiv_url: str
    pdf_url: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_entry(cls, entry: dict) -> "Paper":
        """Create Paper from feedparser entry."""

        # Extract arxiv_id from entry.id
        # Format: http://arxiv.org/abs/2401.12345v1
        arxiv_id = entry.id.split("/abs/")[-1]
        # Remove version suffix (v1, v2, etc.)
        if "v" in arxiv_id:
            arxiv_id = arxiv_id.rsplit("v", 1)[0]

        # Extract authors
        authors = [author.get("name", "") for author in entry.get("authors", [])]

        # Extract categories
        categories = [tag.get("term", "") for tag in entry.get("tags", [])]

        # Clean title and abstract (remove newlines)
        title = entry.get("title", "").replace("\n", " ").strip()
        abstract = entry.get("summary", "").replace("\n", " ").strip()

        # Parse dates
        published = entry.get("published", "")
        updated = entry.get("updated", "")

        # Build URLs
        arxiv_url = entry.id
        pdf_url = entry.id.replace("/abs/", "/pdf/") + ".pdf"

        return cls(
            arxiv_id=arxiv_id,
            title=title,
            authors=authors,
            abstract=abstract,
            categories=categories,
            published=published,
            updated=updated,
            arxiv_url=arxiv_url,
            pdf_url=pdf_url,
        )


class ArxivFetcher:
    """Fetcher for arXiv papers using official API"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.timeout = config.get("advanced", {}).get("api_timeout", 30)
        self.debug = config.get("advanced", {}).get("debug", False)

    def fetch(self, query: str, max_results: int = 50) -> list[Paper]:
        """
        Fetch papers from arXiv API.

        Args:
            query: arXiv query string
            max_results: Maximum number of results to fetch

        Returns:
            List of Paper objects
        """
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        if self.debug:
            print(f"[DEBUG] arXiv query: {query}")
            print(f"[DEBUG] API URL: {ARXIV_API_URL}")

        try:
            response = requests.get(
                ARXIV_API_URL,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch from arXiv: {e}")
            return []

        # Parse Atom feed
        feed = feedparser.parse(response.text)

        if self.debug:
            print(f"[DEBUG] Found {len(feed.entries)} entries")

        # Convert to Paper objects
        papers = []
        for entry in feed.entries:
            try:
                paper = Paper.from_entry(entry)
                papers.append(paper)
            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] Failed to parse entry: {e}")
                continue

        return papers

    def filter_by_date(
        self,
        papers: list[Paper],
        days: int = 7,
    ) -> list[Paper]:
        """
        Filter papers to only include recent ones.

        Args:
            papers: List of papers to filter
            days: Only include papers from last N days

        Returns:
            Filtered list of papers
        """
        if days <= 0:
            return papers

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        filtered = []

        for paper in papers:
            try:
                # Parse published date
                # Format: 2024-01-15T12:34:56Z
                pub_date = datetime.fromisoformat(
                    paper.published.replace("Z", "+00:00")
                )

                if pub_date >= cutoff:
                    filtered.append(paper)
            except (ValueError, AttributeError):
                # Include paper if date parsing fails
                filtered.append(paper)

        return filtered

    def fetch_recent(self, query: str) -> list[Paper]:
        """
        Fetch recent papers based on configuration.

        Args:
            query: arXiv query string

        Returns:
            List of recent papers
        """
        selection = self.config.get("selection", {})
        max_candidates = selection.get("max_candidates", 50)
        days_recent = selection.get("days_recent", 7)

        # Build date range query
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days_recent)
        date_query = f"submittedDate:[{start_date.strftime('%Y%m%d')}0000 TO {end_date.strftime('%Y%m%d')}2359]"

        # Combine with original query
        full_query = f"({query}) AND {date_query}"

        if self.debug:
            print(f"[DEBUG] Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            print(f"[DEBUG] Full query: {full_query}")

        # Fetch papers with date range in query
        papers = self.fetch(full_query, max_results=max_candidates)

        # Double-check with Python filter (in case API date filtering is imprecise)
        papers = self.filter_by_date(papers, days=days_recent)

        if self.debug:
            print(f"[DEBUG] After date filter: {len(papers)} papers")

        return papers
