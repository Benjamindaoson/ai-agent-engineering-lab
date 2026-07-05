import json

from .deep_research_application import DeepResearchWorkflow


class FakeDeepResearchClient:
    def complete(self, system_prompt: str, user_prompt: str, tools=None) -> str:
        if "coordinator" in system_prompt.lower():
            return "NEED_PLAN"
        if "planner" in system_prompt.lower():
            return json.dumps(
                {
                    "title": "AI Agent Course",
                    "steps": [
                        {"title": "Core loop", "prompt": "Research the ReAct loop"},
                        {"title": "Tool use", "prompt": "Research tool calling and workspace use"},
                        {"title": "Team workflow", "prompt": "Research multi-agent collaboration"},
                    ],
                },
                ensure_ascii=False,
            )
        if "researcher" in system_prompt.lower():
            return f"## Research Note\nFinding for: {user_prompt}\n- Source: offline classroom fixture"
        if "reporter" in system_prompt.lower():
            return "# Final Deep Research Report\n\n## Core Conclusions\n- ReAct explains the loop.\n- Manus adds tools.\n- Engineer adds teams.\n\n## Evidence\n" + user_prompt
        return "done"


def main() -> None:
    workflow = DeepResearchWorkflow(FakeDeepResearchClient(), parallel=False)
    print(workflow.run("How should an AI Agent course be structured?"))


if __name__ == "__main__":
    main()
