from dataclasses import dataclass

from .function import Function


@dataclass
class ToolCall:
    id: str
    function: Function
    type: str = "function"

    def to_dict(self) -> dict:
        return {"id": self.id, "type": self.type, "function": self.function.to_dict()}
