from __future__ import annotations

from pathlib import Path

from .chat_client import FakeChatClient, OpenAICompatibleChatClient
from .chat_controller import ChatController
from .model_config import ModelConfig
from .simple_ai import ChatMemory, Document, SimpleVectorStore


def create_chat_memory(window_size: int = 20) -> ChatMemory:
    return ChatMemory(window_size=window_size)


def load_qa_documents(path: str | Path) -> list[Document]:
    text = Path(path).read_text(encoding="utf-8")
    documents: list[Document] = []
    for block in text.split("\n\n"):
        block = block.strip()
        if block:
            documents.append(Document(block, {"source": str(path)}))
    return documents


def create_controller(*, live: bool = False) -> ChatController:
    resource_dir = Path(__file__).resolve().parents[1] / "resources"
    vector_store = SimpleVectorStore()
    vector_store.add(load_qa_documents(resource_dir / "qa.txt"))
    chat_client = OpenAICompatibleChatClient(ModelConfig.from_env()) if live else FakeChatClient()
    return ChatController(
        chat_client=chat_client,
        chat_memory=create_chat_memory(),
        vector_store=vector_store,
        qa_resource=resource_dir / "qa.txt",
    )


def main() -> None:
    controller = create_controller(live=False)
    print(controller.chat("北京现在几点"))
    print(controller.rank_chat("API-KEY 的上限个数是多少？"))


if __name__ == "__main__":
    main()
