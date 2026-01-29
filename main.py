#!/usr/bin/env python3
"""
Paper Digest - Automated paper summarization using arXiv and Claude

Usage:
    python main.py [--config CONFIG] [--dry-run] [--debug]
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from src.config_loader import load_config, get_arxiv_query
from src.arxiv_fetcher import ArxivFetcher
from src.history_manager import HistoryManager
from src.claude_runner import ClaudeRunner
from src.notifier import Notifier
from src.html_converter import HTMLConverter


def main() -> int:
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Paper Digest - Automated paper summarization"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Search papers only, don't run summarization",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output",
    )

    args = parser.parse_args()

    # Get project root (directory containing this script)
    project_root = Path(__file__).parent.resolve()

    # Load configuration
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading configuration...")

    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 1
    except ValueError as e:
        print(f"[ERROR] Invalid configuration: {e}")
        return 1

    # Override debug setting if passed as argument
    if args.debug:
        config.setdefault("advanced", {})["debug"] = True

    debug = config.get("advanced", {}).get("debug", False)

    # Initialize components
    history_file = config.get("advanced", {}).get("history_file", "./.tmp/history.json")
    history_path = project_root / history_file
    retention_days = config.get("advanced", {}).get("history_retention_days", 90)

    history = HistoryManager(str(history_path), retention_days)
    fetcher = ArxivFetcher(config)
    notifier = Notifier(config)

    # Cleanup old history entries
    removed = history.cleanup_old_entries()
    if removed > 0 and debug:
        print(f"[DEBUG] Cleaned up {removed} old history entries")

    # Build query and fetch papers
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching papers from arXiv...")

    query = get_arxiv_query(config)
    if debug:
        print(f"[DEBUG] Query: {query}")

    papers = fetcher.fetch_recent(query)
    print(f"  Found {len(papers)} candidate papers")

    if not papers:
        print("[INFO] No papers found matching your criteria")
        notifier.notify_no_papers()
        return 0

    # Filter out already seen papers
    unseen_papers = history.filter_unseen(papers)
    print(f"  After filtering seen papers: {len(unseen_papers)} new papers")

    if not unseen_papers:
        print("[INFO] All matching papers have been seen before")
        notifier.notify_no_papers()
        return 0

    # Show candidates in dry-run mode
    if args.dry_run:
        print("\n[DRY RUN] Candidate papers:")
        for i, paper in enumerate(unseen_papers[:10], 1):
            print(f"  {i}. {paper.title[:70]}...")
            print(f"     ID: {paper.arxiv_id} | Published: {paper.published[:10]}")
        print("\n[DRY RUN] Skipping summarization")
        return 0

    # Run Claude for selection and summarization
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running Claude for selection and summarization...")

    runner = ClaudeRunner(config, project_root)
    runner.save_candidates(unseen_papers)

    success, selected_ids = runner.run()

    if not success:
        print("[ERROR] Claude summarization failed")
        notifier.notify_error("요약 생성 실패")
        return 1

    # Mark selected papers as seen
    if selected_ids:
        papers_to_mark = []
        for paper in unseen_papers:
            if paper.arxiv_id in selected_ids:
                papers_to_mark.append({
                    "arxiv_id": paper.arxiv_id,
                    "title": paper.title,
                })

        history.mark_multiple_seen(papers_to_mark)
        print(f"  Marked {len(papers_to_mark)} papers as seen")

    # Get output path for notification
    output = config.get("output", {})
    output_dir = output.get("directory", "./digests")
    filename_format = output.get("filename_format", "%Y-%m-%d")
    filename = datetime.now().strftime(filename_format) + ".md"
    output_path = f"{output_dir}/{filename}"

    # Generate HTML if enabled
    html_enabled = output.get("html_enabled", True)
    html_path = None

    if html_enabled:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Generating HTML...")
        try:
            converter = HTMLConverter()
            html_path = converter.convert(output_path)
            print(f"  HTML saved to: {html_path}")
        except Exception as e:
            print(f"  [WARNING] HTML generation failed: {e}")
            if debug:
                import traceback
                traceback.print_exc()

    # Notify completion
    num_papers = len(selected_ids) if selected_ids else config.get("selection", {}).get("num_papers", 2)
    notifier.notify_digest_ready(num_papers, output_path)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Done!")
    print(f"  Markdown saved to: {output_path}")
    if html_path:
        print(f"  HTML saved to: {html_path}")
        print(f"  → Open in browser: open {html_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
