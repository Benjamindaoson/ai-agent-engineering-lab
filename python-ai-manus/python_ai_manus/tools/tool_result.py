from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    output: Any = None
    error: str | None = None
    base64_image: str | None = None

    @staticmethod
    def success(output: Any, base64_image: str | None = None) -> "ToolResult":
        return ToolResult(output=output, base64_image=base64_image)

    @staticmethod
    def failure(error: str) -> "ToolResult":
        return ToolResult(error=error)

    def is_success(self) -> bool:
        return self.error is None

    def has_error(self) -> bool:
        return self.error is not None

    def has_image(self) -> bool:
        return self.base64_image is not None
