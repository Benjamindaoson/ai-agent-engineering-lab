## ADDED Requirements

### Requirement: Complete run bundle
The system SHALL write a separate evidence directory for each completed or failed run containing metadata, task, scenario, submission revision, trace, metrics, world state before, world state at Agent completion, world state after, and result.

#### Scenario: Completed run
- **WHEN** a Project Pack run completes
- **THEN** all required bundle files, including the exact `recovery.py` snapshot and its SHA-256 hash, exist under a unique run directory

#### Scenario: Failed run
- **WHEN** a Project Pack run fails before task completion
- **THEN** the bundle records the failure result and the observed world state without claiming success

### Requirement: Versioned cost evidence
The system SHALL record model identifier, input tokens, output tokens, estimated cost, and a local pricing-card version for each run.

#### Scenario: Cost is calculated
- **WHEN** a run reports token usage
- **THEN** the bundle calculates estimated cost from the Project Pack pricing card rather than remote current pricing
