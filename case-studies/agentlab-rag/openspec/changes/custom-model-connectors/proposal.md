## Why

AgentLab currently exposes a real Browser Agent run but hard-codes DeepSeek and a process-wide environment key. Learners and open-competition entrants need to validate the same evidence contract with their own model provider, model name, and API key without leaking credentials or weakening the official baseline.

## What Changes

- Add a session-scoped custom model connector for public HTTPS, OpenAI Chat Completions-compatible endpoints.
- Add server-side endpoint validation and a non-secret preflight that checks URL safety, authentication, model access, and Chat Completions response shape before a live run begins.
- Pass the approved connector to the existing real Browser Use runner, meter provider-reported usage when available, and record a non-secret model fingerprint in Evidence.
- Expose connector configuration and preflight state in the product UI.
- Label user-supplied connectors as an open-model run so their self-reported USD cost is informative rather than a trusted official ranking metric.

## Capabilities

### New Capabilities
- `custom-model-connector`: Session-scoped configuration, safety validation, preflight, and execution of OpenAI Chat Completions-compatible custom model endpoints.
- `open-model-run-provenance`: Evidence and UI disclosure for user-supplied model endpoints and untrusted provider-reported cost.

### Modified Capabilities
- `agentlab-product-mvp`: The local run workflow accepts a validated custom model connector in addition to the official DeepSeek baseline.
- `agentlab-session-security`: Session APIs accept secrets only for ephemeral connector execution and never persist or return them.

## Impact

- Affected backend: `agentlab/api.py`, `agentlab/runs.py`, `agentlab/live_executor.py`, and a new connector module.
- Affected frozen-run adapter: `project_packs/browser_agent_rescue/workspace/live.py` gains a provider override without changing the default DeepSeek proof path.
- Affected frontend: `agentlab_web/src/App.tsx` and styling for connector setup and preflight feedback.
- Affected tests: API, run manager, connector validation/preflight, and UI source contract tests.
