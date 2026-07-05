from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WeatherRequest:
    city_name: str


class StoreTool:
    def apply(self, weather_request: WeatherRequest, tool_context: dict[str, object]) -> str:
        config = tool_context.get("_AGENT_CONFIG_")
        user_info = config.store.get_item(["user_info"], "user_002") if config and config.store else {}
        username = user_info.get("username", "未知用户") if user_info else "未知用户"
        return f"{username} 查询 {weather_request.city_name}: 天晴"

    def __call__(self, input_text: str, tool_context: dict[str, object]) -> str:
        return self.apply(WeatherRequest(input_text), tool_context)
