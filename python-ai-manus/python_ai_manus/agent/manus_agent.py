from pathlib import Path

from python_ai_manus.model import OpenAIClient, RelevanceFilter
from python_ai_manus.tools import ToolCollection
from python_ai_manus.tools.impl import BrowserTool, FileReaderTool, FileWriterTool, SandboxTool, TavilySearchTool

from .tool_call_agent import ToolCallAgent


SYSTEM_PROMPT = """## Role
You are Manus, a general-purpose AI agent that can use tools to complete tasks.

## Rules
- Workspace: {workspace}
- Do not assume the sandbox shares the workspace directory.
- When running code in the sandbox, pass code content directly to the sandbox instead of passing a script file path.
- Use only one tool call at a time.
"""


class ManusAgent(ToolCallAgent):
    def __init__(self, openai_client: OpenAIClient):
        tool_collection = ToolCollection()
        tool_collection.add_tool(FileWriterTool())
        tool_collection.add_tool(FileReaderTool())
        tool_collection.add_tool(SandboxTool())
        tool_collection.add_tool(TavilySearchTool())
        tool_collection.add_tool(BrowserTool())

        workspace_root = self.get_project_root() / "workspace"
        workspace_root.mkdir(parents=True, exist_ok=True)
        super().__init__(openai_client, tool_collection, SYSTEM_PROMPT.replace("{workspace}", str(workspace_root)))

    def get_project_root(self) -> Path:
        current = Path.cwd().resolve()
        while current != current.parent:
            if (current / "pom.xml").exists():
                return current
            current = current.parent
        return Path.cwd().resolve()

    def set_relevance_filter(self, relevance_filter: RelevanceFilter) -> None:
        self.memory.relevance_filter = relevance_filter
        self.tool_collection.relevance_filter = relevance_filter
