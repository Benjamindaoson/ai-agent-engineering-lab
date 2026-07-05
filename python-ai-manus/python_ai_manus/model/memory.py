from dataclasses import dataclass, field

from .message import Message
from .relevance_filter import RelevanceFilter


@dataclass
class Memory:
    messages: list[Message] = field(default_factory=list)
    relevance_filter: RelevanceFilter | None = None

    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    def get_messages(self, current_query: str | None = None) -> list[Message]:
        if self.relevance_filter is not None and current_query is not None:
            return self.relevance_filter.filter(self.messages, current_query, 5)
        return self.messages
