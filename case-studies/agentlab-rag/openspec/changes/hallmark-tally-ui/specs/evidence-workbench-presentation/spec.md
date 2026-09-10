## ADDED Requirements

### Requirement: Make engineering evidence visually scannable
The workspace and result views SHALL present task acceptance, run state, business success, false success, recovery, steps, model calls, duration, and cost as visual status and metric components before raw structured data.

#### Scenario: User opens a completed run
- **WHEN** a run reaches a terminal status
- **THEN** the result view SHALL show its business outcome and engineering metrics in a scannable metric layout

### Requirement: Preserve factual product copy
The redesign SHALL use AgentLab's actual task names, task descriptions, API values, and historical replay data. It SHALL not add customer logos, revenue claims, prices, or usage claims derived from the Hallmark examples.

#### Scenario: User opens the home view
- **WHEN** the home view renders
- **THEN** all product claims SHALL describe the real Browser Agent, controlled world, SQLite, Evidence, and fixed task graph
