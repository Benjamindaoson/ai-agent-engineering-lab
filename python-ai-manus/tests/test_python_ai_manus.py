import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from python_ai_manus.agent import ManusAgent, ToolCallAgent
from python_ai_manus.external_smoke_check import _line
from python_ai_manus.model import Message, ModelConfig, ModelResponse
from python_ai_manus.tools import ToolCollection
from python_ai_manus.tools.impl import FileReaderTool, FileWriterTool, SandboxTool, TavilySearchTool
from python_ai_manus.tools.impl.docker_sandbox import DockerSandbox


class FakeClient:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.calls = 0

    def chat(self, messages, tools=None):
        self.calls += 1
        if self.calls == 1:
            return ModelResponse(
                content="need tool",
                tool_calls=[
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "write_file",
                            "arguments": json.dumps({"file_path": str(self.file_path), "content": "hello"}),
                        },
                    }
                ],
                finish_reason="tool_calls",
            )
        return ModelResponse("done", [], "stop")


class PythonAiManusTest(unittest.TestCase):
    def test_model_config_from_env_values(self):
        config = ModelConfig("m", "https://example.test", "k")
        self.assertEqual(config.model, "m")
        self.assertEqual(config.base_url, "https://example.test")

    def test_message_serialization(self):
        self.assertEqual(Message.system_message("s").to_dict(), {"role": "system", "content": "s"})

    def test_file_tools(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "a" / "demo.txt"
            write_result = FileWriterTool().execute({"file_path": str(file_path), "content": "hello"})
            self.assertTrue(write_result.is_success())
            read_result = FileReaderTool().execute({"file_path": str(file_path)})
            self.assertEqual(read_result.output, "hello")

    def test_tool_call_agent_executes_tool_and_finishes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "agent.txt"
            tools = ToolCollection()
            tools.add_tool(FileWriterTool())
            agent = ToolCallAgent(FakeClient(file_path), tools, "system")
            result = agent.run("write")
            self.assertIn("write_file", result)
            self.assertIn("complete", result)
            self.assertEqual(file_path.read_text(encoding="utf-8"), "hello")

    def test_manus_agent_has_original_tools(self):
        agent = ManusAgent(FakeClient(Path("unused.txt")))
        self.assertEqual(
            set(agent.tool_collection.tools),
            {"write_file", "read_file", "sandbox", "tavily_search", "browser"},
        )

    def test_tavily_without_key_returns_tool_error(self):
        result = TavilySearchTool().execute({"query": "python"})
        self.assertTrue(result.has_error())

    def test_sandbox_code_command_uses_heredoc(self):
        command = SandboxTool().build_code_execution_command("print('hello')", "python")
        self.assertIn("python3 << 'OPENMANUS_CODE_EOF_", command)

    def test_smoke_line_format(self):
        self.assertEqual(_line("browser", "PASS", "ok"), "browser: PASS - ok")

    def test_docker_sandbox_reports_missing_docker_cli(self):
        sandbox = DockerSandbox()
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with self.assertRaisesRegex(RuntimeError, "Docker CLI"):
                sandbox.start()

    def test_docker_sandbox_execute_timeout_returns_result(self):
        sandbox = DockerSandbox()
        sandbox.container_id = "container-1"
        with (
            patch.object(sandbox, "is_running", return_value=True),
            patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["docker"], 1)),
        ):
            result = sandbox.execute_command("python --version")
            self.assertTrue(result.timed_out)
            self.assertEqual(result.exit_code, 124)


if __name__ == "__main__":
    unittest.main()
