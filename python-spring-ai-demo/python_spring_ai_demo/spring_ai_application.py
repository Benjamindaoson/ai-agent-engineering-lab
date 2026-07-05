from .chat_client import ChatClient
from .mcp_controller import McpController
from .model_config import ModelConfig
from .simple_ai import SimpleEmbeddingModel, SimpleVectorStore
from .tool_controller import ToolController
from .zhouyu_controller import ZhouyuController
from .zhouyu_tools import ZhouyuTools


def create_app(chat_client=None):
    client = chat_client or ChatClient(ModelConfig.from_env())
    embedding_model = SimpleEmbeddingModel()
    vector_store = SimpleVectorStore(embedding_model)
    tools = ZhouyuTools()
    return {
        "zhouyu_controller": ZhouyuController(client, embedding_model, vector_store),
        "tool_controller": ToolController(client, tools),
        "mcp_controller": McpController(client),
        "tools": tools,
    }


def main() -> None:
    app = create_app()
    question = input("请输入问题: ").strip()
    print(app["zhouyu_controller"].chat(question))


if __name__ == "__main__":
    main()
