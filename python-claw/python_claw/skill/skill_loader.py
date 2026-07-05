from __future__ import annotations

from pathlib import Path


class SkillLoader:
    def __init__(self) -> None:
        self.skills_dir: Path | None = None

    def initialize_skill_repository(self, skills_dir: str | Path) -> None:
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def load_all_skills(self) -> list[str]:
        if self.skills_dir is None:
            return []
        return sorted(path.name for path in self.skills_dir.iterdir() if (path / "SKILL.md").exists())

    def get_skill(self, skill_name: str) -> str | None:
        if self.skills_dir is None:
            return None
        path = self.skills_dir / skill_name / "SKILL.md"
        return path.read_text(encoding="utf-8") if path.exists() else None

    def has_skill(self, skill_name: str) -> bool:
        return self.get_skill(skill_name) is not None

    def get_skills_dir(self) -> Path:
        if self.skills_dir is None:
            raise RuntimeError("skill repository is not initialized")
        return self.skills_dir.resolve()
