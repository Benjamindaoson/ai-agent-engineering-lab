## Design

`python-a2a-demo` combines both Java modules:

- `common.py`: `AgentCard`, `AgentRegistry`, `ReactAgent`, `A2aRemoteAgent`, and `SequentialAgent`.
- `server/zhouyu_tools.py`: weather tool.
- `server/a2a_server_application.py`: registers `weatherAgent` and `weatherAgent1` with agent cards.
- `client/agent_config.py`: builds a remote weather agent and sequential agent.
- `client/client_controller.py`: exposes `hello(input)` equivalent to Java `/hello`.

The in-memory registry replaces Nacos and HTTP transport. This keeps the protocol roles visible without requiring external services.

## Verification

Tests cover server tool behavior, agent-card registration, remote invocation, sequential invocation, controller output, and missing-agent errors.
