from __future__ import annotations

from pathlib import Path

from .alibaba_application import create_controller
from .markdown_test import MarkdownDocumentParserConfig, parse_markdown
from .pdf_test import parse_pdf_pages


def main() -> None:
    resource_dir = Path(__file__).resolve().parents[1] / "resources"
    assert len(parse_markdown(resource_dir / "markdown-test.md", MarkdownDocumentParserConfig())) == 2
    assert len(parse_pdf_pages(resource_dir / "pdf-test.pdf")) == 1
    controller = create_controller(live=False)
    assert "getCityTimeFunction" in controller.chat("北京现在几点")
    assert controller.baidu("Spring AI Alibaba")["request"]["top_k"] == 10
    assert "API-KEY" in controller.rank_chat("API-KEY 如何鉴权")
    assert "DashScope" in controller.file_chat("什么是API-KEY")
    print("python-ai-alibaba-demo self check passed")


if __name__ == "__main__":
    main()
