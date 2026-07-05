from .mcp_controller import McpController
from .simple_ai import SimpleEmbeddingModel, SimpleVectorStore
from .tool_controller import ToolController
from .zhouyu_controller import ZhouyuController
from .zhouyu_tools import ZhouyuTools


class FakeChatClient:
    def complete(self, prompt: str, system: str | None = None) -> str:
        if "七言绝句" in prompt:
            return '{"title":"春江","author":"AI","content":"春江潮水连海平"}'
        return f"{system + ': ' if system else ''}answer:{prompt}"

    def stream(self, prompt: str, system: str | None = None):
        yield self.complete(prompt, system)


class FakeMcpClient:
    def list_prompts(self):
        return ["greeting(name)"]

    def read_resource(self, uri: str):
        return f"resource:{uri}=zhouyu"


def main() -> None:
    client = FakeChatClient()
    tools = ZhouyuTools()
    controller = ZhouyuController(client, SimpleEmbeddingModel(), SimpleVectorStore())
    assert "answer" in controller.chat("hello")
    assert controller.store("Q：API-KEY？\nA：鉴权。")
    assert controller.search("API-KEY")
    assert "answer" in ToolController(client, tools).tool("现在几点")
    assert McpController(client, [], [FakeMcpClient()]).mcp_prompt("") == "greeting(name)"
    print("python-spring-ai-demo self check passed")


if __name__ == "__main__":
    main()
