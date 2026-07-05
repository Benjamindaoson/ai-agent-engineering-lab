## ADDED Requirements

### Requirement: Python module mirrors Java ai-deepresearch structure
The system SHALL add `python-ai-deepresearch/` with Python counterparts for Java DTOs, nodes, utilities, application, controller, observation configuration, and parallel streaming example.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-ai-deepresearch/python_ai_deepresearch/`
- **THEN** they can find Python files corresponding to the Java source files in `ai-deepresearch/src/main/java/com/zhouyu/`.

### Requirement: Deep research workflow preserves node state flow
The workflow SHALL run coordinator, planner, researchers, and reporter using state keys equivalent to the Java graph.

#### Scenario: Coordinator requests planning
- **WHEN** coordinator returns `NEED_PLAN`
- **THEN** planner creates a plan, researchers execute plan steps, and reporter generates the final report.

#### Scenario: Coordinator answers directly
- **WHEN** coordinator returns text other than `NEED_PLAN`
- **THEN** the workflow returns that text without running planner or reporter.

### Requirement: Plan JSON is parsed into DTOs
The module SHALL parse raw or fenced JSON into `Plan(title, steps)` and `Step(title, prompt)`.

#### Scenario: Fenced plan JSON is returned
- **WHEN** planner output contains a markdown JSON fence
- **THEN** the plan parser strips the fence and loads the steps.

### Requirement: Offline verification works without model credentials
The module SHALL include tests, a self-check, and an offline demo that do not call a remote model.

#### Scenario: Offline demo runs
- **WHEN** the user runs `python -m python_ai_deepresearch.offline_demo`
- **THEN** fake clients produce a deterministic research report.
