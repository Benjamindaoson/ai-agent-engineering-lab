import json
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from python_ai_engineer.file_tool import FileTool
from python_ai_engineer.plan import Plan
from python_ai_engineer.planner_agent_service import PlannerAgentService
from python_ai_engineer.react_agent import ReactAgent
from python_ai_engineer.zhouyu_agent_hook import ZhouyuAgentHook


class FakeTextAgent:
    def __init__(self, text):
        self.text = text
        self.calls = []

    def call(self, prompt):
        self.calls.append(prompt)
        return self.text


class FakeToolModel:
    def __init__(self, file_path):
        self.file_path = file_path
        self.calls = 0

    def chat(self, messages, tools=None):
        self.calls += 1
        if self.calls == 1:
            return {
                "content": "need to write a file",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "function": {
                            "name": "write_file",
                            "arguments": json.dumps({"file_path": str(self.file_path), "content": "hello"}),
                        },
                    }
                ],
                "finish_reason": "tool_calls",
            }
        return {"content": "done", "tool_calls": [], "finish_reason": "stop"}


class PythonAiEngineerTest(unittest.TestCase):
    def test_file_tool_writes_reads_and_lists_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = pathlib.Path(temp_dir) / "backend" / "app.py"
            tool = FileTool()
            self.assertIn("success", tool.write_file(str(path), "print('ok')").lower())
            self.assertEqual(tool.read_file(str(path)), "print('ok')")
            self.assertIn("backend", tool.list_project_files(temp_dir))

    def test_plan_parses_plain_json_and_fenced_json(self):
        raw = '{"steps":[{"stepNum":"1","agentName":"architectAgent","prompt":"design"}]}'
        fenced = "```json\n" + raw + "\n```"
        self.assertEqual(Plan.from_json(raw).steps[0].agent_name, "architectAgent")
        self.assertEqual(Plan.from_json(fenced).steps[0].prompt, "design")

    def test_planner_service_dispatches_steps_in_order(self):
        planner = FakeTextAgent(
            '{"steps":['
            '{"stepNum":"1","agentName":"architectAgent","prompt":"design"},'
            '{"stepNum":"2","agentName":"backendAgent","prompt":"backend"}'
            "]}"
        )
        architect = FakeTextAgent("architecture ok")
        backend = FakeTextAgent("backend ok")
        service = PlannerAgentService(planner, {"architectAgent": architect, "backendAgent": backend})

        plan = service.plan("build login")
        result = service.execute(plan)

        self.assertEqual([step.agent_name for step in plan.steps], ["architectAgent", "backendAgent"])
        self.assertEqual(architect.calls, ["design"])
        self.assertEqual(backend.calls, ["backend"])
        self.assertIn("complete", result.lower())

    def test_planner_service_reports_unknown_agent(self):
        service = PlannerAgentService(FakeTextAgent('{"steps":[]}'), {})
        plan = Plan.from_json('{"steps":[{"stepNum":"1","agentName":"missingAgent","prompt":"x"}]}')
        self.assertIn("missingAgent", service.execute(plan))

    def test_hook_records_before_and_after_events(self):
        hook = ZhouyuAgentHook()
        hook.before_agent("backendAgent")
        hook.after_agent("backendAgent")
        self.assertEqual(hook.events, ["Backend Agent started", "Backend Agent finished"])

    def test_react_agent_executes_file_tool_call(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = pathlib.Path(temp_dir) / "out.txt"
            agent = ReactAgent("backendAgent", FakeToolModel(file_path), FileTool(), hooks=[ZhouyuAgentHook()])
            result = agent.call("write file")
            self.assertEqual(file_path.read_text(encoding="utf-8"), "hello")
            self.assertIn("done", result)


if __name__ == "__main__":
    unittest.main()
