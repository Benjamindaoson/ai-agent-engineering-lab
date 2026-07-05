from pathlib import Path

from .file_tool import FileTool
from .model_config import ModelConfig
from .openai_client import OpenAIClient
from .planner_agent_service import PlannerAgentService
from .react_agent import ReactAgent
from .zhouyu_agent_hook import ZhouyuAgentHook


WORKSPACE = Path("zhouyu-code")


ARCHITECT_PROMPT = """You are a senior architect. Design architecture only.
Workspace: {workspace}
Write the architecture plan into the workspace. Use one tool call at a time.
"""

BACKEND_PROMPT = """You are a senior backend engineer. Implement backend code from the architecture plan.
Workspace: {workspace}
Only write backend code. Use one tool call at a time.
"""

FRONTEND_PROMPT = """You are a senior frontend engineer. Implement frontend code from the architecture plan.
Workspace: {workspace}
Only write frontend code. Use one tool call at a time.
"""

REVIEW_PROMPT = """You are a senior code review engineer.
Review backend code only and save a review report into the workspace. Use one tool call at a time.
"""

PLANNER_PROMPT = """You are a senior system planner.
Generate a JSON object with this shape:
{"steps":[{"stepNum":"1","agentName":"architectAgent","prompt":"..." }]}
Available agents: architectAgent, backendAgent, frontendAgent, reviewAgent.
Do not wrap the result in markdown fences.
"""


def build_service(model=None, workspace: Path = WORKSPACE) -> PlannerAgentService:
    workspace.mkdir(parents=True, exist_ok=True)
    model = model or OpenAIClient(ModelConfig.from_env())
    file_tool = FileTool()
    hooks = [ZhouyuAgentHook()]
    agents = {
        "architectAgent": ReactAgent(
            "architectAgent", model, file_tool, ARCHITECT_PROMPT.replace("{workspace}", str(workspace)), hooks
        ),
        "backendAgent": ReactAgent("backendAgent", model, file_tool, BACKEND_PROMPT.replace("{workspace}", str(workspace)), hooks),
        "frontendAgent": ReactAgent(
            "frontendAgent", model, file_tool, FRONTEND_PROMPT.replace("{workspace}", str(workspace)), hooks
        ),
        "reviewAgent": ReactAgent("reviewAgent", model, file_tool, REVIEW_PROMPT.replace("{workspace}", str(workspace)), hooks),
    }
    planner_agent = ReactAgent("plannerAgent", model, None, PLANNER_PROMPT)
    return PlannerAgentService(planner_agent, agents)


def main() -> None:
    service = build_service()
    plan = service.plan("Build the simplest login feature using Python and Vue.js. Ignore security.")
    print(plan.to_json())
    print(service.execute(plan))


if __name__ == "__main__":
    main()
