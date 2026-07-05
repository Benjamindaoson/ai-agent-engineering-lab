from dataclasses import dataclass

from .nacos_registry import InMemoryNacosRegistry
from .weather_service import WeatherService


@dataclass
class ReActAgent:
    name: str
    weather_service: WeatherService

    def stream(self, text: str):
        yield {"type": "TASK_STARTED", "agent": self.name}
        if "天气" in text:
            city = text.split("什么天气")[0].strip() or "上海"
            yield {"type": "MESSAGE", "message": {"role": "assistant", "content": self.weather_service.get_weather(city)}}
        elif "生成" in text and "数据" in text:
            count = _first_int(text, 10)
            chunks: list[str] = []
            result = self.weather_service.generate(count, chunks.append)
            for chunk in chunks:
                yield {"type": "MESSAGE", "message": {"role": "assistant", "content": chunk}}
            yield {"type": "MESSAGE", "message": {"role": "assistant", "content": result}}
        else:
            yield {"type": "MESSAGE", "message": {"role": "assistant", "content": f"{self.name}: 已收到 {text}"}}
        yield {"type": "TASK_FINISHED", "agent": self.name}


@dataclass
class A2AServerSpringBootApplication:
    registry: InMemoryNacosRegistry
    agent: ReActAgent


def create_server_application(registry: InMemoryNacosRegistry | None = None) -> A2AServerSpringBootApplication:
    registry = registry or InMemoryNacosRegistry()
    agent = ReActAgent("my-assistant", WeatherService())
    card = {
        "name": "my-assistant",
        "skills": [
            {"id": "getWeather", "name": "getWeather", "description": "获取指定城市的天气", "tags": ["weather"]},
            {"id": "generate", "name": "generate", "description": "生成数据", "tags": ["data"]},
        ],
    }
    registry.register(agent.name, card, agent)
    return A2AServerSpringBootApplication(registry, agent)


def _first_int(text: str, default: int) -> int:
    digits = "".join(ch if ch.isdigit() else " " for ch in text).split()
    return int(digits[0]) if digits else default
