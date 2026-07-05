from pathlib import Path


class FileTool:
    def list_project_files(self, path: str) -> str:
        directory = Path(path)
        if not directory.exists():
            return f"Directory does not exist: {path}"
        try:
            return "\n".join(sorted(item.name for item in directory.iterdir()))
        except OSError as exc:
            return f"List files failed: {exc}"

    def read_file(self, file_path: str) -> str:
        path = Path(file_path)
        if not path.exists():
            return f"File does not exist: {file_path}"
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            return f"Read file failed: {exc}"

    def write_file(self, file_path: str, content: str) -> str:
        path = Path(file_path)
        try:
            if path.parent:
                path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return f"File write success: {file_path}"
        except OSError as exc:
            return f"Write file failed: {exc}"

    def tool_definitions(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_project_files",
                    "description": "List files in a project directory",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string", "description": "Directory path"}},
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read a file",
                    "parameters": {
                        "type": "object",
                        "properties": {"file_path": {"type": "string", "description": "File path"}},
                        "required": ["file_path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "File path"},
                            "content": {"type": "string", "description": "File content"},
                        },
                        "required": ["file_path", "content"],
                    },
                },
            },
        ]

    def execute_tool(self, name: str, arguments: dict) -> str:
        if name == "list_project_files":
            return self.list_project_files(str(arguments.get("path") or ""))
        if name == "read_file":
            return self.read_file(str(arguments.get("file_path") or ""))
        if name == "write_file":
            return self.write_file(str(arguments.get("file_path") or ""), str(arguments.get("content") or ""))
        return f"Tool not found: {name}"
