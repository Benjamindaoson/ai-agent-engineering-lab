## MODIFIED Requirements

### Requirement: Complete a web-based rescue project flow
The product SHALL let a local user open Browser Agent Production Rescue, answer a three-question trial, receive a fixed task, configure either the official DeepSeek baseline or a custom OpenAI-compatible public HTTPS model connector, edit an isolated workspace, preflight the selected connector, start a background run, inspect evidence-backed results, compare two runs, and view a delivery report without opening a terminal.

#### Scenario: Custom-model golden path
- **WHEN** a user enters a valid endpoint, model id, and key, receives a successful preflight, and starts a live run
- **THEN** the frontend SHALL identify the run as an open-model run and show non-secret connector provenance with its evidence-backed outcome

### Requirement: Present model connection state
The frontend SHALL show the selected model mode, custom endpoint hostname, model id, preflight status, and an external-model disclosure before starting a custom run. It SHALL not render, save, or replay the API key.

#### Scenario: Preflight failure is visible
- **WHEN** connector preflight fails
- **THEN** the frontend SHALL show the returned failure and SHALL not present the connector as ready to run
