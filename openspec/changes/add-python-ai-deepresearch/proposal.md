## Why

`ai-deepresearch` is the next course module after `ai-engineer`: it turns multi-agent orchestration into a research workflow with coordinator, planner, parallel researchers, and reporter.

## What Changes

- Add `python-ai-deepresearch/` without modifying `ai-deepresearch/`.
- Mirror the Java DTO, node, util, application, controller, observation, and parallel streaming example files.
- Keep provider config OpenAI-compatible and keep offline tests/demos credential-free.
- Implement Tavily as an optional tool so the module can run offline and report missing key clearly.

## Impact

- New Python module under `python-ai-deepresearch/`.
- New OpenSpec change under `openspec/changes/add-python-ai-deepresearch/`.
