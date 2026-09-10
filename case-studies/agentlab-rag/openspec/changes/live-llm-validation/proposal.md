## Why

Proof #1 proves the recovery mechanism deterministically, but it does not measure behavior when a real model decides browser actions. A controlled live-model validation adds that second, clearly labeled layer without changing the frozen experiment.

## What Changes

- Add an opt-in, OpenAI-compatible validation runner with selectable `deepseek` and `openai` providers. This change's experiment uses DeepSeek `deepseek-v4-flash`.
- Run five clean baseline worlds and five clean fixed worlds, collecting real model usage, cost, latency, actions, and business-state outcomes.
- Apply per-run action/output limits and preserve every live run separately from deterministic Proof #1 evidence.

## Capabilities

### New Capabilities

- `live-llm-validation`: Reproducible, opt-in measurement of the frozen procurement scenario using a pinned OpenAI model.

### Modified Capabilities

- None.

## Impact

Adds a live execution path under `project_packs/browser_agent_rescue/workspace/`, a local provider/price configuration, evidence fields, tests, and documentation. It reads only the selected provider's API key from the process environment and does not write credentials to disk.
