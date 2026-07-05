import json

from python_ai_data.dto import Plan
from python_ai_data.util import get_prompt


class PlannerNode:
    def __init__(self, chat_client):
        self.chat_client = chat_client

    def apply(self, state: dict) -> dict:
        table_infos = [table.to_dict() for table in state["tableInfoRecallResult"]]
        system_prompt = get_prompt("planner").replace("{{table_infos}}", json.dumps(table_infos, ensure_ascii=False))
        return {"plannerResult": Plan.from_json(self.chat_client.complete(system_prompt, state["input"]))}
