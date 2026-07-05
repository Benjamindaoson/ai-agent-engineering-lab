# python-agentscope-a2a-demo

A Python teaching project for AgentScope-style A2A: agent cards, service discovery, remote streaming events, and client calls.

## Run order for class

```powershell
cd python-agentscope-a2a-demo
python -m unittest discover -s tests -v
python -m python_agentscope_a2a_demo.self_check
python -m python_agentscope_a2a_demo.offline_demo
python -m python_agentscope_a2a_demo
```

All commands are offline. Nacos, AgentScope A2A starter, Spring Boot, and DashScope are represented by a stdlib in-memory registry and deterministic stream events.

## Class storyline

1. Server creates `my-assistant`.
2. Server publishes an agent card with `getWeather` and `generate`.
3. Client resolves the card through a Nacos-like registry.
4. Client streams task events from the remote agent.
