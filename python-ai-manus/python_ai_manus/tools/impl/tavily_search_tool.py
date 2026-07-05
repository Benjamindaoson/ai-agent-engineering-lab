import json
import os
import urllib.request
from typing import Any

from python_ai_manus.tools.base_tool import BaseTool
from python_ai_manus.tools.tool_result import ToolResult


class TavilySearchTool(BaseTool):
    def __init__(self):
        super().__init__("tavily_search", "Search the web for information using Tavily search engine")

    def get_parameters_schema(self) -> dict[str, Any]:
        return self.build_schema(
            {
                "query": self.string_param("The search query to execute"),
                "max_results": self.int_param("Maximum number of search results to return"),
            },
            ["query"],
        )

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        query = self.get_string(parameters, "query")
        if not query:
            return ToolResult.failure("query is required")
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return ToolResult.failure("TAVILY_API_KEY environment variable is required")

        payload = json.dumps(
            {
                "api_key": api_key,
                "query": query,
                "max_results": self.get_integer(parameters, "max_results", 5),
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            "https://api.tavily.com/search",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
            return ToolResult.success(
                {
                    "query": query,
                    "total_results": len(data.get("results", [])),
                    "results": [
                        {
                            "title": item.get("title"),
                            "url": item.get("url"),
                            "snippet": item.get("content") or item.get("snippet"),
                        }
                        for item in data.get("results", [])
                    ],
                }
            )
        except Exception as exc:
            # ponytail: live search is optional for offline demos; return an explicit tool error.
            return ToolResult.failure(f"Search failed: {exc}")
