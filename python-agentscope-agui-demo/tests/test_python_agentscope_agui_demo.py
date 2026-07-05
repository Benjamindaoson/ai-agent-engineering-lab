import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from python_agentscope_agui_demo.agui_application import AguiApplication, create_application
from python_agentscope_agui_demo.agui_protocol import parse_sse_events


class PythonAgentScopeAguiDemoTests(unittest.TestCase):
    def test_run_endpoint_streams_agui_text_events(self):
        app = create_application()
        payload = {
            "threadId": "thread-1",
            "runId": "run-1",
            "messages": [{"id": "msg-1", "role": "user", "content": "你好"}],
        }

        body, headers = app.handle_run(payload)
        events = parse_sse_events(body.decode("utf-8"))

        self.assertEqual(headers["Content-Type"], "text/event-stream; charset=utf-8")
        self.assertEqual([event["type"] for event in events], [
            "RUN_STARTED",
            "TEXT_MESSAGE_START",
            "TEXT_MESSAGE_CONTENT",
            "TEXT_MESSAGE_END",
            "RUN_FINISHED",
        ])
        self.assertEqual(events[0]["threadId"], "thread-1")
        self.assertEqual(events[0]["runId"], "run-1")
        self.assertIn("Assistant", events[2]["delta"])

    def test_server_side_memory_keeps_thread_history(self):
        app = create_application()
        app.handle_run({"threadId": "same-thread", "runId": "run-1", "messages": [{"role": "user", "content": "第一句"}]})
        app.handle_run({"threadId": "same-thread", "runId": "run-2", "messages": [{"role": "user", "content": "第二句"}]})

        self.assertEqual([msg["content"] for msg in app.memory["same-thread"]], ["第一句", "第二句"])

    def test_static_resources_match_java_demo_entrypoints(self):
        app = AguiApplication()

        html, html_headers = app.static_response("/")
        js, js_headers = app.static_response("/js/agui-client.js")

        self.assertEqual(html_headers["Content-Type"], "text/html; charset=utf-8")
        self.assertIn("AgentScope AG-UI Demo", html.decode("utf-8"))
        self.assertEqual(js_headers["Content-Type"], "application/javascript; charset=utf-8")
        self.assertIn("class AguiClient", js.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
