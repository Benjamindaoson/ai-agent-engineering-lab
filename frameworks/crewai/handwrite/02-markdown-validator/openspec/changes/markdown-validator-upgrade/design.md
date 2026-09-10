## Context

The reference project is a small CrewAI example with one Markdown validation Tool and one reviewing Agent, but it currently mixes OpenAI configuration, an old LangChain decorator, mismatched YAML keys, and Poetry-oriented documentation. The target must remain a lesson-sized CLI project: one Markdown path enters, a deterministic Tool checks it, and one Agent summarizes the result with DeepSeek.

## Goals / Non-Goals

**Goals:**

- Keep the official Markdown document quality theme and one-Agent/one-Task shape.
- Make the Tool deterministic, line-aware, non-mutating, and directly testable without an LLM.
- Centralize DeepSeek configuration in `build_llm()` and make the Agent use it explicitly.
- Make the `src` layout, YAML packaging, `uv` commands, examples, and README agree.

**Non-Goals:**

- No automatic Markdown repair, batch scanning, repository scanning, Flow, Knowledge, RAG, web UI, FastAPI, database, CI/CD, or cloud deployment.
- No `pymarkdownlnt` dependency for the minimum checker.
- No additional Agents or speculative abstractions.

## Decisions

1. **Use a small standard-library checker.** The Tool will read one path and return a formatted structured report for the required checks: missing/non-Markdown input, empty file, heading jumps, empty headings, duplicate headings, unclosed fenced code, trailing spaces, bare URLs, and empty image alt text. This avoids a runtime dependency on `pymarkdownlnt` and keeps the lesson inspectable. Retaining `pymarkdownlnt` was considered, but rejected because the requested first version values stable local execution over a larger ruleset.

2. **Use CrewAI `BaseTool`.** The custom class will expose `name`, `description`, an input schema, and `_run(file_path: str) -> str`. The installed CrewAI version will be checked before implementation; if its import path differs, the supported installed path will be used. The old `langchain.tools.tool` decorator is removed.

3. **Keep configuration in YAML and align names exactly.** `agents.yaml` will contain `markdown_quality_reviewer`; `tasks.yaml` will contain `validate_markdown_task`; the decorator methods and config lookups will use those same names. The Task explicitly requires the Tool call and forbids source-file mutation.

4. **Use one centralized DeepSeek LLM builder.** `crew.py` will load `.env`, read only `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, and `DEEPSEEK_MODEL`, fail clearly when the key is absent, and return `crewai.LLM(model=f"deepseek/{model_name}", ...)`, which is the installed CrewAI version's native DeepSeek provider path and avoids an extra LiteLLM dependency. The Agent receives `llm=build_llm()` explicitly.

5. **Keep `main.py` thin.** `run()` will load dotenv, read one positional CLI argument, print the exact usage text when absent, build `{"filename": filename}`, kick off the Crew, and print the result. Validation logic remains in the Tool.

## Risks / Trade-offs

- [DeepSeek availability or model naming varies] → Keep all endpoint/model settings in `.env.example` and surface a clear missing-key/configuration error; do not print secrets.
- [A minimal checker is not a full Markdown specification] → Document the supported checks and the deliberately narrow first-version boundary in README.
- [LLM smoke test needs credentials] → Run deterministic Tool and Crew assembly checks without credentials; run the LLM and full smoke checks only when a non-empty local `DEEPSEEK_API_KEY` is available.

## Migration Plan

Copy the read-only reference into the empty target, replace only the target's source/config/docs/examples/tests, run the validation matrix, and keep the reference untouched. Rollback is deleting the target directory or restoring the target's copied files; no external data or user Markdown files are changed.

## Open Questions

None. The user approved the minimal built-in checker design.
