class InMemoryNacosRegistry:
    def __init__(self) -> None:
        self._cards: dict[str, dict] = {}
        self._agents: dict[str, object] = {}

    def register(self, name: str, card: dict, agent: object) -> None:
        self._cards[name] = card
        self._agents[name] = agent

    def resolve(self, name: str) -> dict:
        if name not in self._cards:
            raise KeyError(f"agent not found: {name}")
        return self._cards[name]

    def agent(self, name: str):
        if name not in self._agents:
            raise KeyError(f"agent not found: {name}")
        return self._agents[name]
