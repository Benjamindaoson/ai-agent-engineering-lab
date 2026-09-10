## Why

The copied CrewAI markdown validator is not aligned with the second-course goal: its deterministic Markdown tool uses an outdated LangChain decorator, its Agent and Task configuration keys do not match the intended design, and its OpenAI/Poetry documentation is disconnected from the actual project. This change upgrades the example into a runnable DeepSeek-based lesson that demonstrates Agent + custom Tool without changing the Markdown-quality domain.

## What Changes

- Replace the legacy LangChain Tool decorator with a CrewAI `BaseTool` implementation.
- Add a small deterministic Markdown checker that returns file errors and line-level issues without editing the source file.
- Centralize DeepSeek LLM construction and inject the same LLM into the single reviewer Agent.
- Align YAML keys with one `markdown_quality_reviewer` Agent and one `validate_markdown_task` Task.
- Simplify the CLI to accept one Markdown path and print the Crew result or usage text.
- Update dependencies, package-data configuration, `.env.example`, `.gitignore`, README, and smoke-test examples for `uv` and Python 3.10–3.12.
- Add focused tests for the deterministic checker and CLI-facing behavior.

## Capabilities

### New Capabilities

- `markdown-validation`: Deterministic inspection of one Markdown file with structured line-level findings and no file mutation.
- `markdown-review-crew`: One CrewAI reviewer Agent that calls the validation Tool and summarizes findings and recommendations.

### Modified Capabilities

None.

## Impact

- Affected source: `src/markdown_validator/main.py`, `crew.py`, `config/*.yaml`, and `tools/markdownTools.py`.
- Affected project metadata and docs: `pyproject.toml`, `.env.example`, `.gitignore`, `README.md`.
- Added examples and tests under `examples/` and `tests/`.
- Runtime dependency remains limited to CrewAI and `python-dotenv`; no `pymarkdownlnt` dependency is required for the minimum checker.
