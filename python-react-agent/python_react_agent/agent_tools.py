import json
from pathlib import Path

from .tool import tool
from .tool_param import tool_param


class AgentTools:
    @tool(description="将指定内容写入本地文件。")
    @tool_param(name="json_input", description="包含 'file_path' 和 'content' 的 JSON 字符串。")
    def write_file(self, json_input: str) -> str:
        try:
            root = json.loads(json_input)
            file_path = Path(root["file_path"])
            content = root["content"]
            file_path.write_text(content, encoding="utf-8")
            return "写入成功"
        except (json.JSONDecodeError, KeyError, OSError, TypeError) as exc:
            return f"解析 ActionInput 或执行 write_file 工具时出错: {exc}"
