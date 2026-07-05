## Why

`spring-ai-alibaba-agent-framework-demo` is the course step for Alibaba Agent Framework concepts: ReactAgent wiring, memory checkpoints, hooks, interceptors, human approval, store access, agent flows, agent-as-tool, and RAG tools.

## What Changes

- Add `python-ai-alibaba-agent-framework-demo/` without modifying the Java module.
- Mirror Java files and packages with Python counterparts for application wiring, controller endpoints, tools, hooks, interceptors, and custom flow agent.
- Keep the module offline-first with stdlib in-memory implementations.
- Keep OpenAI-compatible provider configuration for DashScope and DeepSeek.

## Impact

- New Python module under `python-ai-alibaba-agent-framework-demo/`.
- New OpenSpec change under `openspec/changes/add-python-ai-alibaba-agent-framework-demo/`.
