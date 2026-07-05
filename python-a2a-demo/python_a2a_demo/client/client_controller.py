from ..common import A2aRemoteAgent, SequentialAgent


class ClientController:
    def __init__(self, a2a_remote_agent: A2aRemoteAgent, sequential_agent: SequentialAgent):
        self.a2a_remote_agent = a2a_remote_agent
        self.sequential_agent = sequential_agent

    def hello(self, input_text: str) -> dict:
        return self.sequential_agent.invoke(input_text)
