from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable


@dataclass
class AssistantMessage:
    text: str


@dataclass
class Checkpoint:
    thread_id: str
    input: str
    output: str


class MemorySaver:
    def __init__(self) -> None:
        self._items: dict[str, list[Checkpoint]] = {}

    def save(self, thread_id: str, input_text: str, output: str) -> None:
        self._items.setdefault(thread_id, []).append(Checkpoint(thread_id, input_text, output))

    def list(self, thread_id: str) -> list[Checkpoint]:
        return list(self._items.get(thread_id, []))


class MemoryStore:
    def __init__(self) -> None:
        self._items: dict[tuple[tuple[str, ...], str], dict[str, object]] = {}

    def put_item(self, namespace: Iterable[str], key: str, value: dict[str, object]) -> None:
        self._items[(tuple(namespace), key)] = value

    def get_item(self, namespace: Iterable[str], key: str) -> dict[str, object] | None:
        return self._items.get((tuple(namespace), key))


@dataclass
class RunnableConfig:
    thread_id: str = "default"
    store: MemoryStore | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class InterruptionMetadata:
    node: str
    state: dict[str, object]
    tool_feedbacks: list[dict[str, object]]


class ReactAgent:
    def __init__(
        self,
        name: str,
        *,
        system_prompt: str = "",
        description: str = "",
        output_key: str | None = None,
        tools: dict[str, Callable[[str, dict[str, object]], str]] | None = None,
        hooks: list[object] | None = None,
        model_interceptors: list[object] | None = None,
        tool_interceptors: list[object] | None = None,
        saver: MemorySaver | None = None,
        human_approval_tools: set[str] | None = None,
    ) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.description = description
        self.output_key = output_key
        self.tools = tools or {}
        self.hooks = hooks or []
        self.model_interceptors = model_interceptors or []
        self.tool_interceptors = tool_interceptors or []
        self.saver = saver
        self.human_approval_tools = human_approval_tools or set()

    def call(self, input_text: str, config: RunnableConfig | None = None) -> AssistantMessage:
        state = {"messages": [input_text], "events": []}
        for hook in self.hooks:
            if hasattr(hook, "before_agent"):
                state.update(hook.before_agent(state))
            if hasattr(hook, "before_model"):
                state.update(hook.before_model(state))

        def model_call() -> str:
            return self._run_tools(input_text, config, state) or self._model_text(input_text, config)

        result = model_call
        for interceptor in reversed(self.model_interceptors):
            current = result
            result = lambda interceptor=interceptor, current=current: interceptor.intercept(state["messages"], current)

        output = result()
        for hook in self.hooks:
            if hasattr(hook, "after_model"):
                state.update(hook.after_model(state))
            if hasattr(hook, "after_agent"):
                state.update(hook.after_agent(state))
        if state["events"]:
            output = f"{' | '.join(state['events'])} | {output}"
        if self.saver and config:
            self.saver.save(config.thread_id, input_text, output)
        return AssistantMessage(output)

    def stream(self, input_text: str) -> list[str]:
        return [f"chunk:{part}" for part in self.call(input_text).text.split()]

    def invoke(self, input_text: str, config: RunnableConfig | None = None) -> dict[str, object]:
        message = self.call(input_text, config)
        return {self.output_key or self.name: message.text, "messages": [input_text, message.text]}

    def invoke_and_get_output(self, input_text: str, config: RunnableConfig) -> AssistantMessage | InterruptionMetadata:
        feedback = config.metadata.get("human_feedback")
        if feedback:
            return AssistantMessage(f"{self.name}: APPROVED {feedback}")
        if self.human_approval_tools:
            feedback = {
                "name": sorted(self.human_approval_tools)[0],
                "arguments": {"input": input_text},
                "description": "请确认是否执行工具",
            }
            return InterruptionMetadata(self.name, {"input": input_text}, [feedback])
        return self.call(input_text, config)

    def _model_text(self, input_text: str, config: RunnableConfig | None = None) -> str:
        history = len(self.saver.list(config.thread_id)) if self.saver and config else 0
        suffix = f" history={history + 1}" if self.saver and config else ""
        return f"{self.name}: {self.system_prompt} input={input_text}{suffix}"

    def _run_tools(
        self,
        input_text: str,
        config: RunnableConfig | None,
        state: dict[str, object],
    ) -> str:
        if not self.tools:
            return ""
        context = {"input": input_text, "_AGENT_CONFIG_": config, "_AGENT_STATE_": state}
        parts = []
        for name, tool in self.tools.items():
            call = lambda name=name, tool=tool: tool(input_text, context)
            for interceptor in reversed(self.tool_interceptors):
                current = call
                call = lambda name=name, current=current, interceptor=interceptor: interceptor.intercept(name, current)
            parts.append(f"{name}={call()}")
        return f"{self.name}: " + "; ".join(parts)


class SequentialAgent:
    def __init__(self, name: str, sub_agents: list[ReactAgent], description: str = "") -> None:
        self.name = name
        self.sub_agents = sub_agents
        self.description = description

    def invoke(self, input_text: str) -> dict[str, object]:
        data: dict[str, object] = {"messages": [input_text]}
        current = input_text
        for agent in self.sub_agents:
            result = agent.invoke(current)
            data.update(result)
            current = result.get(getattr(agent, "output_key", None) or agent.name, current)
        return data


class ParallelAgent:
    def __init__(self, name: str, sub_agents: list[ReactAgent], merge_output_key: str = "code") -> None:
        self.name = name
        self.sub_agents = sub_agents
        self.merge_output_key = merge_output_key

    def invoke(self, input_text: str) -> dict[str, object]:
        data: dict[str, object] = {}
        for agent in self.sub_agents:
            data.update(agent.invoke(input_text))
        data[self.merge_output_key] = "\n".join(str(data.get(agent.output_key or agent.name, "")) for agent in self.sub_agents)
        return data


class LlmRoutingAgent:
    def __init__(self, name: str, sub_agents: list[ReactAgent]) -> None:
        self.name = name
        self.sub_agents = sub_agents

    def invoke(self, input_text: str) -> dict[str, object]:
        route = self.sub_agents[0] if "代码" in input_text.lower() or "python" in input_text.lower() else self.sub_agents[1]
        result = route.invoke(input_text)
        result["route"] = route.name
        return result
