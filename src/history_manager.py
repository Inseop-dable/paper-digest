"""History manager for tracking seen papers"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class HistoryManager:
    """Manager for tracking papers that have been seen/summarized"""

    def __init__(self, history_file: str, retention_days: int = 90):
        """
        Initialize history manager.

        Args:
            history_file: Path to history JSON file
            retention_days: Days to keep history (0 = unlimited)
        """
        self.history_file = Path(history_file)
        self.retention_days = retention_days
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        """Load history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        return {"papers": {}, "last_updated": None}

    def _save(self) -> None:
        """Save history to file."""
        # Ensure directory exists
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        self.data["last_updated"] = datetime.now().isoformat()

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def is_seen(self, arxiv_id: str) -> bool:
        """
        Check if a paper has been seen before.

        Args:
            arxiv_id: arXiv paper ID

        Returns:
            True if paper has been seen
        """
        return arxiv_id in self.data["papers"]

    def mark_seen(self, arxiv_id: str, title: str) -> None:
        """
        Mark a paper as seen.

        Args:
            arxiv_id: arXiv paper ID
            title: Paper title
        """
        self.data["papers"][arxiv_id] = {
            "title": title,
            "seen_at": datetime.now().isoformat(),
        }
        self._save()

    def mark_multiple_seen(self, papers: list[dict[str, str]]) -> None:
        """
        Mark multiple papers as seen.

        Args:
            papers: List of dicts with 'arxiv_id' and 'title' keys
        """
        now = datetime.now().isoformat()

        for paper in papers:
            arxiv_id = paper.get("arxiv_id", "")
            title = paper.get("title", "")

            if arxiv_id:
                self.data["papers"][arxiv_id] = {
                    "title": title,
                    "seen_at": now,
                }

        self._save()

    def filter_unseen(self, papers: list) -> list:
        """
        Filter out papers that have been seen.

        Args:
            papers: List of Paper objects (with arxiv_id attribute)

        Returns:
            List of unseen papers
        """
        return [p for p in papers if not self.is_seen(p.arxiv_id)]

    def cleanup_old_entries(self) -> int:
        """
        Remove entries older than retention period.

        Returns:
            Number of entries removed
        """
        if self.retention_days <= 0:
            return 0

        cutoff = datetime.now() - timedelta(days=self.retention_days)
        papers = self.data["papers"]

        to_remove = []
        for arxiv_id, info in papers.items():
            try:
                seen_at = datetime.fromisoformat(info["seen_at"])
                if seen_at < cutoff:
                    to_remove.append(arxiv_id)
            except (KeyError, ValueError):
                continue

        for arxiv_id in to_remove:
            del papers[arxiv_id]

        if to_remove:
            self._save()

        return len(to_remove)

    def get_stats(self) -> dict[str, Any]:
        """
        Get history statistics.

        Returns:
            Dictionary with stats
        """
        return {
            "total_papers": len(self.data["papers"]),
            "last_updated": self.data.get("last_updated"),
        }
