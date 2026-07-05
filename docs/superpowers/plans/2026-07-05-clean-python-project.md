# Python Project Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove regenerable and tool-specific files while leaving a clean source tree that restores dependencies and launches AgentLab with one PowerShell command.

**Architecture:** Deletion uses an explicit absolute-path allowlist plus name-based generated-directory discovery constrained to the Python project root. A single `run-local.ps1` performs first-run setup, database seeding, and API/Web startup without adding dependencies.

**Tech Stack:** PowerShell 7/Windows PowerShell, Python 3.13, npm, FastAPI/Uvicorn, Next.js

## Global Constraints

- Delete only targets explicitly approved in `docs/superpowers/specs/2026-07-05-clean-python-project-design.md`.
- Resolve every recursive deletion target and verify it is inside `handwritten-ai-agent-python`.
- Preserve course source, tests, product source, lockfiles, schema, seed data, and maintained documentation.
- Do not add a process-manager dependency.

---

### Task 1: Record cleanup contract

**Files:**
- Create: `openspec/changes/clean-python-project/`

- [ ] Create proposal, design, repository-cleanliness specification, and implementation tasks.
- [ ] Record the pre-cleanup size and exact deletion allowlist.
- [ ] Verify every listed target exists inside the Python project root or is safely absent.

### Task 2: Add one-command local runner

**Files:**
- Create: `run-local.ps1`
- Modify: `README.md`

- [ ] Implement tool checks, virtual-environment creation, `pip install`, `npm ci`, seed, and `-SetupOnly`.
- [ ] Implement API and Web startup with explicit working directories, process IDs, URLs, and stop instructions.
- [ ] Document `powershell -ExecutionPolicy Bypass -File .\run-local.ps1` and `-SetupOnly`.
- [ ] Parse the script with the PowerShell parser and require zero syntax errors.

### Task 3: Delete approved generated and tool-specific content

**Files:**
- Delete: paths listed in the approved design

- [ ] Resolve the project root and reject any target outside it.
- [ ] Delete top-level agent/editor configuration and obsolete snake demo files.
- [ ] Delete AgentLab dependency, build, cache, local database, and nested metadata paths.
- [ ] Delete all generated `__pycache__`, `.pytest_cache`, `output`, and approved `workspace` directories under the project.
- [ ] Verify every approved deletion target is absent.

### Task 4: Restore from clean source and verify

**Files:**
- Test: `run-local.ps1`
- Test: `tests/`
- Test: `AI_Agent_Builder/apps/api/tests/`
- Test: `AI_Agent_Builder/apps/web/`

- [ ] Run `run-local.ps1 -SetupOnly` from the clean state and require exit code 0.
- [ ] Run root Python tests and the 19-project quality gate.
- [ ] Run AgentLab API tests, Web type check, and Web production build.
- [ ] Start services with the one-command runner, verify API `/health` and Web HTTP response, then stop the launched processes.
- [ ] After verification, re-delete regenerated `.venv`, `node_modules`, caches, database, and build output so the final tree remains clean; `run-local.ps1` must recreate them on the next one-command launch.
- [ ] Report final source size, retained local dependency size, and Git status.
