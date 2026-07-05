from python_ai_deepresearch.dto import Plan
from python_ai_deepresearch.util import get_prompt


class ReporterNode:
    def __init__(self, chat_client):
        self.chat_client = chat_client

    def apply(self, state: dict) -> dict:
        plan = Plan.from_json(state["plannerResult"])
        research_notes = []
        for index, step in enumerate(plan.steps):
            research_notes.append(f"## {step.title}\n{state[f'researcherResult_{index}']}")
        result = self.chat_client.complete(get_prompt("reporter"), "\n\n".join(research_notes), tools=["tavilySearch"])
        return {"reporterResult": result}
