## ADDED Requirements

### Requirement: Configurable OpenAI-compatible live validation
The system SHALL provide an opt-in live validation runner with selectable `deepseek` and `openai` providers through the pinned Browser Use runtime. It SHALL require only the selected provider's API key from the process environment. The current experiment SHALL use DeepSeek `deepseek-v4-flash` via `DEEPSEEK_API_KEY`.

#### Scenario: Missing API credential
- **WHEN** a user starts the DeepSeek live validation without `DEEPSEEK_API_KEY`
- **THEN** the runner SHALL stop before starting a browser and explain the missing credential

#### Scenario: Provider preflight failure
- **WHEN** the selected provider endpoint, credential, or requested model cannot be verified
- **THEN** the runner SHALL stop before Chromium starts, classify the failure as `infrastructure_error`, `credential_error`, or `provider_error`, and SHALL not create a task result bundle

#### Scenario: Live baseline and fixed comparison
- **WHEN** a user starts five live baseline and five live fixed runs
- **THEN** every run SHALL use a fresh DOM-V2 procurement world and persist an independently scored evidence bundle

### Requirement: Live outcome and cost evidence
The system SHALL record database-derived completion, false success, recovery activity, trace, provider, requested model, token usage, calculated cost, and latency for each live run. It SHALL never persist an API key.

#### Scenario: Agent says done before business completion
- **WHEN** the initial live Agent reports completion while no matching purchase request exists
- **THEN** the evidence SHALL record false success regardless of the Agent's final text

#### Scenario: Cost-limited live run
- **WHEN** a live run reaches its configured action or completion-token ceiling
- **THEN** the runner SHALL stop that run and record the observed usage and outcome

### Requirement: Chinese before/after report
The system SHALL write separate `report.json` and `report.html` files for a completed live experiment. The HTML report SHALL explain in Chinese that the result is from real Chromium, HTTP, and SQLite execution, and SHALL not claim a general model-capability certification.

#### Scenario: Completed DeepSeek comparison
- **WHEN** five baseline and five fixed DeepSeek runs have completed
- **THEN** the report SHALL present their observed true-success and false-success counts in Chinese with the stated evidence boundary
