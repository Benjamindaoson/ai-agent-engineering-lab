from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from .claw_agent import ClawAgent
from .claw_properties import ClawProperties
from .memory.memory_service import MemoryService
from .memory.session_startup import SessionStartup
from .skill.skill_loader import SkillLoader


@dataclass
class ClawApplication:
    properties: ClawProperties
    memory_service: MemoryService
    session_startup: SessionStartup
    skill_loader: SkillLoader
    claw_agent: ClawAgent


def create_application(
    *,
    workspace_dir: str | Path | None = None,
    today=lambda: date.today(),
    now=lambda: datetime.now(),
) -> ClawApplication:
    root = Path(__file__).resolve().parents[1]
    properties = ClawProperties(workspace_dir=Path(workspace_dir) if workspace_dir else root / "workspace")
    memory_service = MemoryService(properties.workspace_dir, today=today, now=now)
    session_startup = SessionStartup(properties.workspace_dir)
    skill_loader = SkillLoader()
    agent = ClawAgent(
        properties,
        memory_service,
        session_startup,
        skill_loader,
        template_dir=root / "resources" / "template",
    )
    agent.init()
    return ClawApplication(properties, memory_service, session_startup, skill_loader, agent)


def main() -> None:
    app = create_application()
    print(app.claw_agent.main_chat("你好"))


if __name__ == "__main__":
    main()
