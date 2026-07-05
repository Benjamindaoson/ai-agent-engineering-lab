import json

from python_ai_data.util import get_prompt


class ReportGeneratorNode:
    def __init__(self, chat_client):
        self.chat_client = chat_client

    def apply(self, state: dict) -> dict:
        plan = state["plannerResult"]
        step_results = {
            str(index): value.to_dict() if hasattr(value, "to_dict") else str(value)
            for index, value in state.get("planExecuteResult", {}).items()
        }
        prompt = (
            get_prompt("report")
            .replace("{{user_input}}", state["input"])
            .replace("{{plan}}", plan.to_json())
            .replace("{{stepResult}}", json.dumps(step_results, ensure_ascii=False))
        )
        return {"reportGeneratorResult": self.chat_client.complete("", prompt)}
