from python_ai_deepresearch.util import MAX_STEPS, get_prompt


class PlannerNode:
    def __init__(self, chat_client, max_steps: int = MAX_STEPS):
        self.chat_client = chat_client
        self.max_steps = max_steps

    def apply(self, state: dict) -> dict:
        system_prompt = get_prompt("planner").replace("{{max_steps}}", str(self.max_steps))
        result = self.chat_client.complete(system_prompt, state["input"], tools=["tavilySearch"])
        return {"plannerResult": result}
