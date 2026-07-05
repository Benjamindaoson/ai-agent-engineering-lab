from __future__ import annotations

from pathlib import Path

from .simple_ai import Document


def parse_pdf_pages(path: str | Path, *, bottom_text_lines_to_delete: int = 3) -> list[Document]:
    pdf_path = Path(path)
    data = pdf_path.read_bytes()
    if not data.startswith(b"%PDF"):
        raise ValueError(f"{pdf_path} is not a PDF file")
    return [
        Document(
            f"PDF binary document: {pdf_path.name} ({len(data)} bytes). "
            "Text extraction needs an optional PDF parser in live integrations.",
            {
                "source": str(pdf_path),
                "page": 1,
                "parser": "stdlib-placeholder",
                "bottom_text_lines_to_delete": bottom_text_lines_to_delete,
                "bytes": len(data),
            },
        )
    ]


def main() -> None:
    resource = Path(__file__).resolve().parents[1] / "resources" / "pdf-test.pdf"
    documents = parse_pdf_pages(resource)
    print(f"文档数量：{len(documents)}")
    for document in documents:
        print(document)


if __name__ == "__main__":
    main()
