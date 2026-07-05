from dataclasses import dataclass


@dataclass
class Function:
    name: str
    arguments: str

    def to_dict(self) -> dict:
        return {"name": self.name, "arguments": self.arguments}
