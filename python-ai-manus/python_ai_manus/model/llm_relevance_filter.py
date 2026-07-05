import re

from .message import Message
from .model_response import ModelResponse
from .openai_client import OpenAIClient
from .relevance_filter import RelevanceFilter
from .role import Role


class LLMRelevanceFilter(RelevanceFilter):
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client

    def filter(self, messages: list[Message], current_query: str, max_messages: int) -> list[Message]:
        if not messages:
            return []
        if len(messages) <= max_messages:
            return list(messages)

        system_messages = [message for message in messages if message.role == Role.SYSTEM]
        non_system = [message for message in messages if message.role != Role.SYSTEM]
        scored = sorted(
            ((message, self.calculate_relevance(message, current_query)) for message in non_system),
            key=lambda item: item[1],
            reverse=True,
        )
        remaining = max(0, max_messages - len(system_messages))
        return system_messages + [message for message, _ in scored[:remaining]]

    def calculate_relevance(self, message: Message, current_query: str) -> float:
        if message is None or message.content is None or current_query is None:
            return 0.0
        try:
            response = self.openai_client.chat(
                [
                    Message.system_message("You rate semantic relevance. Return only a number from 0.0 to 1.0."),
                    Message.user_message(self._build_relevance_prompt(str(message.content), current_query)),
                ]
            )
            return self._parse_relevance_score(response.content if isinstance(response, ModelResponse) else "")
        except Exception:
            # ponytail: relevance filtering must never break the main agent loop.
            return 0.0

    def _build_relevance_prompt(self, message_content: str, query: str) -> str:
        return (
            "Rate how relevant the message is to the query. Return only a number from 0.0 to 1.0.\n\n"
            f"Query:\n{query}\n\nMessage:\n{message_content}"
        )

    def _parse_relevance_score(self, content: str | None) -> float:
        if not content:
            return 0.0
        match = re.search(r"\d+(?:\.\d+)?", content)
        if not match:
            return 0.0
        return max(0.0, min(1.0, float(match.group(0))))
