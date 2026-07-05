from __future__ import annotations

import math
import re
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Iterable


TOKEN_PATTERN = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)


@dataclass
class Document:
    content: str
    metadata: dict[str, object] = field(default_factory=dict)


class ChatMemory:
    def __init__(self, window_size: int = 20) -> None:
        self.window_size = window_size
        self._messages: dict[str, Deque[tuple[str, str]]] = defaultdict(
            lambda: deque(maxlen=window_size)
        )

    def add(self, conversation_id: str, role: str, content: str) -> None:
        self._messages[conversation_id].append((role, content))

    def history(self, conversation_id: str) -> list[tuple[str, str]]:
        return list(self._messages.get(conversation_id, ()))

    def render(self, conversation_id: str) -> str:
        return " | ".join(f"{role}: {content}" for role, content in self.history(conversation_id))


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


def cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
    common = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in common)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


class SimpleVectorStore:
    def __init__(self) -> None:
        self._documents: list[Document] = []

    def add(self, documents: Iterable[Document]) -> None:
        self._documents.extend(documents)

    def search(self, query: str, top_k: int = 3, threshold: float = 0.0) -> list[Document]:
        query_vector = Counter(tokenize(query))
        scored: list[tuple[float, Document]] = []
        for document in self._documents:
            score = cosine_similarity(query_vector, Counter(tokenize(document.content)))
            if score >= threshold:
                scored.append((score, document))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            Document(doc.content, {**doc.metadata, "score": score})
            for score, doc in scored[:top_k]
        ]


class SimpleRerankModel:
    def rerank(self, query: str, documents: Iterable[Document], top_k: int = 3) -> list[Document]:
        query_tokens = set(tokenize(query))

        def score(document: Document) -> int:
            return len(query_tokens & set(tokenize(document.content)))

        return sorted(documents, key=score, reverse=True)[:top_k]
