# Browser Agent Proof #1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove a pinned Browser Use runtime can be repaired through AgentLab-owned integration code and produce repeatable evidence of a real controlled-world improvement.

**Architecture:** AgentLab owns a small FastAPI/SQLite procurement world, a `browser-agent-rescue` Project Pack, deterministic scorers, and a directory-based evidence bundle. Browser Use stays untouched in `sources/browser-use`; the Project Pack imports it as a local dependency and runs a real Chromium session through its public APIs.

**Tech Stack:** Python 3.12, FastAPI, Uvicorn, SQLite, Pytest, Browser Use from `sources/browser-use`, `uv`.

## Global Constraints

- Browser Use HEAD MUST equal `32601887cfbc9f4f1e3cad3e2b678e56aeaeaae4` before a pack run.
- Never edit or commit files under `sources/browser-use`.
- Proof #1 contains one site, `PROC-001`, and the DOM-change scenario only.
- No model API key, host secret, Docker socket, or real credential enters the proof runtime.
- Deterministic business state is the source of success; an Agent `done` result is not.
- Evidence cost MUST use a versioned local pricing card.

---

### Task 1: Create the AgentLab runtime shell

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `runtime/__init__.py`
- Create: `runtime/provenance.py`
- Create: `tests/test_provenance.py`

**Interfaces:**
- Produces: `assert_browser_use_commit(repo_root: Path, expected_commit: str) -> str`
- Consumes: `sources/browser-use/.git`

- [ ] **Step 1: Write the failing provenance test**

```python
def test_audited_browser_use_commit_is_accepted(repo_root: Path) -> None:
    assert assert_browser_use_commit(repo_root, AUDITED_COMMIT) == AUDITED_COMMIT
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_provenance.py -q`

- [ ] **Step 3: Add the minimal Python project and provenance helper**

Use `subprocess.run(["git", "-C", str(source_dir), "rev-parse", "HEAD"], check=True, capture_output=True, text=True)` and raise a clear `RuntimeError` on a mismatch.

- [ ] **Step 4: Run the provenance test**

Run: `uv run pytest tests/test_provenance.py -q`

### Task 2: Build the controlled procurement world

**Files:**
- Create: `controlled_world/procurement/app.py`
- Create: `controlled_world/procurement/store.py`
- Create: `controlled_world/procurement/templates/*.html`
- Create: `tests/test_procurement_world.py`

**Interfaces:**
- Produces: `create_app(scenario_id: str) -> FastAPI`
- Produces: `snapshot_world() -> dict`
- Produces: `create_purchase_request(sku: str, quantity: int, supplier_id: str) -> dict`

- [ ] **Step 1: Write failing state tests for `PROC-001`**

```python
def test_correct_procurement_request_is_persisted(client) -> None:
    response = client.post('/purchase', data={'sku': 'SKU-1024', 'quantity': '20', 'supplier_id': 'sup-low'})
    assert response.status_code == 303
    assert client.get('/internal/world-state').json()['purchase_requests'][0]['supplier_id'] == 'sup-low'
```

- [ ] **Step 2: Run the world test to verify it fails**

Run: `uv run pytest tests/test_procurement_world.py -q`

- [ ] **Step 3: Implement the minimal SQLite store and FastAPI routes**

Seed `SKU-1024` with one insufficient or overpriced supplier and one valid lowest-price supplier. Keep data in a per-run SQLite file.

- [ ] **Step 4: Add V1/V2 submit markup selected by `scenario_id`**

V1 exposes `id="submit-order"`. V2 exposes `data-action="purchase-submit"`, keeps an accessible submit label, and delays the confirmation state.

- [ ] **Step 5: Run the world tests**

Run: `uv run pytest tests/test_procurement_world.py -q`

### Task 3: Add the Project Pack and learner integration boundary

**Files:**
- Create: `project_packs/browser_agent_rescue/manifest.yaml`
- Create: `project_packs/browser_agent_rescue/tasks/tasks.json`
- Create: `project_packs/browser_agent_rescue/pricing.yaml`
- Create: `project_packs/browser_agent_rescue/workspace/agent_config.py`
- Create: `project_packs/browser_agent_rescue/workspace/tool_policy.py`
- Create: `project_packs/browser_agent_rescue/workspace/completion.py`
- Create: `project_packs/browser_agent_rescue/workspace/recovery.py`
- Create: `project_packs/browser_agent_rescue/workspace/budget.py`
- Create: `project_packs/browser_agent_rescue/workspace/runner.py`
- Create: `tests/test_project_pack.py`

**Interfaces:**
- Produces: `run_task(task_id: str, scenario_id: str, mode: Literal['baseline', 'repair']) -> RunFacts`
- Produces: `verify_procurement_completion(world_state: dict, task: dict) -> CompletionResult`

- [ ] **Step 1: Write failing tests for manifest provenance and false success**

```python
def test_agent_done_without_purchase_request_is_false_success() -> None:
    result = verify_procurement_completion({'purchase_requests': []}, PROC_001)
    assert not result.success
```

- [ ] **Step 2: Run the pack test to verify it fails**

Run: `uv run pytest tests/test_project_pack.py -q`

- [ ] **Step 3: Implement workspace configuration and restricted tool policy**

Create Browser Use `Tools` with `search`, `read_file`, `write_file`, `replace_file`, and `upload_file` excluded. Permit only the controlled host.

- [ ] **Step 4: Implement completion, recovery, and budget policies**

Completion reads the controlled world state. Budget records raw usage and calculates cost from `pricing.yaml`.

- [ ] **Step 5: Run the pack tests**

Run: `uv run pytest tests/test_project_pack.py -q`

### Task 4: Produce evidence bundles and deterministic Browser Use execution

**Files:**
- Create: `evidence/bundle.py`
- Create: `runtime/scripted_model.py`
- Create: `tests/test_evidence_bundle.py`
- Create: `tests/test_browser_use_proof.py`

**Interfaces:**
- Produces: `write_run_bundle(facts: RunFacts, destination: Path) -> Path`
- Produces: `ScriptedChatModel` compatible with Browser Use's `BaseChatModel`

- [ ] **Step 1: Write failing evidence-bundle tests**

```python
def test_failed_run_bundle_contains_world_states_and_result(tmp_path: Path) -> None:
    bundle = write_run_bundle(failed_facts(), tmp_path)
    assert (bundle / 'world_state_before.json').exists()
    assert (bundle / 'world_state_after.json').exists()
    assert (bundle / 'result.json').read_text().find('success') >= 0
```

- [ ] **Step 2: Run the evidence test to verify it fails**

Run: `uv run pytest tests/test_evidence_bundle.py -q`

- [ ] **Step 3: Implement JSON/JSONL evidence writing**

Write `metadata.json`, `task.json`, `scenario.json`, `submission.json`, `trace.jsonl`, `metrics.json`, `world_state_before.json`, `world_state_after.json`, and `result.json`.

- [ ] **Step 4: Implement the scripted model and a real Chromium proof run**

The scripted model invokes Browser Use actions; it never writes world-state outcomes itself. The browser session must launch headless Chromium, execute the controlled pages, and collect `AgentHistory` facts.

- [ ] **Step 5: Run the proof test**

Run: `uv run pytest tests/test_browser_use_proof.py -q`

### Task 5: Demonstrate the DOM-change repair

**Files:**
- Create: `project_packs/browser_agent_rescue/scenarios/dom_change.yaml`
- Modify: `project_packs/browser_agent_rescue/workspace/recovery.py`
- Create: `tests/test_dom_change_improvement.py`

**Interfaces:**
- Produces: baseline and repaired `RunFacts` for the same task and scenario

- [ ] **Step 1: Write the failing before/after proof test**

```python
def test_dom_change_repair_improves_real_world_result(tmp_path: Path) -> None:
    baseline = run_task('PROC-001', 'DOM-V2', mode='baseline')
    repaired = run_task('PROC-001', 'DOM-V2', mode='repair')
    assert not baseline.result.success
    assert repaired.result.success
```

- [ ] **Step 2: Run the proof test to verify it fails**

Run: `uv run pytest tests/test_dom_change_improvement.py -q`

- [ ] **Step 3: Implement the smallest recovery repair**

The baseline targets only the V1 control. The repair waits for and uses the V2 semantic control, then verifies persisted world state.

- [ ] **Step 4: Run the DOM-change test and inspect both evidence bundles**

Run: `uv run pytest tests/test_dom_change_improvement.py -q`

### Task 6: Document and verify Proof #1

**Files:**
- Modify: `README.md`
- Create: `docs/proof-1.md`

- [ ] **Step 1: Document the one-command local proof, evidence bundle contract, safety boundaries, and the optional live-model configuration**

- [ ] **Step 2: Run the focused test suite from the project root**

Run: `uv run pytest tests -q`

- [ ] **Step 3: Run the provenance guard and inspect generated evidence files**

Run: `uv run python -m runtime.provenance`

- [ ] **Step 4: Mark completed OpenSpec tasks and validate the change**

Run: `openspec validate browser-agent-proof-one --strict`
