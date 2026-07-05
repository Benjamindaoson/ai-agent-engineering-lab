from openai import OpenAI

from .model_config import ModelConfig


class ChatClient:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def complete(self, system_prompt: str, user_prompt: str, tools: list[str] | None = None) -> str:
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""
