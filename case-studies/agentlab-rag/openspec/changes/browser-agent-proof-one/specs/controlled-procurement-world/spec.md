## ADDED Requirements

### Requirement: Controlled procurement task
The system SHALL provide task `PROC-001`: create a quantity-20 purchase request for `SKU-1024` using the cheapest supplier that has sufficient inventory.

#### Scenario: Correct procurement request
- **WHEN** an Agent completes `PROC-001` with the valid supplier
- **THEN** the controlled world stores exactly one matching purchase request

#### Scenario: Agent claims completion without world change
- **WHEN** an Agent marks its task done but no matching purchase request exists
- **THEN** deterministic verification marks the task unsuccessful

### Requirement: Controlled DOM variants
The system SHALL serve a baseline DOM variant and a DOM-change variant for the same procurement workflow.

#### Scenario: Baseline page
- **WHEN** the baseline scenario is active
- **THEN** the page exposes the V1 purchase submit control

#### Scenario: Changed page
- **WHEN** the DOM-change scenario is active
- **THEN** the first submit opens a second confirmation page and does not create a purchase request until that confirmation is submitted
