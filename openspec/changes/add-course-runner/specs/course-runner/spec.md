# course-runner Specification

## ADDED Requirements

### Requirement: Sequential Course Progress

The repository SHALL provide a root command that runs the Python projects as ordered course levels.

#### Scenario: Viewing status

- **WHEN** the user runs `python course.py status`
- **THEN** the command lists all 19 levels with locked, current, or completed status

#### Scenario: Running current level

- **WHEN** the user runs `python course.py run all`
- **THEN** the command runs the current level's `self_check`, `offline_demo`, and `tests`

#### Scenario: Unlocking next level

- **WHEN** the current level run succeeds
- **THEN** the command records progress and unlocks the next level

#### Scenario: Preventing skip ahead

- **WHEN** later levels are not completed
- **THEN** the command does not expose a way to run them directly from the course runner
