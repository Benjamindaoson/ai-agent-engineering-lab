## ADDED Requirements

### Requirement: Python module mirrors Java ai-weekly-report structure
The system SHALL add `python-ai-weekly-report/` with Python counterparts for the Java Git tool, email tool, controller, and application wiring.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-ai-weekly-report/python_ai_weekly_report/`
- **THEN** they can find Python files corresponding to the Java source files in `ai-weekly-report/src/main/java/com/zhouyu/`.

### Requirement: Weekly report flow preserves Java tool behavior
The workflow SHALL read weekly Git commits for the local Git user, generate a Markdown weekly report, retain it by chat id, and send it only after human confirmation.

#### Scenario: Project path starts report generation
- **WHEN** the user submits a Git project path
- **THEN** the Git tool reads commit logs and the controller streams Markdown report chunks.

#### Scenario: Confirmation sends prepared report
- **WHEN** the user confirms sending after a report is generated
- **THEN** the email tool receives the prepared report as HTML content.

### Requirement: Offline verification works without external services
The module SHALL include tests, a self-check, and an offline demo that do not require model credentials or live SMTP.

#### Scenario: Offline demo runs
- **WHEN** the user runs `python -m python_ai_weekly_report.offline_demo`
- **THEN** a temporary Git repository is summarized and an email dry-run result is produced.
