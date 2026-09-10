## 1. Deterministic Markdown Tool

- [ ] 1.1 Add failing tests for required issue types, missing/non-Markdown paths, clean Markdown, and non-mutation.
- [ ] 1.2 Implement the standard-library Markdown checker behind CrewAI `BaseTool`.
- [ ] 1.3 Run the Tool tests and direct smoke assertion without an LLM.

## 2. CrewAI and DeepSeek Wiring

- [ ] 2.1 Add centralized `build_llm()` using only the three DeepSeek environment variables.
- [ ] 2.2 Align one `markdown_quality_reviewer` Agent and one `validate_markdown_task` Task across Python and YAML.
- [ ] 2.3 Require the Task to call the deterministic Tool and forbid source-file mutation or invented findings.
- [ ] 2.4 Verify YAML keys and Crew assembly.

## 3. CLI, Packaging, Examples, and Documentation

- [ ] 3.1 Simplify `main.py` to one positional Markdown path, usage output, Crew kickoff, and result printing.
- [ ] 3.2 Update `pyproject.toml`, `.env.example`, and `.gitignore` for Python 3.10–3.12, `uv`, DeepSeek, and YAML package data.
- [ ] 3.3 Add the deliberately invalid Markdown smoke example.
- [ ] 3.4 Rewrite README with truthful setup, smoke, output, non-mutation, and scope boundaries.

## 4. Verification and Delivery Review

- [ ] 4.1 Run `uv sync`, compilation, tests, Tool smoke, YAML checks, and Crew assembly.
- [ ] 4.2 Run the LLM call and full smoke command when a local DeepSeek key is configured, otherwise record the credential blocker without exposing it.
- [ ] 4.3 Run `uv build` and verify both YAML files are present in the wheel.
- [ ] 4.4 Review changed files, secrets, dependencies, reference-directory immutability, and requirement coverage.
