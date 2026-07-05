## Why

`ai-engineer` is the next course step after `ai-manus`: it moves from one tool-using Manus-style agent to a small software-engineering team with a planner and multiple specialist agents.

## What Changes

- Add `python-ai-engineer/` without modifying `ai-engineer/`.
- Keep Python files close to Java class names for side-by-side teaching.
- Implement `FileTool`, `Plan`, `Step`, `PlannerAgentService`, `ZhouyuAgentHook`, role agents, offline demo, and tests.
- Use an OpenAI-compatible provider only for live runs; tests and offline demo use fake agents/models.

## Impact

- New Python module under `python-ai-engineer/`.
- New OpenSpec change under `openspec/changes/add-python-ai-engineer/`.
