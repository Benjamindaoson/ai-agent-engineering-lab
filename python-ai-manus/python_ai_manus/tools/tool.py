from abc import ABC, abstractmethod
from typing import Any

from python_ai_manus.model import ToolDefinition


class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_parameters_schema(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def execute(self, parameters: dict[str, Any]) -> "ToolResult":
        raise NotImplementedError

    def to_definition(self) -> ToolDefinition:
        return ToolDefinition(self.name, self.description, self.get_parameters_schema())
