## ADDED Requirements

### Requirement: Python module mirrors Java spring-ai-alibaba-demo structure
The system SHALL add `python-ai-alibaba-demo/` with Python counterparts for the Java application, controller, Baidu, Markdown, and PDF demo classes.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-ai-alibaba-demo/python_ai_alibaba_demo/`
- **THEN** they can find Python files corresponding to Java files in `spring-ai-alibaba-demo/src/main/java/com/zhouyu/`.

### Requirement: Spring AI Alibaba capability demos are preserved
The module SHALL demonstrate DashScope-compatible chat config, tool-style city time calling, Baidu search request shape, reranked retrieval, chat-memory RAG, file question answering, Markdown parsing, and PDF parsing fallback.

#### Scenario: Controller flow runs offline
- **WHEN** the Python controller is created with fake chat and in-memory vector store dependencies
- **THEN** chat, Baidu search, rank chat, memory RAG, and file chat methods return deterministic classroom outputs.

#### Scenario: Document parser demos run offline
- **WHEN** Markdown and PDF parser demo modules are executed
- **THEN** they return document objects with content and metadata without requiring Spring AI Alibaba, PDFBox, Elasticsearch, or DashScope credentials.

### Requirement: Offline verification works without external services
The module SHALL include tests, a self-check, and an offline demo that do not require model credentials, Elasticsearch, Baidu access, DashScope access, or PDF extraction dependencies.

#### Scenario: Offline demo runs
- **WHEN** the user runs `python -m python_ai_alibaba_demo.offline_demo`
- **THEN** parser, search, chat, RAG, and file-chat examples are demonstrated.
