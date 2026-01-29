"""Claude CLI runner for paper selection and summarization"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


class ClaudeRunner:
    """Runner for Claude CLI to select and summarize papers"""

    def __init__(self, config: dict[str, Any], project_root: Path):
        self.config = config
        self.project_root = project_root
        self.debug = config.get("advanced", {}).get("debug", False)

        # Paths
        self.prompt_template_path = project_root / "src" / "prompts" / "select_and_summarize.md"
        self.temp_dir = project_root / ".tmp"
        self.candidates_path = self.temp_dir / "candidates.json"
        self.prompt_path = self.temp_dir / "prompt.md"

    def save_candidates(self, papers: list) -> None:
        """
        Save candidate papers to temp file for Claude to read.

        Args:
            papers: List of Paper objects
        """
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        candidates = [p.to_dict() for p in papers]

        with open(self.candidates_path, "w", encoding="utf-8") as f:
            json.dump(candidates, f, indent=2, ensure_ascii=False)

        if self.debug:
            print(f"[DEBUG] Saved {len(candidates)} candidates to {self.candidates_path}")

    def _build_interests_section(self) -> str:
        """Build the interests section for the prompt."""
        interests = self.config.get("interests", {})
        venues = self.config.get("venues", {})
        authors = self.config.get("authors", [])

        lines = []

        # Categories
        categories = interests.get("categories", [])
        if categories:
            lines.append(f"- **분야 (arXiv 카테고리)**: {', '.join(categories)}")

        # Keywords
        keywords = interests.get("keywords", [])
        if keywords:
            lines.append(f"- **키워드**: {', '.join(keywords)}")

        # Venues
        conferences = venues.get("conferences", [])
        if conferences:
            lines.append(f"- **관심 학회**: {', '.join(conferences)}")

        journals = venues.get("journals", [])
        if journals:
            lines.append(f"- **관심 저널**: {', '.join(journals)}")

        # Authors
        if authors:
            lines.append(f"- **관심 저자**: {', '.join(authors)}")

        return "\n".join(lines) if lines else "- 특별한 조건 없음"

    def _build_prompt(self) -> str:
        """Build the complete prompt for Claude."""
        # Read template
        with open(self.prompt_template_path, "r", encoding="utf-8") as f:
            template = f.read()

        # Get values
        selection = self.config.get("selection", {})
        num_papers = selection.get("num_papers", 2)

        output = self.config.get("output", {})
        output_dir = output.get("directory", "./digests")
        filename_format = output.get("filename_format", "%Y-%m-%d")

        today = datetime.now()
        filename = today.strftime(filename_format) + ".md"
        output_path = f"{output_dir}/{filename}"

        # Get keywords for practical implications section
        interests = self.config.get("interests", {})
        keywords = interests.get("keywords", [])
        interests_keywords = ", ".join(keywords[:5]) if keywords else "사용자 관심 분야"

        # Replace placeholders
        prompt = template.format(
            interests_section=self._build_interests_section(),
            num_papers=num_papers,
            output_path=output_path,
            date=today.strftime("%Y년 %m월 %d일"),
            interests_keywords=interests_keywords,
        )

        return prompt

    def run(self) -> tuple[bool, list[str]]:
        """
        Run Claude CLI to select and summarize papers.

        Returns:
            Tuple of (success, list of selected arxiv_ids)
        """
        # Build and save prompt
        prompt = self._build_prompt()

        self.temp_dir.mkdir(parents=True, exist_ok=True)
        with open(self.prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)

        if self.debug:
            print(f"[DEBUG] Prompt saved to {self.prompt_path}")

        # Get model
        model = self.config.get("summary", {}).get("model", "sonnet")

        # Build command
        cmd = [
            "claude",
            "-p",  # print mode (non-interactive)
            "--model", model,
            "--allowedTools", "Read,Write",
            "--max-turns", "10",
            prompt,
        ]

        if self.debug:
            print(f"[DEBUG] Running command: {' '.join(cmd[:6])}...")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout for detailed summaries
                cwd=str(self.project_root),
            )

            if result.returncode != 0:
                print(f"[ERROR] Claude CLI failed: {result.stderr}")
                return False, []

            if self.debug:
                print(f"[DEBUG] Claude output length: {len(result.stdout)}")

        except subprocess.TimeoutExpired:
            print("[ERROR] Claude CLI timed out")
            return False, []
        except FileNotFoundError:
            print("[ERROR] Claude CLI not found. Please install it first.")
            return False, []
        except Exception as e:
            print(f"[ERROR] Failed to run Claude CLI: {e}")
            return False, []

        # Extract selected paper IDs from output file
        selected_ids = self._extract_selected_ids()

        return True, selected_ids

    def _extract_selected_ids(self) -> list[str]:
        """
        Extract selected paper IDs from the output file.

        The output file should contain a comment like:
        <!-- SELECTED_PAPERS: ["2401.12345", "2401.67890"] -->

        Returns:
            List of arxiv IDs
        """
        output = self.config.get("output", {})
        output_dir = output.get("directory", "./digests")
        filename_format = output.get("filename_format", "%Y-%m-%d")

        today = datetime.now()
        filename = today.strftime(filename_format) + ".md"
        output_path = self.project_root / output_dir / filename

        if not output_path.exists():
            if self.debug:
                print(f"[DEBUG] Output file not found: {output_path}")
            return []

        try:
            content = output_path.read_text(encoding="utf-8")

            # Look for the SELECTED_PAPERS comment
            match = re.search(
                r'<!--\s*SELECTED_PAPERS:\s*(\[.*?\])\s*-->',
                content,
                re.DOTALL,
            )

            if match:
                ids = json.loads(match.group(1))
                return ids

        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Failed to extract selected IDs: {e}")

        return []
