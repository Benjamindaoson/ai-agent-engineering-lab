from __future__ import annotations

from ..simple_framework import ReactAgent, SequentialAgent


class ZhouyuAgent(SequentialAgent):
    def __init__(self, name: str, description: str, sub_agents: list[ReactAgent]) -> None:
        super().__init__(name, sub_agents, description)
