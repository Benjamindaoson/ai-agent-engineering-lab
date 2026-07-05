import json
from dataclasses import dataclass, field

from .step import Step


@dataclass
class Plan:
    steps: list[Step] = field(default_factory=list)

    @classmethod
    def from_json(cls, text: str) -> "Plan":
        data = json.loads(_strip_json_fence(text))
        return cls([Step.from_dict(item) for item in data.get("steps", [])])

    def to_dict(self) -> dict:
        return {"steps": [step.to_dict() for step in self.steps]}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


def _strip_json_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped
