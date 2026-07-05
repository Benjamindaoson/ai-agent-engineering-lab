import os
from dataclasses import dataclass


@dataclass
class ModelConfig:
    model: str
    base_url: str
    api_key: str

    @classmethod
    def from_env(cls) -> "ModelConfig":
        provider = os.getenv("PROVIDER", "dashscope").strip().lower()
        if provider == "deepseek":
            return cls(
                model=os.getenv("LLM_NAME", "deepseek-chat"),
                base_url="https://api.deepseek.com",
                api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            )
        if provider == "dashscope":
            return cls(
                model=os.getenv("LLM_NAME", "qwen-plus"),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                api_key=os.getenv("DASHSCOPE_API_KEY", ""),
            )
        raise ValueError(f"Unsupported PROVIDER: {provider}")
