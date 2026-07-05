from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable


class MemoryService:
    def __init__(
        self,
        workspace_path: str | Path,
        *,
        today: Callable[[], date] = date.today,
        now: Callable[[], datetime] = datetime.now,
    ) -> None:
        self.workspace_path = Path(workspace_path)
        self.memory_dir = self.workspace_path / "memory"
        self.memory_md_path = self.workspace_path / "MEMORY.md"
        self._today = today
        self._now = now
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def get_today_date(self) -> str:
        return self._today().isoformat()

    def get_yesterday_date(self) -> str:
        return (self._today() - timedelta(days=1)).isoformat()

    def get_today_note_path(self) -> Path:
        return self.memory_dir / f"{self.get_today_date()}.md"

    def get_note_path(self, note_date: str) -> Path:
        return self.memory_dir / f"{note_date}.md"

    def read_today_note(self) -> str:
        return self._read(self.get_today_note_path())

    def read_yesterday_note(self) -> str:
        return self._read(self.get_note_path(self.get_yesterday_date()))

    def read_memory_md(self) -> str:
        return self._read(self.memory_md_path)

    def append_to_today_note(self, content: str) -> None:
        path = self.get_today_note_path()
        if not path.exists():
            path.write_text(f"# {self.get_today_date()}\n\n", encoding="utf-8")
        path.write_text(path.read_text(encoding="utf-8") + f"[{self._timestamp()}] {content}\n", encoding="utf-8")

    def append_to_memory_md(self, content: str) -> None:
        if not self.memory_md_path.exists():
            self.memory_md_path.write_text(f"# 长期记忆\n\n最后更新：{self._timestamp()}\n\n", encoding="utf-8")
        current = self.memory_md_path.read_text(encoding="utf-8")
        self.memory_md_path.write_text(current + f"[{self._timestamp()}] {content}\n", encoding="utf-8")

    def update_memory_md(self, content: str) -> None:
        self.memory_md_path.write_text(f"# 长期记忆\n\n最后更新：{self._timestamp()}\n\n{content}", encoding="utf-8")

    def log_conversation(self, role: str, content: str) -> None:
        self.append_to_today_note(f"### {role}\n{content}\n")

    def log_significant_event(self, event: str) -> None:
        self.append_to_memory_md(f"## 事件\n{event}")

    def log_decision(self, decision: str) -> None:
        self.append_to_memory_md(f"## 决策\n{decision}")

    def log_lesson(self, lesson: str) -> None:
        self.append_to_memory_md(f"## 经验教训\n{lesson}")

    def get_recent_notes(self, days: int) -> list[str]:
        start = self._today() - timedelta(days=days)
        return [self._read(self.get_note_path((start + timedelta(days=i)).isoformat())) for i in range(days + 1)]

    def ensure_today_note_exists(self) -> None:
        path = self.get_today_note_path()
        if not path.exists():
            path.write_text(f"# {self.get_today_date()}\n\n", encoding="utf-8")

    def _timestamp(self) -> str:
        return self._now().strftime("%Y-%m-%d %H:%M:%S")

    def _read(self, path: Path) -> str:
        return path.read_text(encoding="utf-8") if path.exists() else ""
