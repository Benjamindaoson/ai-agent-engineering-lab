## Why

`agentscope-agui-demo` shows how an AgentScope agent is exposed to a browser through the AG-UI protocol.

## What Changes

- Add `python-agentscope-agui-demo/` without modifying `agentscope-agui-demo/`.
- Mirror the Java Spring Boot app with a stdlib Python HTTP server.
- Provide `/agui/run` as a server-sent-events endpoint and serve the static AG-UI demo page.
- Keep live model configuration optional and OpenAI-compatible.

## Impact

- New Python module under `python-agentscope-agui-demo/`.
- New OpenSpec change under `openspec/changes/add-python-agentscope-agui-demo/`.
