from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable

from .model_config import ModelConfig
from .simple_ai import Document


@dataclass
class ChatMessage:
    role: str
    content: str


class FakeChatClient:
    def complete(
        self,
        question: str,
        *,
        context: Iterable[Document] | None = None,
        tools: Iterable[str] | None = None,
        history: str = "",
    ) -> str:
        context_text = "\n".join(document.content for document in context or [])
        tool_text = ",".join(tools or [])
        parts = [f"answer={question}"]
        if tool_text:
            parts.append(f"tools={tool_text}")
        if context_text:
            parts.append(f"context={context_text}")
        if history:
            parts.append(f"history={history}")
        return "\n".join(parts)


class OpenAICompatibleChatClient:
    def __init__(self, config: ModelConfig) -> None:
        config.require_api_key()
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install dependencies with: pip install -r requirements.txt") from exc
        self._config = config
        self._client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def complete(
        self,
        question: str,
        *,
        context: Iterable[Document] | None = None,
        tools: Iterable[str] | None = None,
        history: str = "",
    ) -> str:
        messages = []
        context_text = "\n".join(document.content for document in context or [])
        if context_text:
            messages.append({"role": "system", "content": f"Use this context:\n{context_text}"})
        if history:
            messages.append({"role": "system", "content": f"Conversation history:\n{history}"})
        if tools:
            messages.append({"role": "system", "content": f"Available local tools: {json.dumps(list(tools))}"})
        messages.append({"role": "user", "content": question})
        response = self._client.chat.completions.create(
            model=self._config.model,
            messages=messages,
        )
        return response.choices[0].message.content or ""
