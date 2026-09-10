## Why

`false_ack_v1` proves that a page acknowledgement can be false, and the live runner correctly detects the missing SQLite record.  Its recovery follow-up currently cannot control the original Chromium session because the first agent run tears down the BrowserSession lifecycle that the follow-up expects.

## What Changes

- Preserve the existing Browser Use session across the recovery follow-up by using the pinned version's supported keep-alive and same-agent continuation lifecycle.
- Add a real Chromium continuation regression test proving that the retained session can read the current page and execute a subsequent browser action.
- Record bounded, secret-free continuation facts in new false-ack live evidence.
- Keep recovery limited to business-state facts and instructions; the model and Browser Use perform any second submission.
- Run a fresh DeepSeek Baseline ×5 and Fixed ×5 validation and publish aggregate, per-run evidence without replacing the earlier 1+1 evidence.

## Capabilities

### New Capabilities

- `live-browser-session-continuation`: Continue a verified failed live task in the same live Chromium BrowserSession without treating a page acknowledgement as final success.

### Modified Capabilities

<!-- No existing main OpenSpec capability is modified. -->

## Impact

- `project_packs/browser_agent_rescue/workspace/live.py` and `live_proof.py`
- Real Browser Use regression tests and live-validation tests
- New evidence is written to a new directory only; Proof #1 and historical live evidence remain immutable.

## Bounded recovery amendment

The retained BrowserSession design remains valid, but one follow-up is insufficient. The implementation now needs a SQLite-verified loop of at most two same-Agent continuations, each with an incremental cumulative step ceiling. The follow-up is restricted to facts: the purchase request is absent from SQLite, the original task is incomplete, and the browser session remains available. It must not prescribe clicks, a supplier, or a route.

The controlled world must expose four non-derived metrics: `form_load_count`, `submit_attempts`, `backend_write_attempts`, and `backend_write_successes`. A `FALSE-ACK-V1` first POST is an attempted but unsuccessful write; its second POST is an attempted and successful write. After deterministic verification, this amendment permits only a new Baseline ×1 and Fixed ×1 live check, with at most two additional Fixed runs only if Fixed-1 succeeds. It does not authorize another formal 5+5 run.
