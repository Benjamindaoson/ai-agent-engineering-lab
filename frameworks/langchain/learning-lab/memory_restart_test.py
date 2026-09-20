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


config_a = {
    "configurable": {
        "thread_id": "thread-A"
    }
}


result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "我的项目代号叫什么？如果不知道，就明确说不知道。"
            }
        ]
    },
    config=config_a,
)


print("=== 新 Python 进程中的 thread-A ===")
print(result["messages"][-1].content)