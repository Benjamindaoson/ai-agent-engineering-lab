# python-a2a-demo

A Python teaching project for Agent-to-Agent collaboration: registry, discovery, remote calls, and ordered composition.

## Run order for class

```powershell
cd python-a2a-demo
python -m unittest discover -s tests -v
python -m python_a2a_demo.self_check
python -m python_a2a_demo.offline_demo
python -m python_a2a_demo
```

The module is stdlib-only. It uses an in-memory `AgentRegistry` so server and client behavior can be demonstrated together without external service discovery.

## Class storyline

1. Server registers `weatherAgent` and `weatherAgent1` with agent cards.
2. Client discovers `weatherAgent` through the registry.
3. `A2aRemoteAgent` invokes the remote weather agent.
4. `SequentialAgent` runs remote weather agent, then a local react-style agent.
5. `ClientController.hello()` returns the final state data.
