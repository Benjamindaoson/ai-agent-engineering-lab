import json
import pathlib
import sqlite3
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from python_ai_data.data_application import DataWorkflow
from python_ai_data.data_controller import DataController
from python_ai_data.dto.plan import Plan
from python_ai_data.dto.step import Step
from python_ai_data.init_controller import InitController
from python_ai_data.node.keywords_extract_node import KeywordsExtractNode
from python_ai_data.node.plan_execute_node import PlanExecuteNode
from python_ai_data.node.planner_node import PlannerNode
from python_ai_data.node.report_generator_node import ReportGeneratorNode
from python_ai_data.node.sql_execute_node import SqlExecuteNode
from python_ai_data.node.table_info_recall_node import TableInfoRecallNode


_DBS = []


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def complete(self, system_prompt, user_prompt):
        self.calls.append((system_prompt, user_prompt))
        return self.responses.pop(0)


def make_db():
    conn = sqlite3.connect(":memory:")
    _DBS.append(conn)
    conn.execute("create table orders (order_id integer, total_amount real, status text)")
    conn.execute("insert into orders values (1, 100.0, 'paid')")
    conn.execute("insert into orders values (2, 50.0, 'pending')")
    conn.execute("create table products (product_id integer, product_name text, sales integer)")
    conn.execute("insert into products values (1, 'phone', 20)")
    conn.commit()
    return conn


class PythonAiDataTest(unittest.TestCase):
    def tearDown(self):
        while _DBS:
            _DBS.pop().close()

    def test_plan_parses_plain_and_fenced_json(self):
        raw = '{"steps":[{"stepNum":1,"description":"sum orders","sql":"select count(*) from orders"}]}'
        fenced = "```json\n" + raw + "\n```"
        self.assertEqual(Plan.from_json(raw).steps[0].step_num, 1)
        self.assertIn("orders", Plan.from_json(fenced).steps[0].sql)

    def test_keywords_extract_node_sets_json_result(self):
        result = KeywordsExtractNode(FakeClient(['{"keywords":["orders","amount"]}'])).apply({"input": "order amount"})
        self.assertEqual(json.loads(result["keywordsExtractResult"])["keywords"], ["orders", "amount"])

    def test_table_info_recall_finds_matching_schema(self):
        tables = InitController(make_db()).init()
        node = TableInfoRecallNode(tables)
        result = node.apply({"keywordsExtractResult": '{"keywords":["orders","amount"]}'})
        self.assertEqual(result["tableInfoRecallResult"][0].table_name, "orders")

    def test_planner_node_parses_plan(self):
        client = FakeClient(['{"steps":[{"stepNum":1,"description":"sum","sql":"select sum(total_amount) from orders"}]}'])
        result = PlannerNode(client).apply({"input": "sum", "tableInfoRecallResult": []})
        self.assertEqual(result["plannerResult"].steps[0].description, "sum")

    def test_sql_execute_node_records_success_and_failure(self):
        conn = make_db()
        plan = Plan([Step(1, "bad", "select missing from orders")])
        fail = SqlExecuteNode(conn).apply({"plannerResult": plan, "currentStepNum": 0})
        self.assertFalse(fail["planExecuteResult"][0].success)

        plan.steps[0].sql = "select count(*) as count from orders"
        ok = SqlExecuteNode(conn).apply({"plannerResult": plan, "currentStepNum": 0})
        self.assertTrue(ok["planExecuteResult"][0].success)
        self.assertIn("count", ok["planExecuteResult"][0].data)

    def test_plan_execute_node_repairs_failed_sql(self):
        plan = Plan([Step(1, "count", "select missing from orders")])
        state = {"plannerResult": plan, "currentStepNum": 0}
        first = PlanExecuteNode(FakeClient([])).apply(state)
        self.assertEqual(first["planExecuteNextNode"], "sql")

        state.update(first)
        state["planExecuteResult"] = {0: SqlExecuteNode(make_db()).apply(state)["planExecuteResult"][0]}
        repaired = PlanExecuteNode(FakeClient(["select count(*) as count from orders"])).apply(state)
        self.assertEqual(repaired["plannerResult"].steps[0].sql, "select count(*) as count from orders")

    def test_full_workflow_generates_report_after_sql_repair(self):
        client = FakeClient(
            [
                '{"keywords":["orders"]}',
                '{"steps":[{"stepNum":1,"description":"count orders","sql":"select missing from orders"}]}',
                "select count(*) as count from orders",
                "<html>report</html>",
            ]
        )
        workflow = DataWorkflow(client, make_db())
        result = workflow.run("How many orders?")
        self.assertEqual(result, "<html>report</html>")
        self.assertTrue(workflow.state["planExecuteResult"][0].success)

    def test_controller_can_continue_with_revised_plan(self):
        client = FakeClient(
            [
                '{"keywords":["orders"]}',
                '{"steps":[{"stepNum":1,"description":"count orders","sql":"select count(*) as count from orders"}]}',
                '{"steps":[{"stepNum":1,"description":"sum orders","sql":"select sum(total_amount) as total from orders"}]}',
                "<html>sum report</html>",
            ]
        )
        controller = DataController(DataWorkflow(client, make_db()))
        self.assertIn("plan", controller.stream("count orders").lower())
        self.assertEqual(controller.stream_continue("sum instead"), "<html>sum report</html>")

    def test_report_generator_receives_plan_and_results(self):
        plan = Plan([Step(1, "count", "select count(*) from orders")])
        state = {"input": "count", "plannerResult": plan, "planExecuteResult": {0: object()}}
        result = ReportGeneratorNode(FakeClient(["<html>ok</html>"])).apply(state)
        self.assertEqual(result["reportGeneratorResult"], "<html>ok</html>")


if __name__ == "__main__":
    unittest.main()
