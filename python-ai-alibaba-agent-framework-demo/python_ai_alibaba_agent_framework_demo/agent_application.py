from __future__ import annotations

from dataclasses import dataclass

from .agent.zhouyu_agent import ZhouyuAgent
from .agent_controller import AgentController
from .hooks.logging_hook import LoggingHook
from .hooks.zhouyu_model_hook import ZhouyuModelHook
from .interceptor.zhouyu_model_interceptor import ZhouyuModelInterceptor
from .interceptor.zhouyu_tool_interceptor import ZhouyuToolInterceptor
from .simple_framework import (
    LlmRoutingAgent,
    MemorySaver,
    MemoryStore,
    ParallelAgent,
    ReactAgent,
    SequentialAgent,
)
from .tools.date_tool import DateTool
from .tools.rag_tool import RagTool
from .tools.store_tool import StoreTool
from .tools.zhouyu_tools import ZhouyuTools


@dataclass
class AgentApplication:
    controller: AgentController
    memory_saver: MemorySaver
    hello_agent: ReactAgent
    memory_agent: ReactAgent
    hook_agent: ReactAgent
    human_hook_agent: ReactAgent
    store_agent: ReactAgent
    default_hook_agent: ReactAgent
    sequential_agent: SequentialAgent
    parallel_agent: ParallelAgent
    llm_routing_agent: LlmRoutingAgent
    zhouyu_agent: ZhouyuAgent
    complex_workflow: SequentialAgent
    tool_agent: ReactAgent
    rag_agent: ReactAgent


def create_application() -> AgentApplication:
    memory_saver = MemorySaver()
    memory_store = MemoryStore()
    memory_store.put_item(["user_info"], "user_002", {"username": "周瑜"})

    weather_tool = ZhouyuTools()
    hello_agent = ReactAgent(
        "helloAgent",
        system_prompt="简短的回答用户问题",
        tools={"getWeather": weather_tool, "getDate": DateTool()},
    )
    memory_agent = ReactAgent("memoryAgent", system_prompt="简短的回答用户问题", saver=memory_saver)
    hook_agent = ReactAgent(
        "hookAgent",
        system_prompt="简短的回答用户问题",
        tools={"getWeather": weather_tool},
        hooks=[LoggingHook(), ZhouyuModelHook()],
        model_interceptors=[ZhouyuModelInterceptor()],
        tool_interceptors=[ZhouyuToolInterceptor()],
    )
    human_hook_agent = ReactAgent(
        "humanHookAgent",
        tools={"getWeather": weather_tool},
        saver=MemorySaver(),
        human_approval_tools={"getWeather"},
    )
    store_agent = ReactAgent("storeAgent", tools={"getWeather": StoreTool()}, saver=MemorySaver())
    default_hook_agent = ReactAgent("defaultHookAgent", tools={"getWeather": weather_tool}, saver=MemorySaver())

    plan_agent = ReactAgent("planAgent", system_prompt="根据用户需求制定执行计划，你只负责制定计划，不要执行计划", output_key="planResult")
    execute_agent = ReactAgent("executeAgent", system_prompt="根据执行计划执行任务")
    sequential_agent = SequentialAgent("sequentialAgent", [plan_agent, execute_agent])

    backend_agent = ReactAgent("backendAgent", system_prompt="你是一个Python后端程序员", output_key="backendCode")
    python_agent = ReactAgent("pythonAgent", system_prompt="你是一个Python程序员", output_key="pythonCode")
    parallel_agent = ParallelAgent("parallelAgent", [backend_agent, python_agent], merge_output_key="code")

    code_agent = ReactAgent("agent1", description="这是一个专门用来写Python代码的Agent", system_prompt="你是一个程序员，写python")
    poem_agent = ReactAgent("agent2", description="这是一个专门用来写五言绝句的Agent", system_prompt="你是一个诗人，写五言绝句")
    llm_routing_agent = LlmRoutingAgent("llmRoutingAgent", [code_agent, poem_agent])

    zhouyu_agent = ZhouyuAgent("zhouyuAgent", "", [plan_agent, execute_agent])

    research_agent = ReactAgent("research_agent", description="进行背景研究", output_key="research_result")
    prose_agent = ReactAgent("prose_agent", output_key="prose")
    poem_parallel_agent = ReactAgent("poem_agent", output_key="poem")
    creative_agent = ParallelAgent("creative_agent", [prose_agent, poem_parallel_agent], merge_output_key="creative_outputs")
    review_agent = ReactAgent("review_agent", output_key="final_review")
    complex_workflow = SequentialAgent("complex_workflow", [research_agent, creative_agent, review_agent], "研究 -> 并行创作 -> 评审")

    tool_agent = ReactAgent(
        "toolAgent",
        tools={
            "planAgent": lambda text, context: plan_agent.call(text).text,
            "executeAgent": lambda text, context: execute_agent.call(text).text,
        },
    )
    rag_tool = RagTool(["api_key 需要查内部知识库", "外部搜索可以补充公开资料"])
    rag_agent = ReactAgent(
        "ragAgent",
        system_prompt="你是一个客服助手",
        output_key="rag",
        tools={"rag": rag_tool, "webSearchTool": lambda text, context: f"web:{text}"},
    )

    controller = AgentController(
        hello_agent=hello_agent,
        memory_agent=memory_agent,
        hook_agent=hook_agent,
        human_hook_agent=human_hook_agent,
        memory_saver=memory_saver,
        memory_store=memory_store,
        store_agent=store_agent,
        default_hook_agent=default_hook_agent,
        rag_agent=rag_agent,
    )
    return AgentApplication(
        controller,
        memory_saver,
        hello_agent,
        memory_agent,
        hook_agent,
        human_hook_agent,
        store_agent,
        default_hook_agent,
        sequential_agent,
        parallel_agent,
        llm_routing_agent,
        zhouyu_agent,
        complex_workflow,
        tool_agent,
        rag_agent,
    )


def main() -> None:
    app = create_application()
    print(app.controller.hello("杭州天气"))
    print(app.sequential_agent.invoke("写一个执行计划"))


if __name__ == "__main__":
    main()
