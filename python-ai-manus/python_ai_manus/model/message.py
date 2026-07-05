from dataclasses import dataclass
from typing import Any

from .role import Role
from .tool_call import ToolCall


@dataclass
class Message:
    role: Role
    content: Any = None
    tool_calls: list[ToolCall] | None = None
    name: str | None = None
    tool_call_id: str | None = None
    base64_image: str | None = None

    @staticmethod
    def user_message(content: str, base64_image: str | None = None) -> "Message":
        return Message(Role.USER, content, base64_image=base64_image)

    @staticmethod
    def system_message(content: str) -> "Message":
        return Message(Role.SYSTEM, content)

    @staticmethod
    def assistant_message(content: str | None, base64_image: str | None = None) -> "Message":
        return Message(Role.ASSISTANT, content, base64_image=base64_image)

    @staticmethod
    def tool_message(
        content: str,
        name: str,
        tool_call_id: str,
        base64_image: str | None = None,
    ) -> "Message":
        return Message(Role.TOOL, content, name=name, tool_call_id=tool_call_id, base64_image=base64_image)

    def to_dict(self) -> dict[str, Any]:
        item: dict[str, Any] = {"role": self.role.value}
        if self.content is not None:
            if self.base64_image is not None:
                item["content"] = [
                    {"type": "text", "text": str(self.content)},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{self.base64_image}"}},
                ]
            else:
                item["content"] = self.content
        if self.tool_calls is not None:
            item["tool_calls"] = [tool_call.to_dict() for tool_call in self.tool_calls]
        if self.name is not None:
            item["name"] = self.name
        if self.tool_call_id is not None:
            item["tool_call_id"] = self.tool_call_id
        return item
