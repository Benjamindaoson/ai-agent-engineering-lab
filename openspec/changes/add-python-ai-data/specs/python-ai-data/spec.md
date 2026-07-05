## ADDED Requirements

### Requirement: Python module mirrors Java ai-data structure
The system SHALL add `python-ai-data/` with Python counterparts for DTOs, nodes, utilities, application/controller files, and initialization logic.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-ai-data/python_ai_data/`
- **THEN** they can find Python files corresponding to the Java source files in `ai-data/src/main/java/com/zhouyu/`.

### Requirement: Text-to-SQL workflow preserves Java state flow
The workflow SHALL run keyword extraction, table info recall, planning, plan execution, SQL execution, SQL repair, and report generation.

#### Scenario: SQL step succeeds
- **WHEN** a planned SQL query executes successfully
- **THEN** its result is stored in `planExecuteResult` and the next step is selected.

#### Scenario: SQL step fails
- **WHEN** a planned SQL query fails
- **THEN** the plan executor asks the model/client for a fixed SQL statement, updates the current step, and retries SQL execution.

### Requirement: Offline verification works without external services
The module SHALL include tests, a self-check, and an offline demo that do not require MySQL, Elasticsearch, or model credentials.

#### Scenario: Offline demo runs
- **WHEN** the user runs `python -m python_ai_data.offline_demo`
- **THEN** an in-memory SQLite database is queried and an HTML report is produced.
