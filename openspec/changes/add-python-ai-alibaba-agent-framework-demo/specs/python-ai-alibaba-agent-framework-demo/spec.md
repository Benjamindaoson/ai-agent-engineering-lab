## ADDED Requirements

### Requirement: Python module mirrors Java Agent Framework structure
The system SHALL add `python-ai-alibaba-agent-framework-demo/` with Python counterparts for the Java application, controller, custom agent, hooks, interceptors, and tools.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-ai-alibaba-agent-framework-demo/python_ai_alibaba_agent_framework_demo/`
- **THEN** they can find Python files corresponding to Java files in `spring-ai-alibaba-agent-framework-demo/src/main/java/com/zhouyu/`.

### Requirement: Agent Framework capabilities are preserved
The module SHALL demonstrate React-style agent calls, streaming, memory checkpoints, tool context, hooks, model/tool interceptors, human approval interruption and resume, store access, sequential agents, parallel agents, LLM routing, custom `ZhouyuAgent`, complex workflow, agent-as-tool, and RAG tools.

#### Scenario: Controller flows run offline
- **WHEN** the Python controller is created with in-memory dependencies
- **THEN** hello, stream, memory, hook, human feedback, store, default hook, and multi-agent methods return deterministic classroom outputs.

#### Scenario: Flow agents run offline
- **WHEN** sequential, parallel, routing, custom, complex workflow, tool-agent, and RAG-agent examples are invoked
- **THEN** each returns state data showing the corresponding framework pattern.

### Requirement: Offline verification works without external services
The module SHALL include tests, a self-check, and an offline demo that do not require DashScope, Tavily, Elasticsearch, or Spring Boot.

#### Scenario: Offline demo runs
- **WHEN** the user runs `python -m python_ai_alibaba_agent_framework_demo.offline_demo`
- **THEN** key framework flows are demonstrated without external credentials.
