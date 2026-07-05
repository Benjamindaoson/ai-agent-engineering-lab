## ADDED Requirements

### Requirement: Python module mirrors Java ai-multi-model structure
The system SHALL add `python-ai-multi-model/` with Python counterparts for Java application, controller, and Dashscope service files.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-ai-multi-model/python_ai_multi_model/`
- **THEN** they can find Python files corresponding to `ai-multi-model/src/main/java/com/zhouyu/`.

### Requirement: Multimodal capabilities are preserved
The module SHALL demonstrate image generation, image understanding, video understanding stream, and audio transcription followed by summary prompt rendering.

#### Scenario: Controller flows run offline
- **WHEN** the Python controller is created with the offline service
- **THEN** image generation, image chat, video chat, and audio chat return deterministic classroom outputs.

### Requirement: Offline verification works without external services
The module SHALL include tests, a self-check, and an offline demo that do not require DashScope credentials, Spring Boot, DashScope SDK, ffmpeg, or a large video asset.

#### Scenario: Offline demo runs
- **WHEN** the user runs `python -m python_ai_multi_model.offline_demo`
- **THEN** the four multimodal flows are demonstrated without external credentials.
