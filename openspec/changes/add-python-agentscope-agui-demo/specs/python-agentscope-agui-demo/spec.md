## ADDED Requirements

### Requirement: Python module mirrors AG-UI Spring demo
The system SHALL add `python-agentscope-agui-demo/` with a Python application corresponding to `AguiApplication.java`, `application.yml`, `index.html`, and `agui-client.js`.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-agentscope-agui-demo/`
- **THEN** they can map the Python files to the Java AG-UI demo files.

### Requirement: AG-UI run endpoint streams events
The module SHALL provide an `/agui/run` handler that returns AG-UI-style server-sent events for run started, text message start, text content, text message end, and run finished.

#### Scenario: Browser client receives a response
- **WHEN** a POST body contains `threadId`, `runId`, and user messages
- **THEN** the response is `text/event-stream` and contains ordered AG-UI events.

### Requirement: Server-side memory is preserved per thread
The module SHALL keep per-thread user message history during the server process, matching the Java config `server-side-memory: true`.

#### Scenario: Same thread sends two messages
- **WHEN** two runs use the same `threadId`
- **THEN** both user messages are retained in that thread history.
