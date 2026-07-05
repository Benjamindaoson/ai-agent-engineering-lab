import json
from pathlib import Path

from python_ai_manus.agent import ManusAgent
from python_ai_manus.model import ModelResponse


class FakeOpenAIClient:
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.calls = 0

    def chat(self, messages, tools=None):
        self.calls += 1
        if self.calls == 1:
            return ModelResponse(
                content="Need to create a demo file first.",
                tool_calls=[
                    {
                        "id": "call_write_demo",
                        "type": "function",
                        "function": {
                            "name": "write_file",
                            "arguments": json.dumps(
                                {
                                    "file_path": str(self.output_path),
                                    "content": "hello ai-manus offline demo",
                                }
                            ),
                        },
                    }
                ],
                finish_reason="tool_calls",
            )
        return ModelResponse("Offline Manus demo complete.", [], "stop")


def main() -> None:
    output_path = Path("output") / "ai_manus_demo.txt"
    agent = ManusAgent(FakeOpenAIClient(output_path))
    print(agent.run("Create a demo file."))


if __name__ == "__main__":
    main()
