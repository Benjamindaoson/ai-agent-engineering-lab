from __future__ import annotations

import re
from pathlib import Path

from crewai.tools import BaseTool


class MarkdownValidationTool(BaseTool):
    name: str = "markdown_validation_tool"
    description: str = "Check one Markdown file for common quality issues without modifying it."

    def _run(self, file_path: str) -> str:
        path = Path(file_path.strip())
        if not path.exists():
            return f"Error: file does not exist: {path}"
        if not path.is_file():
            return f"Error: path is not a file: {path}"
        if path.suffix.lower() != ".md":
            return f"Warning: not a Markdown file: {path}"

        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            return f"Error: could not read {path}: {exc}"

        if not text.strip():
            return "line 1: empty-file - Markdown file is empty."

        findings: list[str] = []
        headings: dict[str, int] = {}
        previous_level = 0
        fence: str | None = None
        lines = text.splitlines()

        for line_number, line in enumerate(lines, start=1):
            if line.endswith((" ", "\t")):
                findings.append(f"line {line_number}: trailing-spaces - Line has trailing whitespace.")

            fence_match = re.match(r"^\s*(`{3,}|~{3,})", line)
            if fence_match:
                marker = fence_match.group(1)[0]
                fence = None if fence == marker else marker
                continue
            if fence:
                continue

            heading_match = re.match(r"^ {0,3}(#{1,6})(?:[ \t]+(.*)|[ \t]*)$", line)
            if heading_match:
                level = len(heading_match.group(1))
                title = (heading_match.group(2) or "").strip().rstrip("#").strip()
                if not title:
                    findings.append(f"line {line_number}: empty-heading - Heading has no text.")
                if previous_level and level > previous_level + 1:
                    findings.append(
                        f"line {line_number}: heading-level-jump - Heading jumps from H{previous_level} to H{level}."
                    )
                previous_level = level
                key = title.casefold()
                if title and key in headings:
                    findings.append(
                        f"line {line_number}: duplicate-heading - Heading repeats line {headings[key]}."
                    )
                elif title:
                    headings[key] = line_number

            if re.search(r"(?<![\[(])https?://[^\s)>]+", line):
                findings.append(f"line {line_number}: bare-url - URL should be part of a Markdown link.")
            if re.search(r"!\[\s*\]\([^)]*\)", line):
                findings.append(f"line {line_number}: empty-image-alt - Image alt text is empty.")

        if fence:
            findings.append("line 1: unclosed-code-fence - Fenced code block is not closed.")

        return "No markdown validation issues found." if not findings else "\n".join(findings)


markdown_validation_tool = MarkdownValidationTool()
