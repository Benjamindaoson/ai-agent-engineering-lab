## ADDED Requirements

### Requirement: Disclose open-model provenance
Every custom-connector run SHALL be classified as `open` and record only non-secret endpoint hostname, endpoint/model fingerprint, model identifier, protocol family, and cost trust state in the run result and Evidence submission metadata.

#### Scenario: Open run completes
- **WHEN** a custom endpoint run reaches a terminal state
- **THEN** its result SHALL identify the run as open without returning the API key or full endpoint URL

### Requirement: Distinguish untrusted custom cost
The system SHALL preserve provider-reported token counts when available for a custom connector and SHALL set USD cost to null with an untrusted cost state. Official provider runs SHALL retain their existing calculated USD cost.

#### Scenario: Provider returns token usage without pricing
- **WHEN** a custom endpoint returns prompt and completion token counts but no verified price
- **THEN** the run SHALL display token metrics and identify USD cost as unavailable for trusted ranking
