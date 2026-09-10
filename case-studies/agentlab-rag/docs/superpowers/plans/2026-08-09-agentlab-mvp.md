# AgentLab MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local, browser-operable AgentLab MVP around the frozen Browser Agent rescue proofs.

**Architecture:** FastAPI serves a session-safe JSON API and the built React application. Session data lives under `.agentlab/sessions`; background asyncio jobs invoke the existing live runner and write evidence bundles. React polls jobs and renders all conclusions from result evidence.

**Tech Stack:** Python 3.12, FastAPI, Uvicorn, DeepSeek/OpenAI-compatible client, Browser Use, Chromium, SQLite; React, TypeScript, Vite, Monaco.

## Global Constraints

- Preserve frozen proof source, evidence, tags, model, Browser Use commit, and recovery implementation.
- Accept only session allowlisted filenames; never execute learner code.
- Read `DEEPSEEK_API_KEY` only from the server process environment.
- Use fixed task contracts and programmatic acceptance.

---

### Task 1: Session domain and APIs

**Files:** Create `agentlab/domain.py`, `agentlab/sessions.py`, `agentlab/api.py`, `tests/test_agentlab_api.py`.

- [ ] Write failing API tests for create/session workspace/read/write/traversal/trial/task order.
- [ ] Implement literal-only workspace parsing and session isolation.
- [ ] Run focused tests and commit.

### Task 2: Background runs and evidence

**Files:** Create `agentlab/runs.py`, `agentlab/tasks.py`; modify `controlled_world/procurement/app.py`; test `tests/test_agentlab_runs.py`.

- [ ] Write failing tests for job state, cancellation, evidence result, prompt-injection policy, and budget acceptance.
- [ ] Invoke `run_live_once` from an asyncio task and write a session bundle.
- [ ] Run focused tests and commit.

### Task 3: React product

**Files:** Create `agentlab_web/package.json`, `src/*`, Vite configuration; test build/typecheck.

- [ ] Scaffold React/TypeScript/Vite/Monaco and six navigation states.
- [ ] Connect APIs and poll jobs.
- [ ] Build and commit.

### Task 4: Product verification and docs

**Files:** Modify `README.md`; create `DEMO.md`, `scripts/start.ps1`; test browser smoke flow.

- [ ] Verify safe APIs, tests, build, strict specs, and browser Golden Path with a real live run when a key is present.
- [ ] Commit and tag only after evidence-backed verification.
