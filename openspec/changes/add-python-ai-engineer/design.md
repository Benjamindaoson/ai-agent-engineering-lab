## Design

`python-ai-engineer` mirrors the Java `ai-engineer` module:

- `file_tool.py` maps to `FileTool.java`.
- `plan.py` and `step.py` map to the Java DTOs.
- `zhouyu_agent_hook.py` maps to `ZhouyuAgentHook.java`.
- `planner_agent_service.py` maps to `PlannerAgentService.java`.
- `engineer_application.py` builds `architectAgent`, `backendAgent`, `frontendAgent`, `reviewAgent`, `plannerAgent`, and a sequential agent.

The Python `ReactAgent` is intentionally small: it sends messages to an OpenAI-compatible client, exposes `FileTool` as function tools, executes returned tool calls one at a time, and stops when the model returns final text. This keeps the lesson focused on orchestration rather than framework internals.

## Verification

Tests cover plan parsing, file operations, hook events, planner dispatch, unknown agents, and a fake tool-call loop. Offline demo writes a tiny project plan and generated files without model credentials.
