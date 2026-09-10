# Custom Model Connectors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a local AgentLab learner preflight and run a public HTTPS OpenAI Chat Completions-compatible custom model endpoint without persisting its key or misrepresenting its cost as official.

**Architecture:** `agentlab.model_connectors` owns validation, public provenance and preflight. API routes construct a connector only for a request; `RunManager` persists its public form while the live executor receives the in-memory connector. The existing Browser Use adapter receives an explicit provider/key override, while no-connector runs preserve the official DeepSeek path.

**Tech Stack:** Python 3.12, FastAPI, httpx/OpenAI SDK, Browser Use, pytest, React 19, TypeScript, Vite.

## Global Constraints

- Custom endpoints MUST be public HTTPS and OpenAI Chat Completions-compatible.
- API keys MUST NOT be persisted, logged, returned, embedded in Evidence, or added to frontend persistence.
- No-connector execution MUST retain the frozen DeepSeek proof path.
- Custom USD cost is unavailable/untrusted; do not synthesize a price.
- Historical proof artifacts and untracked runtime/evidence directories remain untouched.

---

### Task 1: Connector module and tests

**Files:**
- Create: `agentlab/model_connectors.py`
- Create: `tests/test_model_connectors.py`

**Interfaces:**
- Produces: `CustomModelConnector`, `parse_connector`, `preflight_connector`, and `ConnectorValidationError`.
- Consumes: JSON-shaped endpoint/model/key input from FastAPI routes.

- [ ] **Step 1: Write failing connector tests**

```python
def test_parse_connector_rejects_local_endpoint():
    with pytest.raises(ConnectorValidationError):
        parse_connector({'endpoint': 'http://127.0.0.1:8000/v1', 'model': 'test', 'api_key': 'x'})
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run: `uv run pytest tests/test_model_connectors.py -q`

- [ ] **Step 3: Implement minimal parsing, public provenance, and fake-client preflight support**

```python
connector = parse_connector(payload)
assert 'api_key' not in connector.public_provenance()
```

- [ ] **Step 4: Run focused connector tests and verify they pass**

Run: `uv run pytest tests/test_model_connectors.py -q`

### Task 2: Live-provider and run-manager integration

**Files:**
- Modify: `project_packs/browser_agent_rescue/workspace/live.py`
- Modify: `agentlab/live_executor.py`
- Modify: `agentlab/runs.py`
- Modify: `tests/test_agentlab_runs.py`

**Interfaces:**
- Consumes: optional `CustomModelConnector` from a run start request.
- Produces: public connector provenance in completed jobs and Evidence submission metadata.

- [ ] **Step 1: Write a failing run-manager test for public-only connector persistence**

```python
assert result['model_connector']['classification'] == 'open'
assert 'api_key' not in str(result)
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run: `uv run pytest tests/test_agentlab_runs.py -q`

- [ ] **Step 3: Add explicit provider key override and propagate connector data through the executor**

```python
provider = provider_from_connector(connector)
outcome = await run_live_once(base_url, fixed=True, provider=provider)
```

- [ ] **Step 4: Run focused run tests and verify they pass**

Run: `uv run pytest tests/test_agentlab_runs.py -q`

### Task 3: API and React workbench

**Files:**
- Modify: `agentlab/api.py`
- Modify: `tests/test_agentlab_api.py`
- Modify: `agentlab_web/src/App.tsx`
- Modify: `agentlab_web/src/product.css`
- Modify: `tests/test_agentlab_ui.py`

**Interfaces:**
- Produces: `POST /api/sessions/{session_id}/model-connector/preflight` and optional `model_connector` in run start payload.
- Consumes: non-persistent form state in the workbench.

- [ ] **Step 1: Write failing API and UI-source tests**

```python
response = client.post(f'/api/sessions/{session_id}/model-connector/preflight', json={'endpoint': 'https://models.example.test/v1', 'model': 'demo', 'api_key': 'secret'})
assert 'secret' not in response.text
```

- [ ] **Step 2: Run the focused tests and verify they fail**

Run: `uv run pytest tests/test_agentlab_api.py tests/test_agentlab_ui.py -q`

- [ ] **Step 3: Implement API boundary and model selector/preflight UX**

```tsx
<button onClick={preflightConnector}>连接预检</button>
```

- [ ] **Step 4: Run focused API/UI tests and verify they pass**

Run: `uv run pytest tests/test_agentlab_api.py tests/test_agentlab_ui.py -q`

### Task 4: Full verification

**Files:**
- Modify: `README.md`
- Modify: `openspec/changes/custom-model-connectors/tasks.md`

- [ ] **Step 1: Document the connector protocol, public endpoint limitation, and key handling**
- [ ] **Step 2: Run Python, frontend, OpenSpec, API, and browser verification**

Run:

```powershell
uv run pytest -q -p no:cacheprovider
npm --prefix agentlab_web run typecheck
npm --prefix agentlab_web run build
openspec validate custom-model-connectors --strict
```
