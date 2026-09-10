## ADDED Requirements

### Requirement: Complete a web-based rescue project flow
The product SHALL let a local user open Browser Agent Production Rescue, answer a three-question trial, receive a fixed task, edit an isolated workspace, start a background run, inspect evidence-backed results, compare two runs, and view a delivery report without opening a terminal.

#### Scenario: Reliability golden path
- **WHEN** a user enables the fixed recovery configuration in a reliability session and starts a live run
- **THEN** the backend SHALL run DeepSeek, Browser Use, Chromium, the controlled procurement world, and SQLite in the background and show the SQLite-derived result in the product

### Requirement: Present six product views
The frontend SHALL present Chinese home/project, trial, workspace, run/result, delivery, and replay views. The workspace SHALL use Monaco and the result view SHALL explain outcomes before exposing JSON.

#### Scenario: Learner reaches the workspace
- **WHEN** a user completes the three trial answers
- **THEN** the frontend SHALL show the assigned task, editable Monaco files, browser status, and run controls in Chinese

### Requirement: Evidence is the product source of truth
Every result, comparison, and delivery conclusion SHALL be derived from a saved run bundle or replay bundle and SHALL expose the run/session/task/scenario, workspace hash, changed files, model/runtime provenance, business outcome, continuation facts, metrics, and before/after world state.

#### Scenario: Product shows a completed run
- **WHEN** a background run reaches a terminal state
- **THEN** its product result SHALL be sourced from the saved job evidence and its SQLite-derived business outcome

### Requirement: Preserve fixed task contracts
The product SHALL assign only reliability, prompt-injection safety, and cost/efficiency tasks from a fixed graph. Task ordering SHALL depend only on the trial profile and task acceptance SHALL be programmatic, never delegated to an LLM judge.

#### Scenario: Fixed trial profile
- **WHEN** a learner selects database verification, blocked tools, and cost measurement
- **THEN** the task order SHALL be reliability, safety, then efficiency

### Requirement: Provide explicit replay
Replay SHALL read historical real evidence and label it as historical real run records. It SHALL never represent replay as a new live execution.

#### Scenario: User opens replay
- **WHEN** the user selects historical replay
- **THEN** the product SHALL list stored historical evidence with the historical-real-run label and shall not start a run
