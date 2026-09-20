from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import InMemorySaver


model = ChatDeepSeek(
    model="deepseek-v4-flash",
)


checkpointer = InMemorySaver()


agent = create_agent(
    model=model,
    tools=[],
    system_prompt="You are a helpful assistant.",
    checkpointer=checkpointer,
)


# =========================
# Thread A：第一轮
# =========================

config_a = {
    "configurable": {
        "thread_id": "thread-A"
    }
}


result_1 = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "请记住：我的项目代号叫 Apollo。只回复：记住了。"
            }
        ]
    },
    config=config_a,
)


print("=== Thread A：第一轮 ===")
print(result_1["messages"][-1].content)


# =========================
# Thread A：第二轮
# =========================

result_2 = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "我的项目代号叫什么？"
            }
        ]
    },
    config=config_a,
)


print("\n=== Thread A：第二轮 ===")
print(result_2["messages"][-1].content)


# =========================
# Thread B：新会话
# =========================

config_b = {
    "configurable": {
        "thread_id": "thread-B"
    }
}


result_3 = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "我的项目代号叫什么？如果不知道，就明确说不知道。"
            }
        ]
    },
    config=config_b,
)


print("\n=== Thread B：新会话 ===")
print(result_3["messages"][-1].content)