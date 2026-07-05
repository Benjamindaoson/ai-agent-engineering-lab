import os
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class ModelConfig:
    api_key: str
    base_url: str
    llm_name: str
    provider: str

    @staticmethod
    def from_env(env: Mapping[str, str] | None = None) -> "ModelConfig":
        source = env if env is not None else os.environ
        provider = source.get("PROVIDER", "dashscope").lower()

        if provider == "deepseek":
            return ModelConfig(
                api_key=source.get("DEEPSEEK_API_KEY", ""),
                base_url="https://api.deepseek.com",
                llm_name=source.get("LLM_NAME", "deepseek-v4-flash"),
                provider=provider,
            )

        if provider == "dashscope":
            return ModelConfig(
                api_key=source.get("DASHSCOPE_API_KEY", ""),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                llm_name=source.get("LLM_NAME", "qwen3-max"),
                provider=provider,
            )

        raise ValueError("PROVIDER must be 'dashscope' or 'deepseek'")
