from dataclasses import dataclass
from typing import Any

from python_ai_manus.model import Message, RelevanceFilter, ToolDefinition

from .tool import Tool
from .tool_result import ToolResult


class ToolCollection:
    def __init__(self):
        self.tools: dict[str, Tool] = {}
        self.relevance_filter: RelevanceFilter | None = None
        self.relevance_threshold = 0.3

    def add_tool(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def get_tool_definitions(self) -> list[ToolDefinition]:
        return [tool.to_definition() for tool in self.tools.values()]

    def get_relevant_tool_definitions(self, query: str | None) -> list[ToolDefinition]:
        if self.relevance_filter is None or query is None or not query.strip():
            return self.get_tool_definitions()

        all_tools = self.get_tool_definitions()
        scored = []
        for tool in all_tools:
            score = self.relevance_filter.calculate_relevance(
                Message.assistant_message(f"{tool.name} {tool.description}"),
                query,
            )
            if score >= self.relevance_threshold:
                scored.append(_ToolScore(tool, score))
        scored.sort(key=lambda item: item.score, reverse=True)
        return [item.tool for item in scored] or all_tools

    def execute_tool(self, tool_name: str, parameters: dict[str, Any]) -> ToolResult:
        tool = self.tools.get(tool_name)
        if tool is None:
            return ToolResult.failure(f"Tool not found: {tool_name}")
        return tool.execute(parameters)


@dataclass
class _ToolScore:
    tool: ToolDefinition
    score: float
