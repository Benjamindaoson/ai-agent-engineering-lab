# Markdown Validator Crew Upgrade Design

## Intent

Upgrade the copied CrewAI `markdown_validator` example into the second course lesson: one deterministic Markdown-checking Tool is called by one CrewAI reviewer Agent, which summarizes issues and recommendations using DeepSeek.

## Boundaries

The project accepts one Markdown path and prints a report. It does not edit Markdown files and does not include Flow, Knowledge, RAG, frontend, FastAPI, database, CI/CD, batch scanning, or multiple-Agent collaboration.

## Implementation

- Keep the `markdown_validator` package and CLI entry point.
- Replace the LangChain decorator Tool with CrewAI `BaseTool`.
- Use a small standard-library checker for the explicitly requested Markdown rules.
- Centralize DeepSeek setup in `build_llm()` with the installed CrewAI native `deepseek/` provider path and inject it into the single Agent.
- Align `markdown_quality_reviewer` and `validate_markdown_task` across Python and YAML.
- Package `config/*.yaml` through setuptools and document `uv` commands.

## Verification

Run `uv sync`, `compileall`, YAML key checks, a direct Tool assertion, Crew assembly, the LLM call when credentials exist, the full CLI smoke test, and `uv build` plus wheel-content inspection.
