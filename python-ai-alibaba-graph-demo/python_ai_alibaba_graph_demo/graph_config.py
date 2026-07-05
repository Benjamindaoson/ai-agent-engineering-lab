from __future__ import annotations

from dataclasses import dataclass

from .blog.content_node_action import ContentNodeAction
from .blog.title_node_action import TitleNodeAction
from .interrupt.interruptable_node_action import InterruptableNodeAction
from .simple_graph import (
    END,
    START,
    CompileConfig,
    CompiledGraph,
    MemorySaver,
    MemoryStore,
    RunnableConfig,
)


@dataclass
class GraphConfig:
    memory_saver: MemorySaver
    memory_store: MemoryStore

    def simple_state_graph(self) -> CompiledGraph:
        return CompiledGraph(
            nodes={
                "title": lambda state, config: TitleNodeAction().apply(state),
                "content": lambda state, config: ContentNodeAction().apply(state),
            },
            edges={START: ["title"], "title": ["content"], "content": [END]},
        )

    def conditional_state_graph(self) -> CompiledGraph:
        def intention(state: dict[str, object], config: RunnableConfig) -> dict[str, object]:
            text = str(state["input"])
            return {"intentionResult": "2" if "代码" in text or "Python" in text else "1"}

        def poem(state: dict[str, object], config: RunnableConfig) -> dict[str, object]:
            return {"result": f"七言绝句：{state['input']}"}

        def code(state: dict[str, object], config: RunnableConfig) -> dict[str, object]:
            return {"result": f"Python代码：# {state['input']}"}

        return CompiledGraph(
            nodes={"intention": intention, "poem": poem, "code": code},
            edges={START: ["intention"], "poem": [END], "code": [END]},
            conditional_edges={
                "intention": (lambda state: str(state["intentionResult"]), {"1": "poem", "2": "code"})
            },
        )

    def hello_state_graph(self) -> CompiledGraph:
        def hello(state: dict[str, object], config: RunnableConfig) -> dict[str, object]:
            user = self.memory_store.get_item(["user_info"], "user_002") or {"username": "未知用户"}
            return {"result": f"{user['username']} 收到：{state['input']}"}

        return CompiledGraph(
            nodes={"hello": hello},
            edges={START: ["hello"], "hello": [END]},
            compile_config=CompileConfig(saver=self.memory_saver),
        )

    def interrupt_before_state_graph(self) -> CompiledGraph:
        return CompiledGraph(
            nodes={
                "node1": lambda state, config: {"node1Result": ["我是节点1"]},
                "node2": lambda state, config: {"node2Result": ["我是节点2"]},
                "node3": lambda state, config: {"node3Result": ["我是节点3"]},
            },
            edges={START: ["node1"], "node1": ["node2"], "node3": [END]},
            conditional_edges={
                "node2": (
                    lambda state: "next" if state.get("humanFeedbackResult") == "next" else "unknown",
                    {"next": "node3", "unknown": "node2"},
                )
            },
            compile_config=CompileConfig(saver=self.memory_saver, interrupt_before={"node2"}),
        )

    def interrupt_state_graph(self) -> CompiledGraph:
        return CompiledGraph(
            nodes={
                "node1": lambda state, config: {"node1Result": ["我是节点1"]},
                "node2": InterruptableNodeAction(),
                "node3": lambda state, config: {"node3Result": ["我是节点3"]},
            },
            edges={START: ["node1"], "node1": ["node2"], "node3": [END]},
            conditional_edges={
                "node2": (
                    lambda state: "next" if state.get("humanFeedbackResult") == "next" else "unknown",
                    {"next": "node3", "unknown": "node2"},
                )
            },
            compile_config=CompileConfig(saver=self.memory_saver),
        )

    def parallel_executor_state_graph(self) -> CompiledGraph:
        def run_parallel(state: dict[str, object], config: RunnableConfig) -> dict[str, object]:
            return {"b_complete": True, "c_complete": True, "next_node": END}

        return CompiledGraph(
            nodes={"a": run_parallel},
            edges={START: ["a"], "a": [END]},
        )

    def sub_state_graph(self) -> CompiledGraph:
        def parent(state: dict[str, object], config: RunnableConfig) -> dict[str, object]:
            return {"ids": {"a": "A", "b1": "B1", "b2": "B2", "c": "C"}}

        return CompiledGraph(
            nodes={"A": parent},
            edges={START: ["A"], "A": [END]},
        )


def create_graph_config() -> GraphConfig:
    memory_saver = MemorySaver()
    memory_store = MemoryStore()
    memory_store.put_item(["user_info"], "user_002", {"username": "周瑜"})
    return GraphConfig(memory_saver=memory_saver, memory_store=memory_store)
