import json

from .deep_research_application import DeepResearchWorkflow
from .dto import Plan


class FakeClient:
    def __init__(self):
        self.responses = [
            "NEED_PLAN",
            json.dumps({"title": "T", "steps": [{"title": "A", "prompt": "a"}]}),
            "research",
            "report",
        ]

    def complete(self, system_prompt: str, user_prompt: str, tools=None) -> str:
        return self.responses.pop(0)


def main() -> None:
    plan = Plan.from_json('```json\n{"title":"T","steps":[{"title":"A","prompt":"a"}]}\n```')
    assert plan.title == "T"
    assert plan.steps[0].prompt == "a"

    workflow = DeepResearchWorkflow(FakeClient(), parallel=False)
    assert workflow.run("topic") == "report"
    assert workflow.state["researcherResult_0"] == "research"
    print("python-ai-deepresearch self-check passed")


if __name__ == "__main__":
    main()
