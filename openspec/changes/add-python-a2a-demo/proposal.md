## Why

`a2a-server-demo` and `a2a-client-demo` are a paired Agent-to-Agent communication lesson. They should become one Python teaching module so server registration and client invocation can be demonstrated together.

## What Changes

- Add `python-a2a-demo/` without modifying the Java `a2a-*` modules.
- Mirror Java server files under `python_a2a_demo/server/`.
- Mirror Java client files under `python_a2a_demo/client/`.
- Replace Nacos/A2A runtime with a stdlib in-memory `AgentRegistry` for offline classroom use.

## Impact

- New Python module under `python-a2a-demo/`.
- New OpenSpec change under `openspec/changes/add-python-a2a-demo/`.
