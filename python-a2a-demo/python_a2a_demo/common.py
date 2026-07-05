from dataclasses import dataclass, field
from typing import Callable


@dataclass
class AgentCard:
    name: str
    description: str
    capabilities: dict
    provider: dict = field(default_factory=dict)
    version: str = "1.0.0"


class AgentRegistry:
    def __init__(self):
        self._cards: dict[str, AgentCard] = {}
        self._handlers: dict[str, Callable[[str], dict]] = {}

    def register(self, card: AgentCard, handler: Callable[[str], dict]) -> None:
        self._cards[card.name] = card
        self._handlers[card.name] = handler

    def get_card(self, name: str) -> AgentCard:
        return self._cards[name]

    def list_cards(self) -> list[AgentCard]:
        return list(self._cards.values())

    def invoke(self, name: str, input_text: str) -> dict:
        if name not in self._handlers:
            raise KeyError(f"Agent not found: {name}")
        return self._handlers[name](input_text)


class ReactAgent:
    def __init__(self, name: str, system_prompt: str, handler: Callable[[str], dict] | None = None):
        self.name = name
        self.system_prompt = system_prompt
        self.handler = handler

    def invoke(self, input_text: str) -> dict:
        if self.handler:
            return self.handler(input_text)
        return {f"{self.name}Result": f"{self.system_prompt}: {input_text}"}


class A2aRemoteAgent:
    def __init__(self, name: str, registry: AgentRegistry, description: str = "", instruction: str = "用户输入：{input}"):
        self.name = name
        self.registry = registry
        self.description = description
        self.instruction = instruction

    @property
    def card(self) -> AgentCard:
        return self.registry.get_card(self.name)

    def invoke(self, input_text: str) -> dict:
        return self.registry.invoke(self.name, self.instruction.format(input=input_text))


class SequentialAgent:
    def __init__(self, name: str, sub_agents: list):
        self.name = name
        self.sub_agents = sub_agents

    def invoke(self, input_text: str) -> dict:
        state = {"input": input_text}
        current_input = input_text
        for agent in self.sub_agents:
            result = agent.invoke(current_input)
            state.update(result)
            current_input = " ".join(str(value) for value in result.values())
        return state
