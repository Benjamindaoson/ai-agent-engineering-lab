import json

from .file_tool import FileTool
from .zhouyu_agent_hook import ZhouyuAgentHook


class ReactAgent:
    def __init__(
        self,
        name: str,
        model,
        file_tool: FileTool | None = None,
        system_prompt: str = "",
        hooks: list[ZhouyuAgentHook] | None = None,
        max_steps: int = 8,
    ):
        self.name = name
        self.model = model
        self.file_tool = file_tool
        self.system_prompt = system_prompt
        self.hooks = hooks or []
        self.max_steps = max_steps

    def call(self, prompt: str) -> str:
        for hook in self.hooks:
            hook.before_agent(self.name)
        try:
            return self._call(prompt)
        finally:
            for hook in self.hooks:
                hook.after_agent(self.name)

    def _call(self, prompt: str) -> str:
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})
        tools = self.file_tool.tool_definitions() if self.file_tool else None

        last_content = ""
        for _ in range(self.max_steps):
            response = self.model.chat(messages, tools)
            content = response.get("content")
            tool_calls = response.get("tool_calls") or []
            if not tool_calls:
                return content or last_content

            assistant_message = {"role": "assistant", "content": content, "tool_calls": tool_calls}
            messages.append(assistant_message)
            if content:
                last_content = content

            for tool_call in tool_calls:
                function = tool_call.get("function") or {}
                name = function.get("name") or ""
                raw_arguments = function.get("arguments") or "{}"
                arguments = json.loads(raw_arguments) if isinstance(raw_arguments, str) else dict(raw_arguments)
                result = self.file_tool.execute_tool(name, arguments) if self.file_tool else f"Tool not available: {name}"
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id") or name,
                        "name": name,
                        "content": result,
                    }
                )
                last_content = result
        return last_content
