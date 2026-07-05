import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable


@dataclass
class Msg:
    text: str = ""
    name: str = "user"
    role: str = "user"
    pending_tools: list[dict[str, Any]] = field(default_factory=list)
    structured_data: Any = None
    visible_tool_input: str = ""
    generate_reason: str = "stop"

    @classmethod
    def text(cls, content: str, name: str = "user", role: str = "user") -> "Msg":
        return cls(text=content, name=name, role=role)


class FakeChatModel:
    """Deterministic model for classroom smoke tests."""

    def generate(self, agent_name: str, sys_prompt: str, user_text: str) -> str:
        if "研究员" in sys_prompt:
            return f"研究员发现：{user_text} 有清晰应用场景。"
        if "作家" in sys_prompt:
            return f"作家摘要：基于上一阶段内容整理出简洁说明。"
        if "编辑" in sys_prompt:
            return f"编辑定稿：内容完整、表达简洁。输入：{user_text}"
        if "乐观主义者" in sys_prompt:
            return "积极方面：持续练习会带来复利。"
        if "悲观主义者" in sys_prompt:
            return "风险方面：缺少反馈会走偏。"
        if "现实主义者" in sys_prompt:
            return "平衡建议：设目标、做项目、找反馈。"
        if "老师" in sys_prompt:
            return "我是 Alice，负责用简洁方式讲清楚问题。"
        if "学生" in sys_prompt:
            return "我是 Bob，会提出问题并记录要点。"
        if "观察者" in sys_prompt:
            return "我是 Jams，会总结大家的观点。"
        if "辩论者" in sys_prompt:
            return f"{agent_name} 观点：技术和业务需要结合。"
        if "主持人" in sys_prompt:
            return "没有唯一正确答案，关键是服务业务目标。"
        return f"{agent_name}: 已收到 {user_text}"


class InMemoryMemory:
    def __init__(self) -> None:
        self.messages: list[Msg] = []

    def add(self, msg: Msg) -> None:
        self.messages.append(msg)

    def save_to(self, session_root: Path, session_id: str) -> None:
        session_dir = session_root / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        target = session_dir / "memory_messages.jsonl"
        with target.open("w", encoding="utf-8") as file:
            for msg in self.messages:
                file.write(json.dumps(asdict(msg), ensure_ascii=False) + "\n")

    def load_from(self, session_root: Path, session_id: str) -> None:
        target = session_root / session_id / "memory_messages.jsonl"
        self.messages.clear()
        if not target.exists():
            return
        with target.open("r", encoding="utf-8") as file:
            for line in file:
                data = json.loads(line)
                self.messages.append(Msg(**data))


class Toolkit:
    def __init__(self) -> None:
        self.tools: list[Any] = []
        self.tool_groups: dict[str, dict[str, Any]] = {}
        self.tool_to_group: dict[int, str] = {}
        self.presets: dict[str, dict[str, Any]] = {}
        self.context: dict[str, Any] = {}
        self.chunk_callback: Callable[[dict[str, Any], str], None] | None = None
        self.mcp_clients: list[str] = []

    def create_tool_group(self, name: str, description: str) -> None:
        self.tool_groups[name] = {"description": description, "enabled": True}

    def update_tool_groups(self, names: Iterable[str], enabled: bool) -> None:
        for name in names:
            if name in self.tool_groups:
                self.tool_groups[name]["enabled"] = enabled

    def register_tool(
        self,
        tool: Any,
        group: str | None = None,
        preset_parameters: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self.tools.append(tool)
        if group:
            self.tool_to_group[id(tool)] = group
        if preset_parameters:
            for method, values in preset_parameters.items():
                self.presets[method] = values

    def register_context(self, name: str, value: Any) -> None:
        self.context[name] = value

    def set_chunk_callback(self, callback: Callable[[dict[str, Any], str], None]) -> None:
        self.chunk_callback = callback

    def register_mcp_client(self, name: str) -> None:
        self.mcp_clients.append(name)

    def _enabled(self, tool: Any) -> bool:
        group = self.tool_to_group.get(id(tool))
        return group is None or self.tool_groups.get(group, {}).get("enabled", True)

    def weather(self, city: str) -> str | None:
        for tool in self.tools:
            if self._enabled(tool) and hasattr(tool, "get_weather"):
                return tool.get_weather(city)
        return None

    def generate(self, count: int) -> tuple[str, list[str]]:
        for tool in self.tools:
            if self._enabled(tool) and hasattr(tool, "generate"):
                chunks: list[str] = []

                def emit(text: str) -> None:
                    chunks.append(text)
                    if self.chunk_callback:
                        self.chunk_callback({"name": "generate", "input": {"count": count}}, text)

                result = tool.generate(count, emit)
                if self.chunk_callback:
                    self.chunk_callback({"name": "generate", "input": {"count": count}}, result)
                return result, chunks + [result]
        return "没有可用工具", []

    def query(self, sql: str) -> str | None:
        for tool in self.tools:
            if self._enabled(tool) and hasattr(tool, "query"):
                return tool.query(sql, self.context.get("user"))
        return None

    def send_email(self, to: str, subject: str) -> tuple[str, str] | None:
        for tool in self.tools:
            if self._enabled(tool) and hasattr(tool, "send"):
                api_key = self.presets.get("send", {}).get("apiKey", "")
                result = tool.send(to, subject, api_key)
                return result, json.dumps({"to": to, "subject": subject}, ensure_ascii=False)
        return None


class LoggingHook:
    def __init__(self) -> None:
        self.events: list[str] = []

    def on_event(self, event: str, msg: Msg) -> bool:
        self.events.append(f"{event}:{msg.text}")
        return True


class ConfirmationHook:
    sensitive_tools = {"delete_file", "generate"}

    def on_event(self, event: str, msg: Msg) -> bool:
        return not any(tool["name"] in self.sensitive_tools for tool in msg.pending_tools)


class ReActAgent:
    def __init__(
        self,
        name: str,
        sys_prompt: str = "",
        model: FakeChatModel | None = None,
        toolkit: Toolkit | None = None,
        memory: InMemoryMemory | None = None,
        hooks: list[Any] | None = None,
    ) -> None:
        self.name = name
        self.sys_prompt = sys_prompt
        self.model = model or FakeChatModel()
        self.toolkit = toolkit
        self.memory = memory
        self.hooks = hooks or []

    def call(self, msg: Msg | None = None, structured_type: type | None = None) -> Msg:
        user_text = msg.text if msg else ""
        if structured_type is not None:
            data = structured_type(name="课程演示产品", price=99.0, features=["结构化输出", "离线可测"])
            return Msg(text=str(data), name=self.name, role="assistant", structured_data=data)

        if self.toolkit:
            generated = self._try_tools(user_text)
            if generated is not None:
                return generated

        response = Msg(
            text=self.model.generate(self.name, self.sys_prompt, user_text),
            name=self.name,
            role="assistant",
        )
        if self.memory:
            self.memory.add(response)
        return response

    def _try_tools(self, user_text: str) -> Msg | None:
        assert self.toolkit is not None
        if "天气" in user_text:
            city = user_text.split("什么天气")[0].strip() or "上海"
            result = self.toolkit.weather(city)
            return Msg(text=result or "没有可用工具：weather", name=self.name, role="assistant")
        if "生成" in user_text and "数据" in user_text:
            count = _first_int(user_text, default=10)
            pending = Msg(
                text="等待人工确认",
                name=self.name,
                role="assistant",
                pending_tools=[{"name": "generate", "input": {"count": count}}],
                generate_reason="tool_calls",
            )
            for hook in self.hooks:
                if not hook.on_event("post_reasoning", pending):
                    return pending
            result, _ = self.toolkit.generate(count)
            return Msg(text=result, name=self.name, role="assistant")
        if "订单数据" in user_text:
            result = self.toolkit.query("select * from orders")
            return Msg(text=result or "没有可用工具：query", name=self.name, role="assistant")
        if "发邮件" in user_text:
            sent = self.toolkit.send_email("zhouyu", "Java")
            if sent:
                result, visible_input = sent
                return Msg(text=result, name=self.name, role="assistant", visible_tool_input=visible_input)
        return None


class MsgHub:
    def __init__(self, participants: list[ReActAgent], announcement: Msg | None = None, name: str = "hub") -> None:
        self.participants = participants
        self.announcement = announcement
        self.name = name

    def __enter__(self) -> "MsgHub":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None

    def enter(self) -> None:
        if not self.announcement:
            return
        for participant in self.participants:
            if participant.memory:
                participant.memory.add(self.announcement)


def sequential(agents: list[ReActAgent], msg: Msg) -> Msg:
    current = msg
    for agent in agents:
        current = agent.call(current)
    return current


def fanout(agents: list[ReActAgent], msg: Msg) -> list[Msg]:
    return [agent.call(msg) for agent in agents]


def _first_int(text: str, default: int) -> int:
    digits = "".join(ch if ch.isdigit() else " " for ch in text).split()
    return int(digits[0]) if digits else default
