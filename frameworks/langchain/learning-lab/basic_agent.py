from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek


def get_weather(city: str) -> str:
    """Get weather data for city."""
    print(f"\n[TOOL 执行] get_weather(city={city})")
    return f"It's always sunny in {city}!"


model = ChatDeepSeek(
    model="deepseek-v4-flash",
)


agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="You are a helpful assistant.",
)


def main():
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "What's the weather in San Francisco?"
                }
            ]
        }
    )

    print("\n=== Agent 完整消息链 ===")

    for index, message in enumerate(result["messages"], start=1):
        print(f"\n--- 消息 {index} ---")
        print("类型：", type(message).__name__)
        print("内容：", message.content)

        if getattr(message, "tool_calls", None):
            print("Tool Calls：", message.tool_calls)

    print("\n=== 最终回答 ===")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()