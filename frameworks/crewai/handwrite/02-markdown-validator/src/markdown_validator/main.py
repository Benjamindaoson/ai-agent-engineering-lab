from __future__ import annotations

import sys

from dotenv import load_dotenv

from markdown_validator.crew import MarkdownValidatorCrew


def run():
    load_dotenv()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 2:
        print("Usage: uv run markdown_validator examples/bad_markdown.md")
        return None

    filename = sys.argv[1]
    inputs = {"filename": filename}
    result = MarkdownValidatorCrew().crew().kickoff(inputs=inputs)
    print(result)


if __name__ == "__main__":
    run()
