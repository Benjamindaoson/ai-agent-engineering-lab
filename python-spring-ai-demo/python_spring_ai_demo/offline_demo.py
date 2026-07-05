from .mcp_controller import McpController
from .simple_ai import SimpleEmbeddingModel, SimpleVectorStore
from .tool_controller import ToolController
from .zhouyu_controller import ZhouyuController
from .zhouyu_tools import ZhouyuTools


class DemoChatClient:
    def complete(self, prompt: str, system: str | None = None) -> str:
        prefix = f"[{system}] " if system else ""
        return prefix + "offline response: " + prompt[:120]

    def stream(self, prompt: str, system: str | None = None):
        for token in self.complete(prompt, system).split():
            yield token + " "


class DemoMcpClient:
    def list_prompts(self):
        return ["greeting(name=周瑜)"]

    def read_resource(self, uri: str):
        return f"{uri}: zhouyu"


def main() -> None:
    client = DemoChatClient()
    tools = ZhouyuTools()
    zhouyu = ZhouyuController(client, SimpleEmbeddingModel(), SimpleVectorStore())
    tool_controller = ToolController(client, tools)
    mcp_controller = McpController(client, [lambda message: f"tool callback saw {message}"], [DemoMcpClient()])

    print("1. chat/system/memory")
    print(zhouyu.chat("你好"))
    print(zhouyu.system("你是谁"))
    print(zhouyu.memory("demo", "记住我是周瑜"))

    print("\n2. store/search/rag")
    zhouyu.store("Q：什么是API-KEY？\nA：API-KEY用于鉴权。\n\nQ：上限是多少？\nA：3个。")
    print([document.text for document in zhouyu.search("API-KEY")])
    print(zhouyu.rag_chat("API-KEY是什么？"))

    print("\n3. tools")
    print(tool_controller.tool("现在几点"))
    print(tools.save_code("print('hello')"))

    print("\n4. mcp")
    print(mcp_controller.mcp("hello"))
    print(mcp_controller.mcp_prompt(""))
    print(mcp_controller.mcp_resource(""))


if __name__ == "__main__":
    main()
