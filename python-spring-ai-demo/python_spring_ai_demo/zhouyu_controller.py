import json
from dataclasses import dataclass

from .simple_ai import Document, EvaluationResponse, SimpleEmbeddingModel, SimpleVectorStore


@dataclass
class Poem:
    title: str
    author: str
    content: str


class ZhouyuTextSplitter:
    def split(self, text: str) -> list[str]:
        normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
        return normalized_text.split("\n\n")

    def apply(self, documents: list[Document]) -> list[Document]:
        result: list[Document] = []
        for document in documents:
            for part in self.split(document.text):
                result.append(Document(part.strip(), dict(document.metadata)))
        return [document for document in result if document.text]


class ZhouyuController:
    def __init__(
        self,
        chat_client,
        embedding_model: SimpleEmbeddingModel | None = None,
        vector_store: SimpleVectorStore | None = None,
    ):
        self.chat_client = chat_client
        self.embedding_model = embedding_model or SimpleEmbeddingModel()
        self.vector_store = vector_store or SimpleVectorStore(self.embedding_model)
        self.chat_memory: dict[str, list[str]] = {}
        self.metrics: dict[str, int] = {}

    def chat(self, question: str) -> str:
        return self.chat_client.complete(question)

    def stream(self, question: str):
        return self.chat_client.stream(question)

    def sse(self, question: str):
        for token in self.stream(question):
            yield {"content": token}

    def system(self, question: str) -> str:
        return self.chat_client.complete(question, system="你是周瑜老师")

    def memory(self, chat_id: str, question: str) -> str:
        history = self.chat_memory.setdefault(chat_id, [])
        prompt = "\n".join([*history, question])
        answer = self.chat_client.complete(prompt)
        history.extend([question, answer])
        return answer

    def advisor(self, question: str) -> str:
        return self.chat_client.complete(question, system="我是周瑜")

    def output(self, topic: str) -> Poem:
        prompt = f"写一首关于{topic}的七言绝句，返回JSON字段title,author,content"
        return self._to_poem(self.chat_client.complete(prompt))

    def entity(self, topic: str) -> Poem:
        return self.output(topic)

    def embedding(self, question: str) -> list[float]:
        return self.embedding_model.embed(question)

    def store(self, text: str | None = None) -> list[Document]:
        content = text or "Q：什么是API-KEY？\nA：用于调用鉴权。\n\nQ：API-KEY的上限个数是多少？\nA：3个。"
        documents = ZhouyuTextSplitter().apply([Document(content)])
        self.vector_store.add(documents)
        return documents

    def search(self, question: str, top_k: int = 2) -> list[Document]:
        return self.vector_store.similarity_search(question, top_k=top_k, similarity_threshold=0)

    def rag_chat(self, question: str) -> str:
        documents = self.search(question)
        prompt = f"{question}\n\n 用以下信息回答问题:\n {documents}"
        return self.chat_client.complete(prompt)

    def rag_advisor(self, question: str) -> str:
        return self.rag_chat(question)

    def rag_advisor2(self, chat_id: str, question: str) -> str:
        memory_text = "\n".join(self.chat_memory.get(chat_id, []))
        documents = self.search(f"{memory_text}\n{question}")
        answer = self.chat_client.complete(f"{question}\n\nRAG上下文：{documents}")
        self.chat_memory.setdefault(chat_id, []).extend([question, answer])
        return answer

    def evaluation(self, question: str) -> EvaluationResponse:
        documents = self.search(question, top_k=1)
        rag_result = self.rag_chat(question)
        passing = bool(documents) and any(term in rag_result for term in question.split())
        return EvaluationResponse(passing=passing or bool(documents), score=1.0 if documents else 0.0, feedback="offline relevancy")

    def test_metric(self) -> str:
        self.metrics["metric.zhouyu.count"] = self.metrics.get("metric.zhouyu.count", 0) + 1
        return "metric"

    def _to_poem(self, content: str) -> Poem:
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = {"title": "无题", "author": "AI", "content": content}
        return Poem(str(data.get("title", "")), str(data.get("author", "")), str(data.get("content", "")))
