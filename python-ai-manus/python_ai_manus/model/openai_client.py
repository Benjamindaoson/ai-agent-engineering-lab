from typing import Any

from openai import OpenAI

from .message import Message
from .model_config import ModelConfig
from .model_response import ModelResponse
from .tool_definition import ToolDefinition


class OpenAIClient:
    def __init__(self, model_config: ModelConfig):
        self.model_config = model_config
        self.client = OpenAI(api_key=model_config.api_key, base_url=model_config.base_url)

    def chat(self, messages: list[Message], tools: list[ToolDefinition] | None = None) -> ModelResponse:
        request: dict[str, Any] = {
            "model": self.model_config.model,
            "messages": [message.to_dict() for message in messages],
        }
        if tools:
            request["tools"] = [tool.to_openai_tool() for tool in tools]

        response = self.client.chat.completions.create(**request)
        choice = response.choices[0]
        message = choice.message
        tool_calls = [tool_call.model_dump() for tool_call in (message.tool_calls or [])]
        return ModelResponse(
            content=message.content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason or "",
        )
