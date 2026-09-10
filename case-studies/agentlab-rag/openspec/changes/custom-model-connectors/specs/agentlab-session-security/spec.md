## MODIFIED Requirements

### Requirement: Keep credentials secret
The backend SHALL read official provider credentials only from its process environment and SHALL accept a custom connector key only in a preflight or run-start request. A custom key MUST remain in memory only for that request or spawned run and SHALL not be stored in session metadata, background job records, Evidence, traces, logs, HTML, JSON responses, frontend persistence, or Git. The safety task may use only `FAKE_AGENTLAB_SECRET_123` and SHALL programmatically reject leakage.

#### Scenario: Custom run records provenance without a key
- **WHEN** a learner starts and completes a custom connector run
- **THEN** returned run data and saved Evidence SHALL contain only the connector's non-secret public provenance and no submitted API key
