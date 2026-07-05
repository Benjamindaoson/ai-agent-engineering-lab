## ADDED Requirements

### Requirement: Python module mirrors Java ai-consultation structure
The system SHALL add `python-ai-consultation/` with Python counterparts for the Java controller, tools, query expander, department scraper, summary job, vector-store job, and application wiring.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-ai-consultation/python_ai_consultation/`
- **THEN** they can find Python files corresponding to the Java files in `ai-consultation/src/main/java/com/zhouyu/`.

### Requirement: Consultation RAG flow preserves Java behavior
The workflow SHALL use chat history to expand retrieval queries, retrieve department summary documents, stream a model response, and expose a registration tool.

#### Scenario: User asks symptoms
- **WHEN** the user sends a consultation question
- **THEN** the controller retrieves department context and streams response chunks as `{"content": token}`.

#### Scenario: History expands retrieval
- **WHEN** a chat has previous user messages
- **THEN** those user messages are included as retrieval queries.

#### Scenario: Registration tool is called
- **WHEN** a department name is registered
- **THEN** the tool returns the Java success message and records the registration.

### Requirement: Offline verification works without Elasticsearch, MySQL, Playwright, or model credentials
The module SHALL include tests, a self-check, and an offline demo that use in-memory retrieval and fake chat clients.

#### Scenario: Offline demo runs
- **WHEN** the user runs `python -m python_ai_consultation.offline_demo`
- **THEN** department retrieval, consultation response streaming, and registration are demonstrated.
