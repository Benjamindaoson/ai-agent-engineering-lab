# repository-cleanliness Specification

## ADDED Requirements

### Requirement: Publishable source tree

The Python project SHALL exclude local dependencies, caches, build outputs, local databases, editor metadata, and agent-tool metadata.

#### Scenario: Inspecting the clean repository

- **WHEN** a user inspects the project tree
- **THEN** maintained source, tests, lockfiles, schemas, and documentation remain while approved generated paths are absent

### Requirement: One-command local startup

The project SHALL provide `run-local.ps1` at its root.

#### Scenario: First launch from clean source

- **WHEN** a Windows user runs `powershell -ExecutionPolicy Bypass -File .\run-local.ps1`
- **THEN** missing Python and npm dependencies are installed, SQLite is seeded, and AgentLab API and Web services are started

#### Scenario: Setup-only verification

- **WHEN** a user runs `run-local.ps1 -SetupOnly`
- **THEN** dependencies and the database are prepared without starting long-lived services

### Requirement: Safe cleanup boundary

Cleanup SHALL reject recursive deletion targets outside the resolved Python project root.

#### Scenario: Invalid deletion target

- **WHEN** a resolved deletion target is not a descendant of the project root
- **THEN** cleanup stops before deleting that target
