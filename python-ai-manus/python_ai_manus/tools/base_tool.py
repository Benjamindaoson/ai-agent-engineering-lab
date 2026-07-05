from typing import Any

from .tool import Tool


class BaseTool(Tool):
    def __init__(self, name: str, description: str):
        self._name = name
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def string_param(self, description: str) -> dict[str, Any]:
        return {"type": "string", "description": description}

    def bool_param(self, description: str) -> dict[str, Any]:
        return {"type": "boolean", "description": description}

    def int_param(self, description: str) -> dict[str, Any]:
        return {"type": "integer", "description": description}

    def enum_param(self, description: str, values: list[str]) -> dict[str, Any]:
        return {"type": "string", "description": description, "enum": values}

    def get_string(self, parameters: dict[str, Any], key: str, default: str | None = None) -> str | None:
        value = parameters.get(key)
        return str(value) if value is not None else default

    def get_boolean(self, parameters: dict[str, Any], key: str, default: bool = False) -> bool:
        value = parameters.get(key)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() == "true"
        return default

    def get_integer(self, parameters: dict[str, Any], key: str, default: int = 0) -> int:
        value = parameters.get(key)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def build_schema(self, properties: dict[str, dict[str, Any]], required: list[str] | None = None) -> dict[str, Any]:
        schema: dict[str, Any] = {"type": "object", "properties": properties}
        if required:
            schema["required"] = required
        return schema
