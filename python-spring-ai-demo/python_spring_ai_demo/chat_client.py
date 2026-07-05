from openai import OpenAI

from .model_config import ModelConfig


class ChatClient:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def complete(self, prompt: str, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(model=self.config.model, messages=messages)
        return response.choices[0].message.content or ""

    def stream(self, prompt: str, system: str | None = None):
        for token in self.complete(prompt, system).split():
            yield token
