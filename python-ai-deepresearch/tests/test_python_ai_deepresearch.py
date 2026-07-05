import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from python_ai_deepresearch.deep_research_application import DeepResearchWorkflow
from python_ai_deepresearch.dto.plan import Plan
from python_ai_deepresearch.node.coordinator_node import CoordinatorNode
from python_ai_deepresearch.node.planner_node import PlannerNode
from python_ai_deepresearch.node.reporter_node import ReporterNode
from python_ai_deepresearch.node.researcher_node import ResearcherNode
from python_ai_deepresearch.observation_configuration import ObservationRegistry
from python_ai_deepresearch.parallel_streaming_example import parallel_streaming_with_node_id_preservation


class FakeChatClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def complete(self, system_prompt, user_prompt, tools=None):
        self.calls.append((system_prompt, user_prompt, tools))
        return self.responses.pop(0)


class FakeSearchTool:
    def search(self, query, max_results=3):
        return [{"title": "source", "url": "https://example.com", "snippet": f"info about {query}"}]


class PythonAiDeepResearchTest(unittest.TestCase):
    def test_plan_parses_plain_and_fenced_json(self):
        raw = '{"title":"AI","steps":[{"title":"History","prompt":"research history"}]}'
        fenced = "```json\n" + raw + "\n```"
        self.assertEqual(Plan.from_json(raw).steps[0].title, "History")
        self.assertEqual(Plan.from_json(fenced).title, "AI")

    def test_coordinator_node_sets_result(self):
        state = {"input": "research AI"}
        result = CoordinatorNode(FakeChatClient(["NEED_PLAN"])).apply(state)
        self.assertEqual(result["coordinatorResult"], "NEED_PLAN")

    def test_planner_node_replaces_max_steps_and_parses_later(self):
        client = FakeChatClient(['{"title":"AI","steps":[{"title":"Now","prompt":"research now"}]}'])
        result = PlannerNode(client, max_steps=3).apply({"input": "AI"})
        self.assertIn('"steps"', result["plannerResult"])
        self.assertIn("tavilySearch", client.calls[0][2])

    def test_researcher_node_uses_its_step(self):
        plan = Plan("AI", [])
        planner_result = json.dumps(
            {
                "title": "AI",
                "steps": [
                    {"title": "A", "prompt": "first"},
                    {"title": "B", "prompt": "second"},
                ],
            }
        )
        client = FakeChatClient(["research result"])
        result = ResearcherNode(client, 1).apply({"plannerResult": planner_result})
        self.assertEqual(result["researcherResult_1"], "research result")
        self.assertEqual(client.calls[0][1], "second")

    def test_reporter_node_combines_research_results(self):
        planner_result = '{"title":"AI","steps":[{"title":"A","prompt":"a"},{"title":"B","prompt":"b"}]}'
        client = FakeChatClient(["# Final Report"])
        result = ReporterNode(client).apply(
            {"plannerResult": planner_result, "researcherResult_0": "result A", "researcherResult_1": "result B"}
        )
        self.assertEqual(result["reporterResult"], "# Final Report")
        self.assertIn("result A", client.calls[0][1])
        self.assertIn("result B", client.calls[0][1])

    def test_workflow_runs_full_research_path(self):
        responses = [
            "NEED_PLAN",
            '{"title":"AI","steps":[{"title":"A","prompt":"a"},{"title":"B","prompt":"b"}]}',
            "research A",
            "research B",
            "# Report",
        ]
        workflow = DeepResearchWorkflow(FakeChatClient(responses), parallel=False)
        result = workflow.run("AI")
        self.assertEqual(result, "# Report")
        self.assertEqual(workflow.state["researcherResult_0"], "research A")
        self.assertEqual(workflow.state["researcherResult_1"], "research B")

    def test_workflow_returns_direct_coordinator_answer(self):
        workflow = DeepResearchWorkflow(FakeChatClient(["hello"]))
        self.assertEqual(workflow.run("hi"), "hello")
        self.assertNotIn("plannerResult", workflow.state)

    def test_observation_registry_records_tool_events(self):
        registry = ObservationRegistry()
        registry.on_tool_start("tavilySearch", {"query": "AI"})
        registry.on_tool_stop("tavilySearch", "ok")
        self.assertEqual(registry.events[0]["event"], "start")
        self.assertEqual(registry.events[1]["result"], "ok")

    def test_parallel_streaming_example_preserves_node_ids(self):
        summary = parallel_streaming_with_node_id_preservation()
        self.assertEqual(summary["node_counts"]["parallel_node_1"], 3)
        self.assertEqual(summary["node_counts"]["parallel_node_2"], 3)


if __name__ == "__main__":
    unittest.main()
