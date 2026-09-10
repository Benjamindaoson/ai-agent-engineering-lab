## ADDED Requirements

### Requirement: Configure an OpenAI-compatible custom connector
The system SHALL accept a session-scoped custom connector only when it includes a non-empty API key, model identifier, and public HTTPS base URL compatible with OpenAI Chat Completions. It MUST reject URLs with credentials, query strings, fragments, localhost names, and literal private, loopback, link-local, multicast, reserved, or unspecified IP addresses. It SHALL validate that a hostname resolves, but the local single-user product SHALL allow hostnames mapped through an environment-specific transparent proxy.

#### Scenario: Reject a literal local endpoint
- **WHEN** a learner submits `https://10.0.0.8/v1` as a custom endpoint
- **THEN** the system SHALL reject the connector before any model request is sent

#### Scenario: Normalize an eligible endpoint
- **WHEN** a learner submits `https://models.example.test/v1/`, a model id, and a non-empty key
- **THEN** the system SHALL retain a normalized HTTPS base URL and create an in-memory connector without persisting the key

### Requirement: Preflight custom model access
The system SHALL provide a preflight action that validates the connector again, requests the configured model from the OpenAI-compatible Models API, and makes a bounded Chat Completions request whose response contains a choice. It MUST return a clear failure without launching a browser run when those checks fail.

#### Scenario: Compatible endpoint preflight succeeds
- **WHEN** a public connector returns its configured model and a valid chat completion
- **THEN** the system SHALL return public connector provenance with a successful preflight result

#### Scenario: Model is unavailable
- **WHEN** the Models API does not include the configured model
- **THEN** the system SHALL return a preflight failure and SHALL not start Chromium or a background run

### Requirement: Run with the approved connector
The system SHALL revalidate a custom connector supplied at run start and use its endpoint, model, and ephemeral key for that live Browser Use run. A run with no connector SHALL retain the official environment-backed DeepSeek behavior.

#### Scenario: Custom connector reaches the live adapter
- **WHEN** a learner starts a run with a valid custom connector
- **THEN** the live adapter SHALL receive the custom endpoint and model instead of the official provider default
