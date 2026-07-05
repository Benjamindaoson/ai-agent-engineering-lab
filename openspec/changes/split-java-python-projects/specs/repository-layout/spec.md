# repository-layout Specification

## ADDED Requirements

### Requirement: Two named project roots

The repository SHALL expose exactly `handwritten-ai-agent-java/` and `handwritten-ai-agent-python/` as visible top-level project directories.

#### Scenario: Inspecting the repository root

- **WHEN** a user lists non-hidden root entries
- **THEN** only the two named project directories are present

### Requirement: Java project ownership

The Java project SHALL contain the Maven aggregator and all 20 Java/Spring teaching modules with valid relative module declarations.

#### Scenario: Loading the Maven reactor

- **WHEN** Maven reads `handwritten-ai-agent-java/pom.xml`
- **THEN** every declared module path resolves inside the Java project

### Requirement: Python project ownership

The Python project SHALL contain all 19 Python teaching modules, course tooling, AgentLab, specifications, documentation, and production-platform material.

#### Scenario: Discovering course levels

- **WHEN** the Python course runner or quality gate discovers projects
- **THEN** all 19 teaching modules resolve relative to the Python project root

### Requirement: Preserve user work

The migration SHALL NOT delete, restore, or overwrite existing user changes.

#### Scenario: Moving a conflicting path

- **WHEN** a destination already contains an entry with the same name
- **THEN** migration stops and reports the conflict instead of overwriting it
