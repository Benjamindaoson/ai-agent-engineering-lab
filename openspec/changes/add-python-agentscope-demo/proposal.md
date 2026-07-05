## Why

`agentscope-demo` is the broad AgentScope capability showcase in the Java course. It demonstrates basic agents, tools, tool groups, preset parameters, injected context, hooks, human confirmation, memory, sessions, pipelines, multi-agent discussion, structured output, skills, RAG, MCP, vision, image generation, and Studio.

## What Changes

- Add `python-agentscope-demo/` without modifying `agentscope-demo/`.
- Provide Python modules with names matching the Java demo classes closely enough for side-by-side teaching.
- Implement an offline-first mini AgentScope teaching layer using the standard library, with OpenAI-compatible model configuration reserved for live expansion.
- Include tests, `self_check`, `offline_demo`, README run order, and `requirements.txt`.

## Impact

- New Python module under `python-agentscope-demo/`.
- New OpenSpec change under `openspec/changes/add-python-agentscope-demo/`.
