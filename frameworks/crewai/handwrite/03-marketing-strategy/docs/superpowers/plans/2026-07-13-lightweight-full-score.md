# Lightweight Full Score Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the fixed-input CrewAI demo into a reusable, isolated, independently evaluated single-machine CLI without adding infrastructure.

**Architecture:** Add one small runtime I/O module for input validation, output cleanup, and manifests. Keep `crew.py` as the CrewAI orchestration boundary, but inject its output directory and add bounded retries. Let the evaluator generate/check one directory per case.

**Tech Stack:** Python 3.11+, standard-library `argparse`/`json`/`unittest`, CrewAI, DeepSeek-compatible OpenAI API, Serper.

## Global Constraints

- No database, Web service, queue, authentication, or new runtime dependency.
- Preserve the existing six-task sequential CrewAI flow and Pydantic output contracts.
- API failures must be explicit after bounded retries.
- Every generated run must be isolated from stale known output files.

### Task 1: Runtime I/O contract

**Files:**
- Create: `src/marketing_posts/runtime.py`
- Create: `tests/test_runtime.py`
- Create: `inputs.example.json`
- Modify: `src/marketing_posts/main.py`

**Steps:**

- [ ] Write tests for valid overrides, missing required fields, known-output cleanup, and manifest contents.
- [ ] Run `python -m unittest discover -s tests -v` and confirm the new tests fail because the runtime module/API is absent.
- [ ] Implement `load_inputs`, `prepare_output_dir`, `write_manifest`, and `parse_args` using only the standard library.
- [ ] Refactor `main.run` to accept `inputs`, `output_dir`, and CLI arguments while preserving the console entry point.
- [ ] Run the focused tests and confirm they pass.

### Task 2: Output injection and bounded retries

**Files:**
- Modify: `src/marketing_posts/crew.py`
- Modify: `src/marketing_posts/main.py`

**Steps:**

- [ ] Add `output_dir` to `MarketingPostsCrew` and route every task output through it.
- [ ] Add two-attempt retry logic around transient DeepSeek and Serper failures; do not retry validation or context-length errors.
- [ ] Keep Pydantic validation and JSON-object compatibility unchanged.
- [ ] Run compile and runtime wiring checks.

### Task 3: Independent evaluation and source checks

**Files:**
- Modify: `evals/run_eval.py`
- Create: `evals/generate_cases.py`
- Modify: `src/marketing_posts/config/tasks.yaml`

**Steps:**

- [ ] Add a case generator that merges each case with defaults and writes to `output/cases/<case-name>`.
- [ ] Make the evaluator inspect each case directory and its manifest, never the global output directory.
- [ ] Require research source URLs and evidence labels while allowing historical dates and compliance quotations.
- [ ] Run the evaluator against a small fixture and confirm it detects wrong case manifests.

### Task 4: Documentation and full verification

**Files:**
- Modify: `README.md`
- Modify: `evals/README.md`

**Steps:**

- [ ] Document custom input, output directories, case generation, required environment variables, and failure behavior.
- [ ] Run `uv sync`.
- [ ] Run `python -m unittest discover -s tests -v`.
- [ ] Run `python -m compileall -q src evals tests`.
- [ ] Run `uv run python evals/generate_cases.py` and `uv run python evals/run_eval.py`.
- [ ] Run `uv run marketing_posts --input inputs.example.json --output-dir output/smoke` and verify all five required outputs.
