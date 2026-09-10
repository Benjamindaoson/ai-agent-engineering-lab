## Why

AgentLab has frozen deterministic and live recovery proofs, but they are only usable from source code and the terminal. A local single-user product is needed so a learner can safely inspect, change, run, and compare the proven Browser Agent engineering workflows.

## What Changes

- Add a FastAPI product backend with isolated session workspaces, fixed task graph, background live-run jobs, evidence-backed results, replay, and delivery reports.
- Add a React, TypeScript, Vite, and Monaco frontend with home, trial, workspace, run/result, delivery, and replay views.
- Add three fixed task definitions: reliability, prompt-injection safety, and cost/efficiency.
- Preserve frozen proof source, evidence, and tags; the product reads historical evidence rather than replacing it.

## Capabilities

### New Capabilities
- `agentlab-product-mvp`: Local web workflow for trial, task assignment, safe editing, live runs, evidence, delivery, and replay.
- `agentlab-session-security`: Filesystem allowlist, session isolation, and secret-safe APIs.
- `agentlab-engineering-task-graph`: Fixed reliability, safety, and efficiency task contracts with programmatic acceptance.

### Modified Capabilities
- None.

## Impact

- New `agentlab/` FastAPI package and `agentlab_web/` React application.
- New local `.agentlab/sessions/` runtime data excluded from source control.
- Existing live runner is called as the source of true Browser Use/Chromium/SQLite outcomes.
