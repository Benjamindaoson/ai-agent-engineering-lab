from __future__ import annotations

from pathlib import Path


class SessionStartup:
    FILES = {
        "agents": "AGENTS.md",
        "soul": "SOUL.md",
        "user": "USER.md",
        "identity": "IDENTITY.md",
        "tools": "TOOLS.md",
        "bootstrap": "BOOTSTRAP.md",
    }

    def __init__(self, workspace_path: str | Path) -> None:
        self.workspace_path = Path(workspace_path)
        self.contents: dict[str, str | None] = {}

    def initialize(self) -> None:
        for key, filename in self.FILES.items():
            path = self.workspace_path / filename
            self.contents[key] = path.read_text(encoding="utf-8") if path.exists() else None

    def delete_bootstrap(self) -> None:
        path = self.workspace_path / "BOOTSTRAP.md"
        if path.exists():
            path.unlink()
        self.contents["bootstrap"] = None

    def get_system_prompt(self) -> str:
        sections: list[tuple[str, str | None]] = [
            ("引导任务", self.contents.get("bootstrap")),
            ("工作空间规范", self.contents.get("agents")),
            ("核心信条", self.contents.get("soul")),
            ("用户信息", self.contents.get("user")),
            ("身份定义", self.contents.get("identity")),
            ("本地工具配置", self.contents.get("tools")),
        ]
        return "\n\n---\n\n".join(f"# {title}\n\n{content or ''}" for title, content in sections if content is not None)
