from .a2a_client_application import A2AClientApplication
from .a2a_server_spring_boot_application import create_server_application
from .nacos_registry import InMemoryNacosRegistry


def main() -> None:
    registry = InMemoryNacosRegistry()
    create_server_application(registry)
    client = A2AClientApplication(registry)
    print("AgentCard:", client.resolve_card("my-assistant"))
    for event in client.stream("my-assistant", "生成3个数据"):
        print(event)


if __name__ == "__main__":
    main()
