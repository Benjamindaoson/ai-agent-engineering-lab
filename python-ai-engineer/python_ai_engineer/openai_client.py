from openai import OpenAI

from .model_config import ModelConfig


class OpenAIClient:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        request = {"model": self.config.model, "messages": messages}
        if tools:
            request["tools"] = tools
        response = self.client.chat.completions.create(**request)
        choice = response.choices[0]
        message = choice.message
        return {
            "content": message.content,
            "tool_calls": [tool_call.model_dump() for tool_call in (message.tool_calls or [])],
            "finish_reason": choice.finish_reason or "",
        }
