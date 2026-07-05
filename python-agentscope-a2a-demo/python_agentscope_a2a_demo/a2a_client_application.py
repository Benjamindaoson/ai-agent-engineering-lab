from .nacos_registry import InMemoryNacosRegistry


class A2AClientApplication:
    def __init__(self, registry: InMemoryNacosRegistry) -> None:
        self.registry = registry

    def resolve_card(self, agent_name: str) -> dict:
        return self.registry.resolve(agent_name)

    def stream(self, agent_name: str, text: str):
        self.resolve_card(agent_name)
        yield from self.registry.agent(agent_name).stream(text)
