from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelResponse:
    content: str | None
    tool_calls: list[Any] = field(default_factory=list)
    finish_reason: str = "stop"

    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)
