## ADDED Requirements

### Requirement: Python module mirrors AgentScope demo concepts
The system SHALL add `python-agentscope-demo/` with Python counterparts for the Java AgentScope demo classes and helper packages.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-agentscope-demo/python_agentscope_demo/`
- **THEN** they can find Python modules corresponding to the Java demo files in `agentscope-demo/src/main/java/com/zhouyu/`.

### Requirement: Core AgentScope behaviors are preserved offline
The module SHALL demonstrate basic agent calls, tools, preset parameters, injected context, tool groups, tool emitters, hooks, human confirmation, short memory sessions, sequential pipelines, fanout pipelines, message hubs, multi-agent debate, structured output, agent skills, RAG, MCP, vision, image generation, and Studio-style conversation.

#### Scenario: Offline demos run without services
- **WHEN** the user runs the offline demo commands
- **THEN** the demonstrations complete without DashScope, AgentScope Java, Mem0, Elasticsearch, MCP server, Studio server, or image model credentials.

### Requirement: Live provider configuration is available but optional
The module SHALL include OpenAI-compatible provider configuration for `PROVIDER=dashscope|deepseek`, reading `DASHSCOPE_API_KEY` or `DEEPSEEK_API_KEY`.

#### Scenario: Missing key is explicit
- **WHEN** live configuration is requested without the required environment key
- **THEN** the module returns a clear error instead of silently falling back to a fake live call.
