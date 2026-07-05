from __future__ import annotations

from pathlib import Path

from .baidu_test import baidu_search
from .simple_ai import ChatMemory, Document, SimpleRerankModel, SimpleVectorStore


class ChatController:
    def __init__(
        self,
        *,
        chat_client,
        chat_memory: ChatMemory,
        vector_store: SimpleVectorStore,
        qa_resource: str | Path,
        rerank_model: SimpleRerankModel | None = None,
    ) -> None:
        self.chat_client = chat_client
        self.chat_memory = chat_memory
        self.vector_store = vector_store
        self.qa_resource = Path(qa_resource)
        self.rerank_model = rerank_model or SimpleRerankModel()

    def chat(self, question: str) -> str:
        return self.chat_client.complete(question, tools=["getCityTimeFunction"])

    def baidu(self, question: str) -> dict[str, object]:
        return baidu_search(question, top_k=10)

    def rank_chat(self, question: str) -> str:
        retrieved = self.vector_store.search(question, top_k=6)
        reranked = self.rerank_model.rerank(question, retrieved, top_k=3)
        return self.chat_client.complete(question, context=reranked)

    def rag_advisor2(self, chat_id: str, question: str) -> str:
        compressed_query = self._compress_query(chat_id, question)
        expanded_queries = self._expand_query(compressed_query)
        documents: list[Document] = []
        for query in expanded_queries:
            documents.extend(self.vector_store.search(query, top_k=3, threshold=0.0))
        joined = self._join_documents(documents)
        reranked = self.rerank_model.rerank(question, joined, top_k=3)
        history = self.chat_memory.render(chat_id)
        answer = self.chat_client.complete(question, context=reranked, history=history)
        self.chat_memory.add(chat_id, "user", question)
        self.chat_memory.add(chat_id, "assistant", answer)
        return answer

    def file_chat(self, question: str) -> str:
        content = self.qa_resource.read_text(encoding="utf-8")
        document = Document(content, {"source": str(self.qa_resource), "advisor": "fileChat"})
        return self.chat_client.complete(question, context=[document])

    def _compress_query(self, chat_id: str, question: str) -> str:
        history = self.chat_memory.render(chat_id)
        return f"{history} {question}".strip() if history else question

    def _expand_query(self, query: str) -> list[str]:
        return [query, f"{query} 相关文档", f"{query} 答案"]

    def _join_documents(self, documents: list[Document]) -> list[Document]:
        seen: set[str] = set()
        joined: list[Document] = []
        for document in documents:
            if document.content in seen:
                continue
            seen.add(document.content)
            joined.append(document)
        return joined
