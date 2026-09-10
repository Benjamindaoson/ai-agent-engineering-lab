## Why

AgentLab must prove that a real Agent system can be improved through code changes and that the improvement can be reproduced from runtime evidence. The first proof uses a pinned Browser Use runtime and a controlled procurement website, rather than a polished learning UI or an LLM-generated claim of success.

## What Changes

- Establish the AgentLab repository boundary: Browser Use is a pinned, read-only upstream runtime under `sources/browser-use`.
- Add the first `browser-agent-rescue` Project Pack with a learner-editable integration layer, one controlled procurement application, and task `PROC-001`.
- Add deterministic world-state scoring and a portable per-run evidence bundle.
- Add one repeatable DOM-change scenario that turns the baseline into a failure and verifies an integration-layer repair.
- Record model usage with a versioned local price card instead of mutable remote price data.

## Capabilities

### New Capabilities

- `project-pack-runtime`: Loads the pinned Browser Use runtime and runs a learner-owned integration layer against a declared task and scenario.
- `controlled-procurement-world`: Provides the minimal purchasing workflow and deterministic business-state API required by `PROC-001`.
- `reproducible-evidence-bundle`: Stores the task, scenario, source revisions, traces, metrics, world states, and result for every run.
- `dom-change-improvement`: Reproduces a controlled page-change failure and verifies a before/after engineering improvement.

### Modified Capabilities

None.

## Impact

New Python runtime, test, and project-pack files will be added under the AgentLab repository. Browser Use remains an unmodified upstream source at commit `32601887cfbc9f4f1e3cad3e2b678e56aeaeaae4`; it supplies the real browser Agent runtime but is not the learner-editable product code.
