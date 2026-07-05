from .client.agent_config import AgentConfig
from .client.client_controller import ClientController
from .server.a2a_server_application import A2AServerApplication


def main() -> None:
    registry = A2AServerApplication().start()
    config = AgentConfig(registry)
    remote = config.a2a_remote_agent()
    sequential = config.sequential_agent()
    assert remote.invoke("上海天气")["weatherResult"] == "天晴"
    result = ClientController(remote, sequential).hello("上海天气")
    assert result["weatherResult"] == "天晴"
    assert "reactAgentResult" in result
    print("python-a2a-demo self check passed")


if __name__ == "__main__":
    main()
