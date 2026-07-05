from .a2a_client_application import A2AClientApplication
from .a2a_server_spring_boot_application import create_server_application
from .nacos_registry import InMemoryNacosRegistry


def main() -> None:
    registry = InMemoryNacosRegistry()
    create_server_application(registry)
    events = list(A2AClientApplication(registry).stream("my-assistant", "上海什么天气"))
    assert events[0]["type"] == "TASK_STARTED"
    assert "上海 的天气" in events[1]["message"]["content"]
    assert events[-1]["type"] == "TASK_FINISHED"
    print("self_check: ok")


if __name__ == "__main__":
    main()
