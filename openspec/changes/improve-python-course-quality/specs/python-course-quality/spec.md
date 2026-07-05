# python-course-quality Specification

## ADDED Requirements

### Requirement: Full Python Quality Gate

The repository SHALL provide a root command that checks all Python course projects.

#### Scenario: Running all Python checks

- **WHEN** the user runs `python scripts/python_quality_gate.py`
- **THEN** the command runs `self_check`, `tests`, and `offline_demo` for each of the 19 Python projects

#### Scenario: Reporting failed checks

- **WHEN** any project check fails or times out
- **THEN** the command exits with a non-zero status

### Requirement: Clear External Dependency Errors

Python projects SHALL return clear errors for missing local command dependencies used by classroom demos.

#### Scenario: Missing Git

- **WHEN** Git is not available for the weekly report project
- **THEN** the project raises a clear Git dependency error

#### Scenario: Missing Docker

- **WHEN** Docker is not available for the Manus sandbox
- **THEN** the project raises a clear Docker dependency error
