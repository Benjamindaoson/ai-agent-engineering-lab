from __future__ import annotations

from ...memory.memory_service import MemoryService


class UpdateMemoryTool:
    def __init__(self, memory_service: MemoryService) -> None:
        self.memory_service = memory_service

    def update_memory(self, content: str, category: str = "event") -> str:
        if not content:
            return "错误：content 参数不能为空"
        handlers = {
            "preference": lambda: self.memory_service.log_significant_event(f"用户偏好：{content}"),
            "decision": lambda: self.memory_service.log_decision(content),
            "lesson": lambda: self.memory_service.log_lesson(content),
            "fact": lambda: self.memory_service.log_significant_event(f"重要事实：{content}"),
        }
        handlers.get((category or "event").lower(), lambda: self.memory_service.log_significant_event(content))()
        return f"记忆已更新：{content}"
