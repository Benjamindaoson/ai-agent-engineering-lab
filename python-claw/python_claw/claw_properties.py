from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ClawProperties:
    workspace_dir: Path = Path("python-claw/workspace")
    sessions_dir: Path = Path("python-claw/sessions")
    model_name: str = "qwen3-max"
    api_key: str = ""
    feishu_app_id: str = ""
    feishu_app_secret: str = ""
    websocket_port: int = 8887
    sysprompt_prefix: str = "你是一个有帮助的 AI 助手"
    main_agent_name: str = "网页助手"
    feishu_agent_name: str = "飞书助手"

    def __post_init__(self) -> None:
        self.workspace_dir = Path(self.workspace_dir)
        self.sessions_dir = Path(self.sessions_dir)
