from __future__ import annotations


DOCUMENTS = [
    "AgentLab trains learners through project submissions, reviews, and evidence.",
    "RAG systems need chunking, retrieval, grounded generation, and evaluation.",
]


def answer(query: str) -> str:
    terms = {part.lower() for part in query.split() if part.strip()}
    for document in DOCUMENTS:
        if terms & {part.strip(".,").lower() for part in document.split()}:
            return document
    return "No grounded answer found."
