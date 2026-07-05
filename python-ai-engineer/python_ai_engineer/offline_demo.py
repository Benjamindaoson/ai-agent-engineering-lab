import json
from pathlib import Path

from .engineer_application import build_service


class FakeEngineerModel:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.calls = 0

    def chat(self, messages, tools=None):
        self.calls += 1
        system = messages[0]["content"] if messages and messages[0]["role"] == "system" else ""
        if "senior system planner" in system:
            return {
                "content": json.dumps(
                    {
                        "steps": [
                            {"stepNum": "1", "agentName": "architectAgent", "prompt": "write architecture plan"},
                            {"stepNum": "2", "agentName": "backendAgent", "prompt": "write backend code"},
                            {"stepNum": "3", "agentName": "frontendAgent", "prompt": "write frontend code"},
                            {"stepNum": "4", "agentName": "reviewAgent", "prompt": "write review report"},
                        ]
                    },
                    ensure_ascii=False,
                ),
                "tool_calls": [],
                "finish_reason": "stop",
            }
        if "senior architect" in system:
            return self._write_once("architecture.md", "# Architecture\n\nLogin demo with frontend and backend.")
        if "senior backend" in system:
            return self._write_once("backend/app.py", "def login(username, password):\n    return username == 'demo'\n")
        if "senior frontend" in system:
            return self._write_once("frontend/index.html", "<button>Login</button>\n")
        if "senior code review" in system:
            return self._write_once("review.md", "# Review\n\nBackend demo code is intentionally minimal.\n")
        return {"content": "done", "tool_calls": [], "finish_reason": "stop"}

    def _write_once(self, relative_path: str, content: str):
        return {
            "content": "writing file",
            "tool_calls": [
                {
                    "id": f"call_{self.calls}",
                    "function": {
                        "name": "write_file",
                        "arguments": json.dumps(
                            {"file_path": str(self.workspace / relative_path), "content": content},
                            ensure_ascii=False,
                        ),
                    },
                }
            ],
            "finish_reason": "tool_calls",
        }


class FakeFinishingModel(FakeEngineerModel):
    def chat(self, messages, tools=None):
        if messages and messages[-1].get("role") == "tool":
            return {"content": "done", "tool_calls": [], "finish_reason": "stop"}
        return super().chat(messages, tools)


def main() -> None:
    workspace = Path("output") / "zhouyu-code"
    service = build_service(FakeFinishingModel(workspace), workspace)
    plan = service.plan("Build a login demo")
    print(plan.to_json())
    print(service.execute(plan))
    print(f"Artifacts written to: {workspace}")


if __name__ == "__main__":
    main()
