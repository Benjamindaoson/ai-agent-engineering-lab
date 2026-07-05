from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


START = "__START__"
END = "__END__"


@dataclass
class Checkpoint:
    thread_id: str
    state: dict[str, object]


class MemorySaver:
    def __init__(self) -> None:
        self._items: dict[str, list[Checkpoint]] = {}

    def save(self, thread_id: str, state: dict[str, object]) -> None:
        self._items.setdefault(thread_id, []).append(Checkpoint(thread_id, dict(state)))

    def list(self, thread_id: str) -> list[Checkpoint]:
        return list(self._items.get(thread_id, []))


class MemoryStore:
    def __init__(self) -> None:
        self._items: dict[tuple[tuple[str, ...], str], dict[str, object]] = {}

    def put_item(self, namespace: list[str], key: str, value: dict[str, object]) -> None:
        self._items[(tuple(namespace), key)] = value

    def get_item(self, namespace: list[str], key: str) -> dict[str, object] | None:
        return self._items.get((tuple(namespace), key))


@dataclass
class RunnableConfig:
    thread_id: str = "default"
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class CompileConfig:
    saver: MemorySaver | None = None
    interrupt_before: set[str] = field(default_factory=set)
    observation_enabled: bool = False
    lifecycle_listeners: list[str] = field(default_factory=list)


class Interruption(Exception):
    def __init__(self, node: str, state: dict[str, object]) -> None:
        super().__init__(node)
        self.node = node
        self.state = state


class CompiledGraph:
    def __init__(
        self,
        nodes: dict[str, Callable[[dict[str, object], RunnableConfig], dict[str, object]]],
        edges: dict[str, list[str]],
        conditional_edges: dict[str, tuple[Callable[[dict[str, object]], str], dict[str, str]]] | None = None,
        compile_config: CompileConfig | None = None,
    ) -> None:
        self.nodes = nodes
        self.edges = edges
        self.conditional_edges = conditional_edges or {}
        self.compile_config = compile_config or CompileConfig()
        self._states: dict[str, dict[str, object]] = {}

    def invoke(self, inputs: dict[str, object], config: RunnableConfig | None = None) -> dict[str, object]:
        runnable_config = config or RunnableConfig()
        state = dict(inputs)
        try:
            return self._run(state, self._next(START, state), runnable_config)
        except Interruption as interruption:
            self._states[runnable_config.thread_id] = interruption.state
            return {"interrupted": True, "node": interruption.node, **interruption.state}

    def stream(self, inputs: dict[str, object], config: RunnableConfig | None = None) -> list[str]:
        state = self.invoke(inputs, config)
        if state.get("interrupted"):
            return ["中断了，请提供用户的年龄"]
        return self._stream_state(state)

    def update_state(self, config: RunnableConfig, values: dict[str, object]) -> RunnableConfig:
        state = self._states.setdefault(config.thread_id, {})
        state.update(values)
        return config

    def get_state(self, config: RunnableConfig) -> dict[str, object]:
        return dict(self._states.get(config.thread_id, {}))

    def stream_from_initial_node(self, state: dict[str, object], config: RunnableConfig) -> list[str]:
        current = str(state.get("_next_node", self._next(START, state)))
        if current == "node2" and state.get("humanFeedbackResult") != "next":
            self._states[config.thread_id] = dict(state)
            return ["再次中断了，请提供用户的年龄"]
        try:
            output = self._run(dict(state), current, config)
        except Interruption:
            return ["再次中断了，请提供用户的年龄"]
        return self._stream_state(output)

    def _run(self, state: dict[str, object], current: str, config: RunnableConfig) -> dict[str, object]:
        while current != END:
            if current in self.compile_config.interrupt_before and "human_feedback" not in config.metadata:
                state["_next_node"] = current
                raise Interruption(current, state)
            result = self.nodes[current](state, config)
            state.update(result)
            if self.compile_config.saver:
                self.compile_config.saver.save(config.thread_id, state)
            current = self._next(current, state)
        return state

    def _next(self, current: str, state: dict[str, object]) -> str:
        if current in self.conditional_edges:
            selector, mapping = self.conditional_edges[current]
            return mapping[selector(state)]
        targets = self.edges.get(current, [END])
        return targets[0]

    def _stream_state(self, state: dict[str, object]) -> list[str]:
        chunks: list[str] = []
        for key in ("node1Result", "node2Result", "node3Result", "content"):
            if key in state:
                value = state[key]
                if isinstance(value, list):
                    chunks.extend(str(item) for item in value)
                else:
                    chunks.append(str(value))
        return chunks
