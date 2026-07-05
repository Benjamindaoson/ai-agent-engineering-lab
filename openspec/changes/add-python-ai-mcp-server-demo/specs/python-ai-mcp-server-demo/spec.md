## ADDED Requirements

### Requirement: Python module mirrors Java MCP server demo
The system SHALL add `python-ai-mcp-server-demo/` with Python counterparts for `WeatherService` and `McpServerApplication`.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-ai-mcp-server-demo/python_ai_mcp_server_demo/`
- **THEN** they can find Python files corresponding to Java files in `spring-ai-mcp-server-demo/src/main/java/com/zhouyu/`.

### Requirement: MCP server capabilities are preserved
The module SHALL expose the Java demo's weather tool, greeting prompt, and configuration resource.

#### Scenario: Weather tool is called
- **WHEN** `getWeather` is called with `上海`
- **THEN** the result is `天晴`.

#### Scenario: Greeting prompt is requested
- **WHEN** prompt `greeting` is requested with a name
- **THEN** the result contains the assistant greeting message.

#### Scenario: Configuration resource is read
- **WHEN** resource `config://username` is read
- **THEN** the configured value is returned, or `123` is returned for missing keys.

### Requirement: Offline verification works without a live MCP runtime
The module SHALL include tests, a self-check, and an offline demo that use stdlib-only dispatch.

#### Scenario: Offline demo runs
- **WHEN** the user runs `python -m python_ai_mcp_server_demo.offline_demo`
- **THEN** tools, prompts, resources, and JSON-style call dispatch are demonstrated.
