from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DateRequest:
    city_name: str


class DateTool:
    def apply(self, date_request: DateRequest, tool_context: dict[str, object]) -> str:
        return f"{date_request.city_name} 当前时间 {datetime.now().isoformat(timespec='seconds')}"

    def __call__(self, input_text: str, tool_context: dict[str, object]) -> str:
        return self.apply(DateRequest(input_text), tool_context)
