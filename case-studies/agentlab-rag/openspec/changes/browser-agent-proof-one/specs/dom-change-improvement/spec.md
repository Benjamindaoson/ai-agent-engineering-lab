## ADDED Requirements

### Requirement: Reproducible baseline failure
The DOM-change scenario SHALL cause the declared baseline integration to fail deterministic procurement verification without modifying the task data.

#### Scenario: Baseline under DOM change
- **WHEN** the baseline integration runs `PROC-001` against the DOM-change variant
- **THEN** the task result is unsuccessful and the bundle records the failure evidence

### Requirement: Verified repair
The repaired integration SHALL complete `PROC-001` against the same DOM-change scenario and produce a valid controlled-world purchase request.

#### Scenario: Repair under DOM change
- **WHEN** the repaired integration runs `PROC-001` against the DOM-change variant
- **THEN** deterministic verification succeeds and the bundle records the before/after metrics and world-state evidence
