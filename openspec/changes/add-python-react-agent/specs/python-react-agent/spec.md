## ADDED Requirements

### Requirement: Python module mirrors Java ReAct module structure
The system SHALL add a `python-react-agent/` module whose source files correspond to the Java files in `java-react-agent/src/main/java/com/zhouyu/`.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-react-agent/python_react_agent/`
- **THEN** they can find Python counterparts for `AgentTools`, `ModelConfig`, `ReActAgent`, `Tool`, `ToolParam`, and `ToolUtil`

### Requirement: Provider configuration supports DashScope and DeepSeek
The system SHALL support OpenAI-compatible DashScope and DeepSeek chat completion settings from environment variables.

#### Scenario: DashScope provider is selected
- **WHEN** `PROVIDER=dashscope` and `DASHSCOPE_API_KEY` is set
- **THEN** the Python agent uses DashScope base URL `https://dashscope.aliyuncs.com/compatible-mode/v1`

#### Scenario: DeepSeek provider is selected
- **WHEN** `PROVIDER=deepseek` and `DEEPSEEK_API_KEY` is set
- **THEN** the Python agent uses DeepSeek base URL `https://api.deepseek.com`

### Requirement: ReAct loop matches Java behavior
The system SHALL implement the Java module's ReAct loop using prompt construction, one model call per iteration, parsed `Reason`, `Action`, `ActionInput`, tool execution, observation history, and final answer handling.

#### Scenario: Final answer ends the loop
- **WHEN** the model output contains `FinalAnswer: done`
- **THEN** the agent returns `done` without executing a tool

#### Scenario: Action output executes a tool
- **WHEN** the model output contains `Reason`, `Action`, and `ActionInput`
- **THEN** the agent parses the tool call and passes `ActionInput` to the named tool

### Requirement: Local verification does not require model credentials
The system SHALL include a local self-check command that verifies parser and tool metadata behavior without calling a remote model.

#### Scenario: Self-check runs offline
- **WHEN** the user runs the documented self-check command without API keys
- **THEN** parser and tool metadata checks pass locally
