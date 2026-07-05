import re
from dataclasses import dataclass, field


@dataclass
class Document:
    text: str
    metadata: dict = field(default_factory=dict)


@dataclass
class EvaluationResponse:
    passing: bool
    score: float
    feedback: str


class SimpleEmbeddingModel:
    def embed(self, text: str) -> list[float]:
        # ponytail: fixed 3-bin character embedding, replace with real embedding when semantic quality matters.
        buckets = [0.0, 0.0, 0.0]
        for index, char in enumerate(text):
            buckets[index % 3] += ord(char) % 97
        total = sum(buckets) or 1.0
        return [value / total for value in buckets]


class SimpleVectorStore:
    def __init__(self, embedding_model: SimpleEmbeddingModel | None = None):
        self.embedding_model = embedding_model or SimpleEmbeddingModel()
        self.documents: list[Document] = []

    def add(self, documents: list[Document]) -> None:
        self.documents.extend(documents)

    def similarity_search(self, query: str, top_k: int = 2, similarity_threshold: float = 0.0) -> list[Document]:
        terms = self._terms(query)
        scored: list[tuple[int, int, Document]] = []
        for index, document in enumerate(self.documents):
            haystack = f"{document.text} {' '.join(str(value) for value in document.metadata.values())}".lower()
            score = sum(1 for term in terms if term and term in haystack)
            if score > similarity_threshold:
                scored.append((score, index, document))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [document for _, _, document in scored[:top_k]]

    def _terms(self, text: str) -> list[str]:
        tokens = re.findall(r"[A-Za-z0-9-]+|[\u4e00-\u9fff]{2,}", text.lower())
        expanded: list[str] = []
        for token in tokens:
            expanded.append(token)
            if re.fullmatch(r"[\u4e00-\u9fff]+", token):
                expanded.extend(token[index : index + 2] for index in range(0, max(len(token) - 1, 0)))
        return expanded or [text.lower()]
