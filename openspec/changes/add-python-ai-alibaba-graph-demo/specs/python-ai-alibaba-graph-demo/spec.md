## ADDED Requirements

### Requirement: Python module mirrors Java Graph Demo structure
The system SHALL add `python-ai-alibaba-graph-demo/` with Python counterparts for Java application, graph config, controller, observation config, title/content node actions, and interruptable node action.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-ai-alibaba-graph-demo/python_ai_alibaba_graph_demo/`
- **THEN** they can find Python files corresponding to Java files in `spring-ai-alibaba-graph-demo/src/main/java/com/zhouyu/`.

### Requirement: Graph orchestration capabilities are preserved
The module SHALL demonstrate simple sequential graph execution, stream output, conditional routing, thread/checkpoint memory, interrupt-before-node, interruptable node, parallel branch merge, subgraph merge, and observation configuration.

#### Scenario: Controller flows run offline
- **WHEN** the Python controller is created with in-memory dependencies
- **THEN** simple, stream, conditional, thread, memory saver, interrupt/resume, parallel, and subgraph methods return deterministic classroom outputs.

### Requirement: Offline verification works without external services
The module SHALL include tests, a self-check, and an offline demo that do not require DashScope, Spring Boot, Reactor, Micrometer, OpenTelemetry, or Alibaba graph runtime.

#### Scenario: Offline demo runs
- **WHEN** the user runs `python -m python_ai_alibaba_graph_demo.offline_demo`
- **THEN** key graph flows are demonstrated without external credentials.
