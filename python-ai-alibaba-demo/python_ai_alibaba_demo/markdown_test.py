from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .simple_ai import Document


@dataclass(frozen=True)
class MarkdownDocumentParserConfig:
    additional_metadata: dict[str, object] = field(default_factory=dict)
    include_code_block: bool = True
    include_blockquote: bool = True
    horizontal_rule_create_document: bool = True


def parse_markdown(path: str | Path, config: MarkdownDocumentParserConfig | None = None) -> list[Document]:
    parser_config = config or MarkdownDocumentParserConfig()
    text = Path(path).read_text(encoding="utf-8")
    chunks = _split_on_horizontal_rule(text) if parser_config.horizontal_rule_create_document else [text]
    return [
        Document(_filter_markdown(chunk, parser_config).strip(), dict(parser_config.additional_metadata))
        for chunk in chunks
        if _filter_markdown(chunk, parser_config).strip()
    ]


def _split_on_horizontal_rule(text: str) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.strip() in {"---", "***", "___"}:
            chunks.append("\n".join(current))
            current = []
        else:
            current.append(line)
    chunks.append("\n".join(current))
    return chunks


def _filter_markdown(text: str, config: MarkdownDocumentParserConfig) -> str:
    lines: list[str] = []
    inside_code = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            inside_code = not inside_code
            if config.include_code_block:
                lines.append(line)
            continue
        if inside_code and not config.include_code_block:
            continue
        if line.lstrip().startswith(">") and not config.include_blockquote:
            continue
        lines.append(line)
    return "\n".join(lines)


def main() -> None:
    resource = Path(__file__).resolve().parents[1] / "resources" / "markdown-test.md"
    config = MarkdownDocumentParserConfig(additional_metadata={"title": "zhouyu_title"})
    for document in parse_markdown(resource, config):
        print(document)


if __name__ == "__main__":
    main()
