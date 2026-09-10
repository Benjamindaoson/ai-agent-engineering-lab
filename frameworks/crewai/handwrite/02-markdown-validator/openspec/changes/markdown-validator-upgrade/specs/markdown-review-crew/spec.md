## ADDED Requirements

### Requirement: Summarize Tool results with one reviewer Agent
The Crew SHALL contain one Agent named `markdown_quality_reviewer` and one Task named `validate_markdown_task`; the Agent SHALL call the Markdown validation Tool before summarizing findings and recommendations.

#### Scenario: Crew assembly
- **WHEN** `MarkdownValidatorCrew().crew()` is constructed
- **THEN** it contains one Agent, one Task, and sequential processing with matching YAML keys

#### Scenario: Agent reviews a file
- **WHEN** the CLI starts the Crew with `{"filename": filename}`
- **THEN** the Agent receives the Tool result and outputs a Markdown issue summary, line/type explanations, recommendations, and a pass recommendation

### Requirement: Use DeepSeek explicitly
The reviewer Agent SHALL use the centralized DeepSeek LLM configuration and SHALL not depend on OpenAI environment variables or SERPER configuration.

#### Scenario: Configured DeepSeek
- **WHEN** `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, and `DEEPSEEK_MODEL` are loaded
- **THEN** `build_llm()` returns a CrewAI LLM configured with those values

#### Scenario: Missing DeepSeek key
- **WHEN** `DEEPSEEK_API_KEY` is empty
- **THEN** `build_llm()` raises a clear configuration error without logging a secret

### Requirement: Provide a thin CLI
The package SHALL expose the `markdown_validator` command, accept one Markdown path, print usage when no path is supplied, and print the Crew result without editing the input file.

#### Scenario: Valid CLI invocation
- **WHEN** the command receives `examples/bad_markdown.md`
- **THEN** it starts the Crew with `inputs = {"filename": filename}` and prints the resulting report

#### Scenario: Missing CLI argument
- **WHEN** the command receives no path
- **THEN** it prints `Usage: uv run markdown_validator examples/bad_markdown.md`
