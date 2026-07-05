from ..common import AgentCard, AgentRegistry, ReactAgent
from .zhouyu_tools import ZhouyuTools


class A2AServerApplication:
    def __init__(self, registry: AgentRegistry | None = None):
        self.registry = registry or AgentRegistry()
        self.tools = ZhouyuTools()

    def weather_agent(self) -> ReactAgent:
        return ReactAgent("weatherAgent", "简短的回答用户问题", self._weather_handler)

    def weather_agent1(self) -> ReactAgent:
        return ReactAgent("weatherAgent1", "简短的回答用户问题", self._weather_handler)

    def start(self) -> AgentRegistry:
        card = AgentCard(
            name="weatherAgent",
            description="专门用于获取天气的智能体",
            capabilities={"streaming": False},
            provider={"name": "Zhouyu", "organization": "Zhouyu Organization", "url": "https://github.com/zhouyu"},
            version="1.0.0",
        )
        self.registry.register(card, self.weather_agent().invoke)
        self.registry.register(
            AgentCard("weatherAgent1", "专门用于获取天气的智能体", {"streaming": False}, card.provider, "1.0.0"),
            self.weather_agent1().invoke,
        )
        return self.registry

    def _weather_handler(self, input_text: str) -> dict:
        return {"weatherResult": self.tools.get_weather(input_text)}
