## ADDED Requirements

### Requirement: Extend evidence language to every operational view
Trial, Workspace, Run Result, Delivery, and Replay SHALL use the shared evidence-first token and component language while preserving their current actions and data presentation.

#### Scenario: User progresses from Trial to Run Result
- **WHEN** the user starts a project, submits the trial, edits code, and views a run
- **THEN** each view SHALL preserve its existing functional action while presenting state and evidence with shared visual conventions
