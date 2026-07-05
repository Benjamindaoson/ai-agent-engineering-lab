from .client.agent_config import AgentConfig
from .client.client_controller import ClientController
from .server.a2a_server_application import A2AServerApplication


def main() -> None:
    print("1. A2A server registers weatherAgent")
    registry = A2AServerApplication().start()
    for card in registry.list_cards():
        print(f"- {card.name}: {card.description}, streaming={card.capabilities['streaming']}")

    print("\n2. Client discovers and invokes remote weatherAgent")
    config = AgentConfig(registry)
    remote = config.a2a_remote_agent()
    print(remote.invoke("上海天气怎么样？"))

    print("\n3. Client runs sequentialAgent: remote weather agent -> local react agent")
    sequential = config.sequential_agent()
    print(sequential.invoke("上海天气怎么样？"))

    print("\n4. Controller /hello equivalent")
    print(ClientController(remote, sequential).hello("上海天气怎么样？"))


if __name__ == "__main__":
    main()
