from dataclasses import dataclass


@dataclass
class Step:
    title: str
    prompt: str

    @classmethod
    def from_dict(cls, data: dict) -> "Step":
        return cls(title=str(data.get("title") or ""), prompt=str(data.get("prompt") or ""))

    def to_dict(self) -> dict:
        return {"title": self.title, "prompt": self.prompt}
