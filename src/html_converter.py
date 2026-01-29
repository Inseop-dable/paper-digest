"""HTML converter for Paper Digest markdown files"""

from pathlib import Path
from typing import Optional

import markdown


class HTMLConverter:
    """Convert markdown digest to HTML with styling"""

    def __init__(self):
        self.css = """
            body {
                max-width: 900px;
                margin: 40px auto;
                padding: 20px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                             "Noto Sans KR", "Malgun Gothic", sans-serif;
                font-size: 16px;
                line-height: 1.7;
                color: #333;
                background: #fff;
            }

            @media print {
                body {
                    max-width: 100%;
                    margin: 0;
                }
            }

            h1 {
                font-size: 2em;
                margin-top: 0;
                margin-bottom: 0.5em;
                color: #1a1a1a;
                border-bottom: 3px solid #3498db;
                padding-bottom: 0.3em;
            }

            h2 {
                font-size: 1.5em;
                margin-top: 2em;
                margin-bottom: 0.5em;
                color: #2c3e50;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 0.2em;
            }

            h3 {
                font-size: 1.2em;
                margin-top: 1.5em;
                margin-bottom: 0.5em;
                color: #34495e;
            }

            p {
                margin: 0.8em 0;
            }

            strong {
                color: #2c3e50;
                font-weight: 600;
            }

            a {
                color: #3498db;
                text-decoration: none;
            }

            a:hover {
                text-decoration: underline;
            }

            code {
                background-color: #f5f5f5;
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-family: "SF Mono", Monaco, "Courier New", monospace;
                font-size: 0.9em;
                color: #e74c3c;
            }

            hr {
                border: none;
                border-top: 2px solid #e0e0e0;
                margin: 2em 0;
            }

            blockquote {
                margin: 1em 0;
                padding-left: 1em;
                border-left: 4px solid #3498db;
                color: #555;
                font-style: italic;
                background: #f9f9f9;
                padding: 0.5em 1em;
            }

            ul, ol {
                margin: 0.8em 0;
                padding-left: 2em;
            }

            li {
                margin: 0.4em 0;
            }

            /* arXiv 링크 스타일 */
            a[href*="arxiv.org"] {
                font-weight: 500;
                color: #2ecc71;
            }

            /* 프린트 최적화 */
            @media print {
                a {
                    color: #000;
                    text-decoration: underline;
                }
            }
        """

    def convert(
        self,
        md_path: str,
        html_path: Optional[str] = None,
        custom_css: Optional[str] = None
    ) -> str:
        """
        Convert markdown file to HTML.

        Args:
            md_path: Path to markdown file
            html_path: Output HTML path (default: same as md_path with .html extension)
            custom_css: Optional custom CSS string

        Returns:
            Path to generated HTML file
        """
        md_file = Path(md_path)

        if not md_file.exists():
            raise FileNotFoundError(f"Markdown file not found: {md_path}")

        # Determine output path
        if html_path is None:
            html_file = md_file.with_suffix('.html')
        else:
            html_file = Path(html_path)

        # Read markdown content
        md_content = md_file.read_text(encoding='utf-8')

        # Convert markdown to HTML
        html_body = markdown.markdown(
            md_content,
            extensions=[
                'extra',      # Tables, footnotes, etc.
                'nl2br',      # Newline to <br>
                'sane_lists', # Better list handling
            ]
        )

        # Wrap in HTML document
        css_to_use = custom_css if custom_css else self.css
        full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paper Digest</title>
    <style>
{css_to_use}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""

        # Write HTML file
        html_file.write_text(full_html, encoding='utf-8')

        return str(html_file)
