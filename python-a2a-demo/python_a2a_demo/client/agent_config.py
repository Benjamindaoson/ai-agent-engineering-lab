from ..common import A2aRemoteAgent, AgentRegistry, ReactAgent, SequentialAgent


class AgentConfig:
    def __init__(self, agent_card_provider: AgentRegistry):
        self.agent_card_provider = agent_card_provider

    def a2a_remote_agent(self) -> A2aRemoteAgent:
        return A2aRemoteAgent(
            name="weatherAgent",
            registry=self.agent_card_provider,
            description="专门用于获取天气的远程智能体",
            instruction="用户输入：{input}",
        )

    def sequential_agent(self) -> SequentialAgent:
        weather_agent = self.a2a_remote_agent()
        react_agent = ReactAgent("reactAgent", "写诗")
        return SequentialAgent("sequentialAgent", [weather_agent, react_agent])
