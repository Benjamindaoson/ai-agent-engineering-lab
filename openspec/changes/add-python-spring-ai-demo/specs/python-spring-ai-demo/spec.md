## ADDED Requirements

### Requirement: Python module mirrors Java spring-ai-demo structure
The system SHALL add `python-spring-ai-demo/` with Python counterparts for the Java request object, utility, tools, controllers, and application wiring.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-spring-ai-demo/python_spring_ai_demo/`
- **THEN** they can find Python files corresponding to Java files in `spring-ai-demo/src/main/java/com/zhouyu/`.

### Requirement: Spring AI capability demos are preserved
The module SHALL demonstrate chat, stream/SSE, system prompts, memory, advisors, structured output, embeddings, vector store search, RAG, evaluation, tool calling, MCP prompt/resource access, and metrics.

#### Scenario: RAG flow runs
- **WHEN** documents are stored and a question is searched
- **THEN** the controller retrieves matching documents and sends them to the chat client as context.

#### Scenario: Tool flow runs
- **WHEN** tool controller methods are called
- **THEN** local tool callbacks can be executed automatically or in user-controlled style.

#### Scenario: MCP flow runs offline
- **WHEN** MCP controller methods are called with fake MCP clients
- **THEN** prompt and resource values are returned without requiring a live MCP server.

### Requirement: Offline verification works without external services
The module SHALL include tests, a self-check, and an offline demo that do not require model credentials, MySQL, Elasticsearch, Micrometer, or MCP servers.

#### Scenario: Offline demo runs
- **WHEN** the user runs `python -m python_spring_ai_demo.offline_demo`
- **THEN** chat, RAG, tool, and MCP examples are demonstrated.
