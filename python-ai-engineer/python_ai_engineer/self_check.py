import tempfile
from pathlib import Path

from .file_tool import FileTool
from .plan import Plan
from .planner_agent_service import PlannerAgentService


class FakeAgent:
    def __init__(self, text):
        self.text = text
        self.calls = []

    def call(self, prompt):
        self.calls.append(prompt)
        return self.text


def main() -> None:
    plan = Plan.from_json('{"steps":[{"stepNum":"1","agentName":"architectAgent","prompt":"design"}]}')
    assert plan.steps[0].agent_name == "architectAgent"

    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "a" / "demo.txt"
        tool = FileTool()
        assert "success" in tool.write_file(str(path), "ok").lower()
        assert tool.read_file(str(path)) == "ok"

    planner = FakeAgent('{"steps":[{"stepNum":"1","agentName":"architectAgent","prompt":"design"}]}')
    architect = FakeAgent("ok")
    service = PlannerAgentService(planner, {"architectAgent": architect})
    assert "complete" in service.execute(service.plan("build")).lower()
    assert architect.calls == ["design"]
    print("python-ai-engineer self-check passed")


if __name__ == "__main__":
    main()
