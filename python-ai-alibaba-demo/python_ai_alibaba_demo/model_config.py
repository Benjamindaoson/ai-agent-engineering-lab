from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    api_key: str
    model: str
    base_url: str

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "ModelConfig":
        values = env or os.environ
        provider = values.get("PROVIDER", "dashscope").strip().lower()
        model = values.get("LLM_NAME", "").strip()

        if provider == "deepseek":
            api_key = values.get("DEEPSEEK_API_KEY", "")
            return cls(
                provider=provider,
                api_key=api_key,
                model=model or "deepseek-chat",
                base_url=values.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            )

        if provider == "dashscope":
            api_key = values.get("DASHSCOPE_API_KEY", "")
            return cls(
                provider=provider,
                api_key=api_key,
                model=model or "qwen-long",
                base_url=values.get(
                    "DASHSCOPE_BASE_URL",
                    "https://dashscope.aliyuncs.com/compatible-mode/v1",
                ),
            )

        raise ValueError("PROVIDER must be dashscope or deepseek")

    def require_api_key(self) -> None:
        if not self.api_key:
            if self.provider == "deepseek":
                raise RuntimeError("DEEPSEEK_API_KEY is required for live DeepSeek calls")
            raise RuntimeError("DASHSCOPE_API_KEY is required for live DashScope calls")
