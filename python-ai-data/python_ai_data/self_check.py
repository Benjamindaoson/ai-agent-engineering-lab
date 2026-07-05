import json

from .data_application import DataWorkflow
from .dto import Plan
from .init_controller import create_demo_connection


class FakeClient:
    def __init__(self):
        self.responses = [
            '{"keywords":["orders"]}',
            '{"steps":[{"stepNum":1,"description":"count","sql":"select count(*) as count from orders"}]}',
            "<html>ok</html>",
        ]

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return self.responses.pop(0)


def main() -> None:
    plan = Plan.from_json('```json\n{"steps":[{"stepNum":1,"description":"count","sql":"select 1"}]}\n```')
    assert plan.steps[0].sql == "select 1"
    workflow = DataWorkflow(FakeClient(), create_demo_connection())
    assert workflow.run("count orders") == "<html>ok</html>"
    assert workflow.state["planExecuteResult"][0].success
    print("python-ai-data self-check passed")


if __name__ == "__main__":
    main()
