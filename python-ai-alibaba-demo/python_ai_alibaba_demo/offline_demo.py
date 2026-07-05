from __future__ import annotations

from pathlib import Path

from .alibaba_application import create_controller
from .markdown_test import MarkdownDocumentParserConfig, parse_markdown
from .pdf_test import parse_pdf_pages


def main() -> None:
    resource_dir = Path(__file__).resolve().parents[1] / "resources"
    controller = create_controller(live=False)

    print("== Markdown parser ==")
    markdown_docs = parse_markdown(
        resource_dir / "markdown-test.md",
        MarkdownDocumentParserConfig(additional_metadata={"title": "zhouyu_title"}),
    )
    print(f"documents={len(markdown_docs)}")

    print("== PDF parser ==")
    print(parse_pdf_pages(resource_dir / "pdf-test.pdf")[0])

    print("== Baidu tool ==")
    print(controller.baidu("Spring AI Alibaba"))

    print("== Chat tool ==")
    print(controller.chat("北京现在几点"))

    print("== RAG advisor ==")
    print(controller.rag_advisor2("demo-chat", "API-KEY 上限是多少？"))

    print("== File chat ==")
    print(controller.file_chat("什么是API-KEY？"))


if __name__ == "__main__":
    main()
