## ADDED Requirements

### Requirement: Python module mirrors JavaClaw platform structure
The system SHALL add `python-claw/` with Python counterparts for JavaClaw application, properties, core agent, Feishu receiver, Feishu tools, WebSocket handler/config, memory service, session startup, skill loader, and update-memory tool.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-claw/python_claw/`
- **THEN** they can find Python modules corresponding to the Java files in `java-claw/src/main/java/com/zhouyu/`.

### Requirement: Platform behaviors are preserved offline
The module SHALL demonstrate workspace initialization, template copying, skill loading, main/Feishu sessions, daily notes, long-term memory, `/new` reset, web chat JSON protocol, Feishu text parsing, event-id deduplication, private/group reply selection, and local tools.

#### Scenario: Offline platform flow runs
- **WHEN** `create_application()` is called
- **THEN** a workspace is initialized and both main and Feishu sessions can respond without external services.

### Requirement: Offline verification works without live services
The module SHALL include tests, a self-check, and an offline demo that do not require Spring Boot, AgentScope, Feishu SDK, DashScope credentials, WebSocket server startup, or shell command execution.

#### Scenario: Offline demo runs
- **WHEN** the user runs `python -m python_claw.offline_demo`
- **THEN** workspace, memory, web-chat, Feishu routing, and tool examples are demonstrated.
