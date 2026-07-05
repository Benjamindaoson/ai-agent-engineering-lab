from abc import ABC, abstractmethod

from .message import Message


class RelevanceFilter(ABC):
    @abstractmethod
    def filter(self, messages: list[Message], current_query: str, max_messages: int) -> list[Message]:
        raise NotImplementedError

    @abstractmethod
    def calculate_relevance(self, message: Message, current_query: str) -> float:
        raise NotImplementedError
