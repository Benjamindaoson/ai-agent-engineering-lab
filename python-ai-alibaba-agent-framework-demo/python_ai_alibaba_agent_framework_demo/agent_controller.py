from __future__ import annotations

from .simple_framework import InterruptionMetadata, MemorySaver, MemoryStore, ReactAgent, RunnableConfig


class AgentController:
    def __init__(
        self,
        *,
        hello_agent: ReactAgent,
        memory_agent: ReactAgent,
        hook_agent: ReactAgent,
        human_hook_agent: ReactAgent,
        memory_saver: MemorySaver,
        memory_store: MemoryStore,
        store_agent: ReactAgent,
        default_hook_agent: ReactAgent,
        rag_agent: ReactAgent,
    ) -> None:
        self.hello_agent = hello_agent
        self.memory_agent = memory_agent
        self.hook_agent = hook_agent
        self.human_hook_agent = human_hook_agent
        self.memory_saver = memory_saver
        self.memory_store = memory_store
        self.store_agent = store_agent
        self.default_hook_agent = default_hook_agent
        self.rag_agent = rag_agent
        self.interruption_metadata_sessions: dict[str, InterruptionMetadata] = {}

    def hello(self, input: str) -> str:
        return self.hello_agent.call(input).text

    def stream(self, input: str) -> list[str]:
        return self.hello_agent.stream(input)

    def memory(self, input: str, chat_id: str) -> str:
        return self.memory_agent.call(input, RunnableConfig(thread_id=chat_id)).text

    def tool_context(self, input: str) -> str:
        return self.hello_agent.call(input).text

    def hook(self, input: str) -> str:
        return self.hook_agent.call(input).text

    def human_hook(self, input: str, thread_id: str) -> str:
        result = self.human_hook_agent.invoke_and_get_output(input, RunnableConfig(thread_id=thread_id))
        if isinstance(result, InterruptionMetadata):
            self.interruption_metadata_sessions[thread_id] = result
            return str(result.tool_feedbacks[0]["description"])
        return result.text

    def human_agent_feedback(self, thread_id: str) -> str:
        interruption = self.interruption_metadata_sessions[thread_id]
        feedback = [{**item, "result": "APPROVED"} for item in interruption.tool_feedbacks]
        config = RunnableConfig(thread_id=thread_id, metadata={"human_feedback": feedback})
        return self.human_hook_agent.invoke_and_get_output("", config).text

    def store(self, input: str, thread_id: str) -> str:
        config = RunnableConfig(thread_id=thread_id, store=self.memory_store)
        return self.store_agent.call(input, config).text

    def default_hook(self, input: str, thread_id: str) -> str:
        return self.default_hook_agent.call(input, RunnableConfig(thread_id=thread_id)).text

    def multi_agent(self, input: str) -> dict[str, object]:
        return self.rag_agent.invoke(input)
