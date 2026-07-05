## Why

`spring-ai-alibaba-graph-demo` is the course step for graph orchestration: state graphs, node actions, conditional edges, checkpoint memory, human interruption/resume, parallel branches, subgraphs, and graph observation configuration.

## What Changes

- Add `python-ai-alibaba-graph-demo/` without modifying the Java module.
- Mirror Java files with Python counterparts for application, config, controller, observation, blog node actions, and interruptable node action.
- Implement a tiny stdlib graph runner instead of depending on Spring Boot, Reactor, Micrometer, or Alibaba graph runtime.
- Keep OpenAI-compatible provider configuration for DashScope and DeepSeek.

## Impact

- New Python module under `python-ai-alibaba-graph-demo/`.
- New OpenSpec change under `openspec/changes/add-python-ai-alibaba-graph-demo/`.
