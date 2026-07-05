import json
import os
import urllib.request


class TavilySearchTool:
    name = "tavilySearch"

    def search(self, query: str, max_results: int = 3) -> list[dict]:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return [{"title": "Tavily disabled", "url": "", "snippet": "TAVILY_API_KEY is not set"}]
        payload = json.dumps({"api_key": api_key, "query": query, "max_results": max_results}).encode("utf-8")
        request = urllib.request.Request(
            "https://api.tavily.com/search",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        return [
            {"title": item.get("title"), "url": item.get("url"), "snippet": item.get("content") or item.get("snippet")}
            for item in data.get("results", [])
        ]
