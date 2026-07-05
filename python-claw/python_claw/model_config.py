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
            return cls(provider, values.get("DEEPSEEK_API_KEY", ""), model or "deepseek-chat", values.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
        if provider == "dashscope":
            return cls(provider, values.get("DASHSCOPE_API_KEY", ""), model or "qwen3-max", values.get("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"))
        raise ValueError("PROVIDER must be dashscope or deepseek")
