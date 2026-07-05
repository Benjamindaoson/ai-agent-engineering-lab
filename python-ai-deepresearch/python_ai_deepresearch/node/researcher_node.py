from python_ai_deepresearch.dto import Plan
from python_ai_deepresearch.util import get_prompt


class ResearcherNode:
    def __init__(self, chat_client, step_num: int):
        self.chat_client = chat_client
        self.step_num = step_num

    def apply(self, state: dict) -> dict:
        plan = Plan.from_json(state["plannerResult"])
        step = plan.steps[self.step_num]
        result = self.chat_client.complete(get_prompt("researcher"), step.prompt, tools=["tavilySearch"])
        return {f"researcherResult_{self.step_num}": result}
