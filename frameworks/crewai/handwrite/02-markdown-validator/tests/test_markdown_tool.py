from pathlib import Path

from markdown_validator.tools.markdownTools import MarkdownValidationTool


def test_reports_required_markdown_issues(tmp_path: Path) -> None:
    path = tmp_path / "bad.md"
    path.write_text(
        "# One\n### Three  \n#\n# One\nhttp://example.com\n![ ](image.png)\n```python\n",
        encoding="utf-8",
    )

    report = MarkdownValidationTool()._run(str(path))

    for issue in (
        "heading-level-jump",
        "empty-heading",
        "duplicate-heading",
        "unclosed-code-fence",
        "trailing-spaces",
        "bare-url",
        "empty-image-alt",
    ):
        assert issue in report
    assert "line 2" in report


def test_reports_missing_and_non_markdown_files(tmp_path: Path) -> None:
    tool = MarkdownValidationTool()
    assert "does not exist" in tool._run(str(tmp_path / "missing.md"))
    text = tmp_path / "notes.txt"
    text.write_text("plain", encoding="utf-8")
    assert "not a Markdown file" in tool._run(str(text))


def test_reports_clean_markdown(tmp_path: Path) -> None:
    path = tmp_path / "good.md"
    path.write_text("# Title\n\n## Section\n\nText.\n", encoding="utf-8")
    assert "No markdown validation issues found" in MarkdownValidationTool()._run(str(path))
