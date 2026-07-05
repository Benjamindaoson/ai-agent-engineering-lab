import json
import tempfile
from pathlib import Path

from python_ai_manus.agent import ManusAgent
from python_ai_manus.model import Message, ModelConfig, ModelResponse
from python_ai_manus.tools.impl import FileReaderTool, FileWriterTool, SandboxTool


class FakeOpenAIClient:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.calls = 0

    def chat(self, messages, tools=None):
        self.calls += 1
        if self.calls == 1:
            return ModelResponse(
                "write check file",
                [
                    {
                        "id": "call_self_check",
                        "type": "function",
                        "function": {
                            "name": "write_file",
                            "arguments": json.dumps({"file_path": str(self.file_path), "content": "ok"}),
                        },
                    }
                ],
                "tool_calls",
            )
        return ModelResponse("done", [], "stop")


def main() -> None:
    dashscope = ModelConfig(model="qwen-plus", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", api_key="x")
    assert dashscope.model == "qwen-plus"

    message = Message.user_message("hello")
    assert message.to_dict() == {"role": "user", "content": "hello"}

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "check.txt"
        writer = FileWriterTool()
        reader = FileReaderTool()
        assert writer.execute({"file_path": str(file_path), "content": "abc"}).is_success()
        assert reader.execute({"file_path": str(file_path)}).output == "abc"

        agent_path = Path(temp_dir) / "agent.txt"
        agent = ManusAgent(FakeOpenAIClient(agent_path))
        result = agent.run("write a file")
        assert "write_file" in result
        assert agent_path.read_text(encoding="utf-8") == "ok"

    command = SandboxTool().build_code_execution_command("print('x')", "python")
    assert "python3 << '" in command
    print("python-ai-manus self-check passed")


if __name__ == "__main__":
    main()
