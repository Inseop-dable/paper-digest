"""macOS notification system for Paper Digest"""

import platform
import subprocess
from typing import Any


class Notifier:
    """Cross-platform notifier (currently macOS only)"""

    def __init__(self, config: dict[str, Any]):
        notification = config.get("notification", {})

        self.enabled = notification.get("enabled", True)
        self.sound = notification.get("sound", "Glass")
        self.title = "Paper Digest"

        # Check if we're on macOS
        self.is_macos = platform.system() == "Darwin"

    def _escape(self, text: str) -> str:
        """Escape text for AppleScript."""
        return text.replace("\\", "\\\\").replace('"', '\\"')

    def notify(self, message: str, subtitle: str = "") -> bool:
        """
        Show a notification.

        Args:
            message: Main notification message
            subtitle: Optional subtitle

        Returns:
            True if notification was shown
        """
        if not self.enabled:
            return False

        if not self.is_macos:
            # On non-macOS, just print to console
            print(f"[NOTIFICATION] {self.title}: {message}")
            if subtitle:
                print(f"  {subtitle}")
            return True

        # Build AppleScript command
        script_parts = [f'display notification "{self._escape(message)}"']
        script_parts.append(f'with title "{self._escape(self.title)}"')

        if subtitle:
            script_parts.append(f'subtitle "{self._escape(subtitle)}"')

        if self.sound:
            script_parts.append(f'sound name "{self.sound}"')

        script = " ".join(script_parts)

        try:
            subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                timeout=5,
            )
            return True
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False

    def notify_digest_ready(self, num_papers: int, output_path: str) -> bool:
        """
        Notify that digest is ready.

        Args:
            num_papers: Number of papers summarized
            output_path: Path to output file

        Returns:
            True if notification was shown
        """
        message = f"{num_papers}개의 논문이 요약되었습니다"
        subtitle = f"저장 위치: {output_path}"

        return self.notify(message, subtitle)

    def notify_no_papers(self) -> bool:
        """
        Notify that no new papers were found.

        Returns:
            True if notification was shown
        """
        return self.notify("오늘은 새로운 관심 논문이 없습니다")

    def notify_error(self, error_message: str) -> bool:
        """
        Notify about an error.

        Args:
            error_message: Error description

        Returns:
            True if notification was shown
        """
        return self.notify(f"오류 발생: {error_message}")
