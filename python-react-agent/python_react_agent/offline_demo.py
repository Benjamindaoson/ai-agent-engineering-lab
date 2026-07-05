import json
from pathlib import Path

from .model_config import ModelConfig
from .react_agent import ReActAgent


class _FakeCompletions:
    def __init__(self, responses: list[str]):
        self._responses = responses

    def create(self, **_kwargs):
        content = self._responses.pop(0)
        message = type("Message", (), {"content": content})()
        choice = type("Choice", (), {"message": message})()
        return type("Response", (), {"choices": [choice]})()


class _FakeClient:
    def __init__(self, responses: list[str]):
        completions = _FakeCompletions(responses)
        self.chat = type("Chat", (), {"completions": completions})()


def run_demo(output_dir: Path | str = "output") -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    demo_file = output_path / "demo.txt"
    action_input = json.dumps({"file_path": str(demo_file), "content": "hello offline demo"}, ensure_ascii=False)

    fake_client = _FakeClient(
        [
            f"Reason: 需要先写入一个演示文件\nAction: write_file\nActionInput: {action_input}",
            "FinalAnswer: 离线演示完成",
        ]
    )
    config = ModelConfig(
        api_key="offline",
        base_url="https://api.deepseek.com",
        llm_name="offline-demo",
        provider="deepseek",
    )

    return ReActAgent(
        api_client=fake_client,
        config=config,
        model_output_label="Fake model output",
        tool_result_label="Fake tool result",
    ).run("离线演示")


if __name__ == "__main__":
    print(run_demo())
