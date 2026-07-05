import json
import os
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class PythonReactAgentTests(unittest.TestCase):
    def test_deepseek_config_reads_provider_env(self):
        from python_react_agent.model_config import ModelConfig

        env = {
            "PROVIDER": "deepseek",
            "DEEPSEEK_API_KEY": "sk-test",
        }

        config = ModelConfig.from_env(env)

        self.assertEqual(config.api_key, "sk-test")
        self.assertEqual(config.base_url, "https://api.deepseek.com")

    def test_tool_description_uses_decorator_metadata(self):
        from python_react_agent.agent_tools import AgentTools
        from python_react_agent.tool_util import ToolUtil

        description = ToolUtil.get_tool_description(AgentTools)

        self.assertIn("toolName=write_file", description)
        self.assertIn("file_path", description)
        self.assertIn("content", description)

    def test_parser_accepts_fenced_json_action_input(self):
        from python_react_agent.react_agent import ReActAgent

        parsed = ReActAgent.parse_llm_output(
            'Reason: need a file\nAction: write_file\nActionInput: ```json\n{"file_path":"a.txt","content":"hi"}\n```'
        )

        self.assertEqual(parsed.type, "action")
        self.assertEqual(parsed.reason, "need a file")
        self.assertEqual(parsed.action, "write_file")
        self.assertEqual(json.loads(parsed.action_input_str)["content"], "hi")

    def test_parser_returns_final_answer(self):
        from python_react_agent.react_agent import ReActAgent

        parsed = ReActAgent.parse_llm_output("Reason: enough\nFinalAnswer: done")

        self.assertEqual(parsed.type, "final_answer")
        self.assertEqual(parsed.answer, "done")

    def test_write_file_tool_writes_content(self):
        from python_react_agent.agent_tools import AgentTools

        with tempfile.TemporaryDirectory() as temp_dir:
            path = pathlib.Path(temp_dir) / "out.txt"
            result = AgentTools().write_file(
                json.dumps({"file_path": str(path), "content": "hello"}, ensure_ascii=False)
            )

            self.assertEqual(result, "写入成功")
            self.assertEqual(path.read_text(encoding="utf-8"), "hello")

    def test_offline_demo_runs_full_agent_flow(self):
        from python_react_agent.offline_demo import run_demo

        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_demo(pathlib.Path(temp_dir))

            self.assertEqual(result, "离线演示完成")
            self.assertEqual((pathlib.Path(temp_dir) / "demo.txt").read_text(encoding="utf-8"), "hello offline demo")


if __name__ == "__main__":
    unittest.main()
