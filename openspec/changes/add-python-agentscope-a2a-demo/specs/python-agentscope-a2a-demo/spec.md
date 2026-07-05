## ADDED Requirements

### Requirement: Python module mirrors AgentScope A2A demo
The system SHALL add `python-agentscope-a2a-demo/` with Python counterparts for `A2AServerSpringBootApplication.java`, `A2AClientApplication.java`, `WeatherService.java`, and `application.yml`.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-agentscope-a2a-demo/`
- **THEN** they can map Python files to the Java A2A demo files.

### Requirement: Server publishes an agent card
The module SHALL register `my-assistant` with skills `getWeather` and `generate`.

#### Scenario: Client resolves the card
- **WHEN** the client asks the registry for `my-assistant`
- **THEN** the returned card includes both skill definitions.

### Requirement: Client streams A2A task events
The module SHALL stream task started, message, and task finished events for weather and data-generation requests.

#### Scenario: Weather request streams a response
- **WHEN** the client sends `上海什么天气`
- **THEN** a message event contains `上海 的天气：晴天，25°C`.
