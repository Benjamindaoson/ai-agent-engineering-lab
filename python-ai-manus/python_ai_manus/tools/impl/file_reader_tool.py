from pathlib import Path
from typing import Any

from python_ai_manus.tools.base_tool import BaseTool
from python_ai_manus.tools.tool_result import ToolResult


class FileReaderTool(BaseTool):
    def __init__(self):
        super().__init__("read_file", "Read file content")

    def get_parameters_schema(self) -> dict[str, Any]:
        return self.build_schema({"file_path": self.string_param("File path to read")}, ["file_path"])

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        file_path = self.get_string(parameters, "file_path")
        if not file_path:
            return ToolResult.failure("file_path is required")
        path = Path(file_path)
        if not path.exists():
            return ToolResult.failure(f"File does not exist: {file_path}")
        try:
            return ToolResult.success(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return ToolResult.failure(f"Read file failed: {exc}")
