import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    api_key: str
    base_url: str
    model_name: str

    @classmethod
    def from_env(cls) -> "ModelConfig":
        provider = os.getenv("PROVIDER", "dashscope").lower()
        if provider == "dashscope":
            key = os.getenv("DASHSCOPE_API_KEY", "")
            if not key:
                raise RuntimeError("缺少 DASHSCOPE_API_KEY")
            return cls(provider, key, "https://dashscope.aliyuncs.com/compatible-mode/v1", os.getenv("LLM_NAME", "qwen3-max"))
        if provider == "deepseek":
            key = os.getenv("DEEPSEEK_API_KEY", "")
            if not key:
                raise RuntimeError("缺少 DEEPSEEK_API_KEY")
            return cls(provider, key, "https://api.deepseek.com", os.getenv("LLM_NAME", "deepseek-chat"))
        raise RuntimeError(f"不支持的 PROVIDER: {provider}")
