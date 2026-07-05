## ADDED Requirements

### Requirement: Python module mirrors Java ai-manus structure
The system SHALL add `python-ai-manus/` with Python counterparts for the Java `agent`, `model`, `tools`, and `tools.impl` packages.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-ai-manus/python_ai_manus/`
- **THEN** they can find Python files corresponding to `BaseAgent`, `ToolCallAgent`, `ManusAgent`, model classes, tool abstractions, and implementation tools from `ai-manus`.

### Requirement: OpenAI-compatible tool-call client
The system SHALL provide an OpenAI-compatible chat client that sends messages and tool definitions and returns content, tool calls, and finish reason.

#### Scenario: DeepSeek provider is selected
- **WHEN** `PROVIDER=deepseek` and `DEEPSEEK_API_KEY` are set
- **THEN** the model client uses DeepSeek's OpenAI-compatible endpoint.

#### Scenario: DashScope provider is selected
- **WHEN** `PROVIDER=dashscope` and `DASHSCOPE_API_KEY` are set
- **THEN** the model client uses DashScope's OpenAI-compatible endpoint.

### Requirement: Manus agent includes original tool families
The Python Manus agent SHALL include file writing, file reading, Docker sandbox execution, Tavily search, and browser actions.

#### Scenario: Manus agent is created
- **WHEN** `ManusAgent` is instantiated
- **THEN** its tool collection contains `write_file`, `read_file`, `sandbox`, `tavily_search`, and `browser`.

### Requirement: Offline verification works without model credentials
The module SHALL include tests and demos that validate core behavior without calling a remote model.

#### Scenario: Offline demo executes a tool call
- **WHEN** the offline demo runs
- **THEN** a fake model response triggers a real local tool execution and then returns a final answer.

### Requirement: External tool smoke checks are explicit
The module SHALL include a command that checks Tavily, Docker sandbox, and browser behavior separately from offline unit tests.

#### Scenario: External smoke check runs
- **WHEN** the user runs `python -m python_ai_manus.external_smoke_check`
- **THEN** the command reports PASS, SKIP, or FAIL for `tavily_search`, `sandbox`, and `browser`.
