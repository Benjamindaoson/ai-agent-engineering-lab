import os
import shutil
import tempfile
from pathlib import Path

from python_ai_manus.tools.impl import BrowserTool, SandboxTool, TavilySearchTool


def _line(name: str, status: str, detail: str) -> str:
    return f"{name}: {status} - {detail}"


def check_tavily() -> str:
    if not os.getenv("TAVILY_API_KEY"):
        return _line("tavily_search", "SKIP", "TAVILY_API_KEY is not set")
    result = TavilySearchTool().execute({"query": "OpenAI", "max_results": 1})
    if result.is_success():
        total = result.output.get("total_results", 0) if isinstance(result.output, dict) else "unknown"
        return _line("tavily_search", "PASS", f"returned {total} result(s)")
    return _line("tavily_search", "FAIL", result.error or "unknown error")


def check_docker() -> str:
    if not shutil.which("docker"):
        return _line("sandbox", "SKIP", "docker command is not available")
    tool = SandboxTool()
    try:
        result = tool.execute({"action": "execute", "language": "python", "code": "print(2 + 3)"})
        if result.is_success() and "5" in str(result.output):
            return _line("sandbox", "PASS", "executed Python code in Docker")
        return _line("sandbox", "FAIL", result.error or str(result.output))
    finally:
        tool.cleanup()


def check_playwright() -> str:
    tool = BrowserTool()
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            html = Path(temp_dir) / "smoke.html"
            html.write_text("<html><body><h1>playwright smoke ok</h1></body></html>", encoding="utf-8")
            nav = tool.execute({"action": "navigate", "url": html.as_uri()})
            if nav.has_error():
                return _line("browser", "FAIL", nav.error or "navigate failed")
            content = tool.execute({"action": "get_content"})
            if content.has_error() or "playwright smoke ok" not in str(content.output):
                return _line("browser", "FAIL", content.error or "content check failed")
            screenshot = tool.execute({"action": "screenshot"})
            if screenshot.has_error() or not screenshot.base64_image:
                return _line("browser", "FAIL", screenshot.error or "screenshot check failed")
            return _line("browser", "PASS", "opened local file and captured screenshot")
    finally:
        tool.cleanup()


def main() -> None:
    results = [check_tavily(), check_docker(), check_playwright()]
    for result in results:
        print(result)
    if any(": FAIL -" in result for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
