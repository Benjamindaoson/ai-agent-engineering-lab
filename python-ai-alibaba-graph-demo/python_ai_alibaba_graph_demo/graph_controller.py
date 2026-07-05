from __future__ import annotations

from .simple_graph import CompiledGraph, MemorySaver, RunnableConfig


class GraphController:
    def __init__(
        self,
        *,
        simple_state_graph: CompiledGraph,
        conditional_state_graph: CompiledGraph,
        hello_state_graph: CompiledGraph,
        interrupt_before_state_graph: CompiledGraph,
        interrupt_state_graph: CompiledGraph,
        parallel_executor_state_graph: CompiledGraph,
        sub_state_graph: CompiledGraph,
        memory_saver: MemorySaver,
    ) -> None:
        self.simple_state_graph = simple_state_graph
        self.conditional_state_graph = conditional_state_graph
        self.hello_state_graph = hello_state_graph
        self.interrupt_before_graph = interrupt_before_state_graph
        self.interrupt_graph = interrupt_state_graph
        self.parallel_executor_state_graph = parallel_executor_state_graph
        self.sub_state_graph = sub_state_graph
        self.memory_saver = memory_saver

    def simple(self, subject: str) -> dict[str, object]:
        return self.simple_state_graph.invoke({"subject": subject})

    def stream(self, subject: str) -> list[str]:
        return [chunk for chunk in self.simple_state_graph.stream({"subject": subject}) if chunk.startswith("content:")]

    def conditional(self, input: str) -> dict[str, object]:
        return self.conditional_state_graph.invoke({"input": input})

    def thread(self, chat_id: str, input: str) -> str:
        state = self.hello_state_graph.invoke({"input": input, "chatId": chat_id}, RunnableConfig(thread_id=chat_id))
        return str(state["result"])

    def memory_saver_endpoint(self, chat_id: str, input: str) -> str:
        return self.thread(chat_id, input)

    def interrupt_before_state_graph(self, chat_id: str) -> list[str]:
        return self.interrupt_before_graph.stream({}, RunnableConfig(thread_id=chat_id))

    def continue_before_state_graph(self, chat_id: str, user_input: str) -> list[str]:
        config = RunnableConfig(thread_id=chat_id, metadata={"human_feedback": "placeholder"})
        self.interrupt_before_graph.update_state(config, {"humanFeedbackResult": user_input})
        return self.interrupt_before_graph.stream_from_initial_node(self.interrupt_before_graph.get_state(config), config)

    def interrupt_state_graph(self, chat_id: str) -> list[str]:
        return self.interrupt_graph.stream({}, RunnableConfig(thread_id=chat_id))

    def continue_state_graph(self, chat_id: str, user_input: str) -> list[str]:
        config = RunnableConfig(thread_id=chat_id, metadata={"human_feedback": "placeholder"})
        self.interrupt_graph.update_state(config, {"humanFeedbackResult": user_input})
        return self.interrupt_graph.stream_from_initial_node(self.interrupt_graph.get_state(config), config)

    def parallel(self) -> dict[str, object]:
        return self.parallel_executor_state_graph.invoke({})

    def sub_graph(self) -> dict[str, object]:
        return self.sub_state_graph.invoke({})
