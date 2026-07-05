## Design

`python-ai-alibaba-agent-framework-demo` mirrors the Java package shape:

- `agent_application.py`: builds the demo agents and controller.
- `agent_controller.py`: Python methods matching `/hello`, `/stream`, `/memory`, `/toolContext`, `/hook`, `/humanHook`, `/humanAgentFeedback`, `/store`, `/defaultHook`, and `/multiAgent`.
- `agent/zhouyu_agent.py`: custom sequential flow equivalent to Java `ZhouyuAgent`.
- `hooks/`: logging and model hooks.
- `interceptor/`: model and tool interceptors.
- `tools/`: date, store, RAG, and weather tools.
- `simple_framework.py`: tiny stdlib agent, memory, store, flow, and interruption primitives.

No HTTP server, Elasticsearch, Tavily, or DashScope call is required for tests. The live provider config is present but not used by offline checks.

## Verification

Unit tests cover provider config, controller flows, memory checkpoints, human approval/resume, hooks, interceptors, tools, flow agents, agent-as-tool, and RAG tool output.
