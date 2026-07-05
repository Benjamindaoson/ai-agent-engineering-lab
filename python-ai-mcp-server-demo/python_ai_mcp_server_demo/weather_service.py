from dataclasses import dataclass


@dataclass
class PromptResult:
    description: str
    messages: list[dict]


class WeatherService:
    def __init__(self, environment: dict[str, str] | None = None):
        self.environment = dict(environment or {})

    def get_weather(self, city_name: str) -> str:
        if city_name == "上海":
            return "天晴"
        if city_name == "北京":
            return "下雨"
        return "不知道"

    def greeting(self, name: str) -> PromptResult:
        message = f"你好, {name}! 有什么可以帮您?"
        return PromptResult(
            "Greeting",
            [{"role": "assistant", "content": {"type": "text", "text": message}}],
        )

    def get_config(self, key: str) -> str:
        return self.environment.get(key, "123")
