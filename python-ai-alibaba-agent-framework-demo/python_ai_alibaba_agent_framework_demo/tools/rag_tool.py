from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RagTool:
    documents: list[str]

    def rag_tool(self, query: str) -> list[str]:
        query_lower = query.lower()
        return [doc for doc in self.documents if any(word in doc.lower() for word in query_lower.split())] or self.documents[:1]

    def __call__(self, input_text: str, tool_context: dict[str, object]) -> str:
        return " | ".join(self.rag_tool(input_text))
