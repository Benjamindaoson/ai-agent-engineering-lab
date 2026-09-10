# Markdown Validator Crew Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the copied CrewAI Markdown validator into a runnable DeepSeek-based Agent + custom Tool lesson without changing the official Markdown-quality domain.

**Architecture:** A deterministic standard-library checker is wrapped in a CrewAI `BaseTool`. One YAML-configured Agent explicitly uses a centralized DeepSeek LLM and one YAML-configured Task asks it to call the Tool and summarize the returned findings. The CLI only loads dotenv, reads one path, starts the Crew, and prints the result.

**Tech Stack:** Python 3.10–3.12, `uv`, CrewAI, `python-dotenv`, PyYAML through CrewAI, setuptools `src` layout, standard-library tests.

## Global Constraints

- Modify only `D:\CrewAI-Handwrite\02-markdown-validator`.
- Keep `D:\CrewAI-Handwrite\markdown_validator` read-only.
- `requires-python = ">=3.10,<3.13"`.
- Use only DeepSeek variables: `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL`.
- Do not add Flow, Knowledge, RAG, frontend, FastAPI, database, CI/CD, batch scanning, or auto-repair.
- Do not add `pymarkdownlnt` unless the minimum checker cannot satisfy the requested checks.

## File Map

- Modify `pyproject.toml`: metadata, dependencies, package data, CLI entry point.
- Modify `src/markdown_validator/tools/markdownTools.py`: deterministic checker and `BaseTool` wrapper.
- Modify `src/markdown_validator/crew.py`: DeepSeek builder and one Agent/Task/Crew.
- Modify `src/markdown_validator/config/agents.yaml` and `tasks.yaml`: aligned keys and instructions.
- Modify `src/markdown_validator/main.py`: thin CLI.
- Modify `.env.example`, `.gitignore`, and `README.md`: truthful setup and boundaries.
- Create `examples/bad_markdown.md`: deterministic smoke input.
- Create `tests/test_markdown_tool.py`: direct checker regression coverage.

### Task 1: Lock the checker contract with tests

**Files:**
- Create: `tests/test_markdown_tool.py`

**Interfaces:**
- Consumes: `markdown_validator.tools.markdownTools.MarkdownValidationTool` and its `_run(file_path)` method.
- Produces: assertions for missing files, non-Markdown paths, empty files, required issue types, and clean files.

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from markdown_validator.tools.markdownTools import MarkdownValidationTool


def test_reports_required_markdown_issues(tmp_path: Path) -> None:
    path = tmp_path / "bad.md"
    path.write_text("# One\n### Three  \n#\n# One\n```python\nhttp://example.com\n![ ](image.png)\n", encoding="utf-8")

    report = MarkdownValidationTool()._run(str(path))

    for issue in ("heading-level-jump", "empty-heading", "duplicate-heading", "unclosed-code-fence", "trailing-spaces", "bare-url", "empty-image-alt"):
        assert issue in report
    assert "line 2" in report


def test_reports_missing_and_non_markdown_files(tmp_path: Path) -> None:
    tool = MarkdownValidationTool()
    assert "does not exist" in tool._run(str(tmp_path / "missing.md"))
    text = tmp_path / "notes.txt"
    text.write_text("plain", encoding="utf-8")
    assert "not a Markdown file" in tool._run(str(text))


def test_reports_clean_markdown(tmp_path: Path) -> None:
    path = tmp_path / "good.md"
    path.write_text("# Title\n\n## Section\n\nText.\n", encoding="utf-8")
    assert "No markdown validation issues found" in MarkdownValidationTool()._run(str(path))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_markdown_tool.py -q`

Expected: FAIL because `MarkdownValidationTool` does not exist in the copied legacy Tool module.

- [ ] **Step 3: Implement the minimal checker**

Implement `MarkdownValidationTool(BaseTool)` with `name = "markdown_validation_tool"`, a useful `description`, `_run(file_path: str) -> str`, and a small line scan that emits `line N: <issue-type> - <description>`. Use `Path.read_text(encoding="utf-8")`; return clear error strings for missing/non-`.md` paths; do not write files.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_markdown_tool.py -q`

Expected: all tests pass.

### Task 2: Align CrewAI wiring and DeepSeek configuration

**Files:**
- Modify: `src/markdown_validator/crew.py`
- Modify: `src/markdown_validator/config/agents.yaml`
- Modify: `src/markdown_validator/config/tasks.yaml`

**Interfaces:**
- Consumes: `MarkdownValidationTool` from Task 1.
- Produces: `build_llm()`, `MarkdownValidatorCrew`, one `markdown_quality_reviewer` Agent, and one `validate_markdown_task` Task.

- [ ] **Step 1: Add the failing assembly check**

Run: `uv run python -c "from markdown_validator.crew import MarkdownValidatorCrew; c=MarkdownValidatorCrew().crew(); assert len(c.agents)==1; assert len(c.tasks)==1; print('assembly ok')"`

Expected: FAIL because the copied class and YAML names are not the target names and the old LLM wiring is not centralized.

- [ ] **Step 2: Implement the minimal Crew wiring**

In `crew.py`, load dotenv, read the three DeepSeek variables in `build_llm()`, raise `ValueError("Missing DEEPSEEK_API_KEY; configure it in .env.")` when empty, and return `LLM(model=f"deepseek/{model_name}", api_key=api_key, base_url=base_url, temperature=0.2, timeout=120, max_retries=2, max_tokens=3000)`. The native provider path is required by the installed CrewAI version so no extra LiteLLM dependency is needed. Use exact decorator methods/config keys for `markdown_quality_reviewer` and `validate_markdown_task`; pass `tools=[MarkdownValidationTool()]` and `llm=build_llm()` to the Agent.

- [ ] **Step 3: Replace YAML instructions**

Configure the Agent to summarize actual Tool results, include line/type/description/recommendations, and never edit the file. Configure the Task to call `markdown_validation_tool` with `{filename}`, then report the returned result and a pass recommendation without inventing findings.

- [ ] **Step 4: Run assembly and YAML checks**

Run: `uv run python -c "import yaml; from pathlib import Path; a=yaml.safe_load(Path('src/markdown_validator/config/agents.yaml').read_text()); t=yaml.safe_load(Path('src/markdown_validator/config/tasks.yaml').read_text()); assert set(a)=={'markdown_quality_reviewer'}; assert set(t)=={'validate_markdown_task'}; print('yaml keys ok')"`

Run: `uv run python -c "from markdown_validator.crew import MarkdownValidatorCrew; c=MarkdownValidatorCrew().crew(); print('agents=', len(c.agents), 'tasks=', len(c.tasks), 'process=', c.process)"`

Expected: aligned keys and one Agent/Task. The assembly command requires a configured DeepSeek key because the Agent is explicit about its LLM.

### Task 3: Make the CLI, package metadata, examples, and docs truthful

**Files:**
- Modify: `src/markdown_validator/main.py`
- Modify: `pyproject.toml`
- Modify: `.env.example`
- Modify: `.gitignore`
- Modify: `README.md`
- Create: `examples/bad_markdown.md`

**Interfaces:**
- Consumes: `MarkdownValidatorCrew` and `build_llm()` from Task 2.
- Produces: `markdown_validator` CLI and documented smoke command.

- [ ] **Step 1: Add the failing CLI expectation**

Run: `uv run markdown_validator`

Expected: the copied CLI raises an exception instead of printing the required usage line.

- [ ] **Step 2: Implement the thin CLI and metadata**

Make `run()` load dotenv, print `Usage: uv run markdown_validator examples/bad_markdown.md` and return when there is no argument, otherwise call `MarkdownValidatorCrew().crew().kickoff(inputs={"filename": filename})` and print the result. Set `requires-python = ">=3.10,<3.13"`, keep dependencies to `crewai` and `python-dotenv`, configure setuptools `src` discovery and `config/*.yaml` package data, and keep `[project.scripts] markdown_validator = "markdown_validator.main:run"`.

- [ ] **Step 3: Add the smoke fixture and required docs**

Create `examples/bad_markdown.md` with heading jump, empty heading, duplicate heading, unclosed fence, trailing spaces, bare URL, and empty image alt. Document DeepSeek `.env` setup, `uv sync`, the smoke command, report contents, non-mutation, and excluded features. Do not mention OpenAI keys or real credentials.

- [ ] **Step 4: Run CLI help and static checks**

Run: `uv run markdown_validator`

Expected: the exact usage line and no traceback.

Run: `uv run python -m compileall src`

Expected: exit code 0.

### Task 4: Verify the complete local run and wheel

**Files:**
- Review: all files changed by Tasks 1–3

**Interfaces:**
- Consumes: the complete target project.
- Produces: verification evidence and a ship-readiness report.

- [ ] **Step 1: Synchronize dependencies**

Run: `uv sync`

- [ ] **Step 2: Run deterministic Tool and Crew checks**

Run the direct Tool assertion against `examples/bad_markdown.md`, the YAML key check, and the Crew assembly command. Confirm the example file hash is unchanged before and after the Tool call.

- [ ] **Step 3: Run DeepSeek checks when configured**

If `.env` contains a non-empty `DEEPSEEK_API_KEY`, run `uv run python -c "from markdown_validator.crew import build_llm; print(build_llm().call('只回复 OK'))"` and `uv run markdown_validator examples/bad_markdown.md`. Otherwise report these checks as blocked by missing credentials without printing the key.

- [ ] **Step 4: Build and inspect the wheel**

Run: `uv build`

Run: `uv run python -c "import zipfile; from pathlib import Path; wheel=next(Path('dist').glob('*.whl')); names=zipfile.ZipFile(wheel).namelist(); assert 'markdown_validator/config/agents.yaml' in names; assert 'markdown_validator/config/tasks.yaml' in names; print('wheel yaml ok')"`

- [ ] **Step 5: Review delivery readiness**

Inspect the diff and confirm no reference-directory files changed, no secrets are printed or documented, no unnecessary dependencies remain, and all user requirements are either verified or explicitly marked blocked.
