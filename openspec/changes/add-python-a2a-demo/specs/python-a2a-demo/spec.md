## ADDED Requirements

### Requirement: Python module combines Java A2A client and server demos
The system SHALL add `python-a2a-demo/` with server and client subpackages corresponding to `a2a-server-demo` and `a2a-client-demo`.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-a2a-demo/python_a2a_demo/`
- **THEN** they can find server/client Python files corresponding to both Java modules.

### Requirement: A2A server registration is preserved
The server SHALL register `weatherAgent` with card metadata and expose a weather result under `weatherResult`.

#### Scenario: Weather agent is invoked
- **WHEN** `weatherAgent` receives a weather input
- **THEN** the returned state contains `weatherResult`.

### Requirement: A2A client invocation is preserved
The client SHALL discover a remote weather agent through a registry and support sequential execution with a local React-style agent.

#### Scenario: Remote agent is called
- **WHEN** the client remote agent invokes `weatherAgent`
- **THEN** it returns the remote weather state.

#### Scenario: Sequential agent is called
- **WHEN** the client sequential agent invokes a weather input
- **THEN** it returns both remote weather result and local react-agent result.

### Requirement: Offline verification works without Nacos or live model credentials
The module SHALL include tests, a self-check, and an offline demo using an in-memory registry.

#### Scenario: Offline demo runs
- **WHEN** the user runs `python -m python_a2a_demo.offline_demo`
- **THEN** server registration, remote invocation, and sequential invocation are demonstrated.
