import base64
from typing import Any

from python_ai_manus.tools.base_tool import BaseTool
from python_ai_manus.tools.tool_result import ToolResult


class BrowserTool(BaseTool):
    def __init__(self):
        super().__init__("browser", "Navigate web pages, take screenshots, interact with elements, and extract content")
        self.playwright = None
        self.browser = None
        self.context = None
        self.current_page = None

    def get_parameters_schema(self) -> dict[str, Any]:
        return self.build_schema(
            {
                "action": self.enum_param(
                    "Browser action",
                    ["navigate", "click", "type", "screenshot", "get_content", "scroll", "wait"],
                ),
                "url": self.string_param("URL for navigate"),
                "selector": self.string_param("CSS selector for click/type/wait"),
                "text": self.string_param("Text for type"),
                "timeout": self.int_param("Timeout in milliseconds"),
                "wait_for": self.string_param("Selector to wait for"),
                "scroll_direction": self.enum_param("Scroll direction", ["up", "down", "left", "right"]),
                "scroll_amount": self.int_param("Scroll amount in pixels"),
            },
            ["action"],
        )

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        action = self.get_string(parameters, "action")
        if not action:
            return ToolResult.failure("action is required")
        try:
            if self.current_page is None:
                self._initialize_browser()
            method = getattr(self, f"_handle_{action.lower()}", None)
            if method is None:
                return ToolResult.failure(f"Unknown action: {action}")
            return method(parameters)
        except Exception as exc:
            # ponytail: browser automation is optional in offline classes; report as tool failure.
            return ToolResult.failure(f"Browser operation failed: {exc}")

    def _initialize_browser(self) -> None:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError("playwright is not installed; run `pip install playwright` and `playwright install chromium`") from exc

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True, timeout=30000)
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )
        self.current_page = self.context.new_page()

    def _handle_navigate(self, parameters: dict[str, Any]) -> ToolResult:
        url = self.get_string(parameters, "url")
        if not url:
            return ToolResult.failure("url is required for navigate")
        timeout = self.get_integer(parameters, "timeout", 30000)
        response = self.current_page.goto(url, timeout=timeout)
        self.current_page.wait_for_load_state("networkidle")
        status = response.status if response else "unknown"
        return ToolResult.success(
            f"Navigated to: {url}\nTitle: {self.current_page.title()}\n"
            f"Final URL: {self.current_page.url}\nStatus: {status}"
        )

    def _handle_click(self, parameters: dict[str, Any]) -> ToolResult:
        selector = self.get_string(parameters, "selector")
        if not selector:
            return ToolResult.failure("selector is required for click")
        self.current_page.locator(selector).click(timeout=self.get_integer(parameters, "timeout", 30000))
        return ToolResult.success(f"Clicked element: {selector}")

    def _handle_type(self, parameters: dict[str, Any]) -> ToolResult:
        selector = self.get_string(parameters, "selector")
        text = self.get_string(parameters, "text")
        if not selector:
            return ToolResult.failure("selector is required for type")
        if text is None:
            return ToolResult.failure("text is required for type")
        locator = self.current_page.locator(selector)
        locator.clear()
        locator.fill(text, timeout=self.get_integer(parameters, "timeout", 30000))
        return ToolResult.success(f"Typed text into element: {selector}")

    def _handle_screenshot(self, parameters: dict[str, Any]) -> ToolResult:
        screenshot = self.current_page.screenshot(full_page=True, type="png")
        return ToolResult.success("Screenshot captured", base64.b64encode(screenshot).decode("ascii"))

    def _handle_get_content(self, parameters: dict[str, Any]) -> ToolResult:
        body = self.current_page.text_content("body") or ""
        return ToolResult.success(f"Title: {self.current_page.title()}\nURL: {self.current_page.url}\nContent:\n{body}")

    def _handle_scroll(self, parameters: dict[str, Any]) -> ToolResult:
        direction = self.get_string(parameters, "scroll_direction", "down")
        amount = self.get_integer(parameters, "scroll_amount", 500)
        scripts = {
            "down": f"window.scrollBy(0, {amount})",
            "up": f"window.scrollBy(0, -{amount})",
            "left": f"window.scrollBy(-{amount}, 0)",
            "right": f"window.scrollBy({amount}, 0)",
        }
        script = scripts.get(direction)
        if script is None:
            return ToolResult.failure(f"Invalid scroll direction: {direction}")
        self.current_page.evaluate(script)
        return ToolResult.success(f"Scrolled {direction} by {amount} pixels")

    def _handle_wait(self, parameters: dict[str, Any]) -> ToolResult:
        wait_for = self.get_string(parameters, "wait_for")
        timeout = self.get_integer(parameters, "timeout", 30000)
        if wait_for:
            self.current_page.wait_for_selector(wait_for, timeout=timeout)
            return ToolResult.success(f"Waited for element: {wait_for}")
        self.current_page.wait_for_load_state("networkidle")
        return ToolResult.success("Waited for page load")

    def cleanup(self) -> None:
        for item in (self.current_page, self.context, self.browser):
            if item is not None:
                try:
                    item.close()
                except (AttributeError, RuntimeError):
                    pass
        if self.playwright is not None:
            try:
                self.playwright.stop()
            except (AttributeError, RuntimeError):
                pass
        self.playwright = self.browser = self.context = self.current_page = None
