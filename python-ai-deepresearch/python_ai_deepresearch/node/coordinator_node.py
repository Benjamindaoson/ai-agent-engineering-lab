from python_ai_deepresearch.util import get_prompt


class CoordinatorNode:
    def __init__(self, chat_client):
        self.chat_client = chat_client

    def apply(self, state: dict) -> dict:
        user_input = state["input"]
        result = self.chat_client.complete(get_prompt("coordinator"), user_input)
        return {"coordinatorResult": result.strip()}
