## Why

`agentscope-a2a-demo` shows AgentScope A2A discovery and streaming calls: a server publishes `my-assistant` with tool skills, and a client resolves the agent card through Nacos before streaming a message.

## What Changes

- Add `python-agentscope-a2a-demo/` without modifying `agentscope-a2a-demo/`.
- Mirror the Java server, client, weather tool, and application config with stdlib Python.
- Replace live Nacos with an in-memory registry for offline classroom runs.
- Include tests, `self_check`, `offline_demo`, README, and `requirements.txt`.

## Impact

- New Python module under `python-agentscope-a2a-demo/`.
- New OpenSpec change under `openspec/changes/add-python-agentscope-a2a-demo/`.
