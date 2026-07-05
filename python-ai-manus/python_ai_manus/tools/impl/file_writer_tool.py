from pathlib import Path
from typing import Any

from python_ai_manus.tools.base_tool import BaseTool
from python_ai_manus.tools.tool_result import ToolResult


class FileWriterTool(BaseTool):
    def __init__(self):
        super().__init__("write_file", "Write content to a file")

    def get_parameters_schema(self) -> dict[str, Any]:
        return self.build_schema(
            {
                "file_path": self.string_param("File path to write"),
                "content": self.string_param("Content to write"),
                "append": self.bool_param("Append instead of overwriting"),
            },
            ["file_path", "content"],
        )

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        file_path = self.get_string(parameters, "file_path")
        if not file_path:
            return ToolResult.failure("file_path is required")
        content = self.get_string(parameters, "content", "") or ""
        append = self.get_boolean(parameters, "append", False)
        path = Path(file_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if append:
                with path.open("a", encoding="utf-8") as file:
                    file.write(content)
            else:
                path.write_text(content, encoding="utf-8")
            return ToolResult.success(f"Successfully wrote file: {file_path}")
        except OSError as exc:
            return ToolResult.failure(f"Write file failed: {exc}")
