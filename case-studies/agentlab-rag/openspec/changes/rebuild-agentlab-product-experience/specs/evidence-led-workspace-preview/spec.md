## ADDED Requirements

### Requirement: Preview the false-success incident
The homepage SHALL show a workspace preview for Browser Agent Production Rescue that names the false-success incident, identifies `recovery.py` as relevant code, and distinguishes Agent-reported, page-reported, and business-state success.

#### Scenario: User scans the first viewport
- **WHEN** a user views the homepage without starting a session
- **THEN** they SHALL be able to identify that the page and Agent report success while the verified business state is unsuccessful

### Requirement: Show recorded before-and-after proof
The homepage SHALL show the recorded Baseline and Fixed results: Baseline 0/5 actual success and 5/5 False Success; Fixed 5/5 actual success and 0/5 False Success. It SHALL identify the results as real DeepSeek, Browser Use, Chromium, and SQLite runs rather than simulated animation.

#### Scenario: User reviews proof before entering a project
- **WHEN** the user reaches the proof comparison
- **THEN** they SHALL see both experiment groups, their outcomes, and the provenance label
