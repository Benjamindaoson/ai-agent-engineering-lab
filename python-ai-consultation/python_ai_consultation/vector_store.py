import re

from .document import Document


class SimpleVectorStore:
    def __init__(self, documents: list[Document] | None = None):
        self.documents = list(documents or [])

    def add(self, documents: list[Document]) -> None:
        self.documents.extend(documents)

    def search(self, queries: list[str], top_k: int = 3, similarity_threshold: float = 0.0) -> list[Document]:
        scored: list[tuple[int, int, Document]] = []
        terms = self._terms(" ".join(queries))
        for index, document in enumerate(self.documents):
            haystack = f"{document.metadata.get('departmentName', '')} {document.text}".lower()
            score = sum(1 for term in terms if term and term in haystack)
            if score > similarity_threshold:
                scored.append((score, index, document))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [document for _, _, document in scored[:top_k]]

    def _terms(self, text: str) -> list[str]:
        tokens = re.findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]{2,}", text.lower())
        expanded: list[str] = []
        for token in tokens:
            expanded.append(token)
            if re.fullmatch(r"[\u4e00-\u9fff]+", token):
                expanded.extend(token[index : index + 2] for index in range(0, max(len(token) - 1, 0)))
        tokens = expanded
        if tokens:
            return tokens
        return [text.lower()]
