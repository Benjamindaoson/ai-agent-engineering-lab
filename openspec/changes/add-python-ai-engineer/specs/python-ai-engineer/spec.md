## ADDED Requirements

### Requirement: Python module mirrors Java ai-engineer structure
The system SHALL add `python-ai-engineer/` with Python counterparts for `FileTool`, `Plan`, `Step`, `PlannerAgentService`, `ZhouyuAgentHook`, and `EngineerApplication`.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-ai-engineer/python_ai_engineer/`
- **THEN** they can find files corresponding to the Java classes in `ai-engineer/src/main/java/com/zhouyu/`.

### Requirement: Planner service parses and executes plans
The Python planner service SHALL parse planner JSON into `Plan`/`Step` objects and dispatch each step to the named agent.

#### Scenario: Plan executes in order
- **WHEN** a plan contains steps for `architectAgent`, `backendAgent`, `frontendAgent`, and `reviewAgent`
- **THEN** the service calls the matching agents in plan order and returns a completion message.

### Requirement: File tool supports original operations
The Python file tool SHALL support listing a directory, reading a file, and writing a file.

#### Scenario: File is written and read
- **WHEN** `write_file` writes content to a nested file path
- **THEN** parent directories are created and `read_file` returns the same content.

### Requirement: Offline verification works without model credentials
The module SHALL include tests, a self-check, and an offline demo that do not call a remote model.

#### Scenario: Offline demo runs
- **WHEN** the user runs `python -m python_ai_engineer.offline_demo`
- **THEN** fake planner and role agents create deterministic project artifacts locally.
