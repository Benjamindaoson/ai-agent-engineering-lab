## Context

The pinned Browser Use commit ends every `Agent.run()` by stopping its Agent EventBus and calling `Agent.close()`.  With the current default `BrowserProfile.keep_alive=None`, `Agent.close()` calls `BrowserSession.kill()`.  `kill()` clears and replaces the BrowserSession EventBus; the replacement has no BrowserSession or watchdog handlers.  `Agent.add_new_task()` recreates only the Agent EventBus, so its next run reaches a BrowserStateRequestEvent with no DOM watchdog handler.

## Goals / Non-Goals

**Goals:**

- Reuse one BrowserSession and the currently open Chromium page across a business-state recovery follow-up.
- Use the pinned Browser Use continuation API (`Agent.add_new_task()` followed by `Agent.run()`) rather than a second Agent or a browser-state reconstruction layer.
- Prove the lifecycle with a deterministic real-browser test before live DeepSeek validation.
- Persist only stable, non-secret continuation facts in new evidence.

**Non-Goals:**

- Altering `FALSE-ACK-V1`, the procurement page, `PROC-001`, model, task prompt, recovery semantics, or Browser Use source.
- Performing browser, HTTP, or SQLite mutation from recovery code.
- UI work or new scenarios.

## Decisions

1. Construct the live BrowserProfile with `keep_alive=True`.
   This selects the pinned `Agent.close()` path that stops the BrowserSession EventBus with `clear=False`, retaining handlers and CDP/Chromium state; its resilient EventBus restarts on a later dispatch.  The default `None` selects `kill()`, which clears handlers and cannot be resumed.  Alternative: create a second BrowserSession or reattach CDP; rejected because it loses the original session and is not needed by the pinned API.

2. Keep one `Agent` instance and use `add_new_task()` for recovery.
   This is the continuation mechanism implemented in the pinned source.  Alternative: inject the old session into a new Agent; rejected because it adds a second lifecycle owner and is not the documented source-level continuation path.

3. Add test-facing lifecycle facts from AgentLab, using a generated UUID run id rather than Python object identity.
   Evidence records only session reuse, continuation progress and outcome, current-page-independent counters, and business-state results.  It excludes API keys, cookies, credentials, page body, and debug handler inventories.

4. Treat the official validation as ten independent worlds and aggregate observed metrics only from successful experiment attempts.
   Each attempt receives a fresh FastAPI process, SQLite database, false-ack state, BrowserSession run id, and browser cleanup.  Infrastructure exceptions are retained in a root-level count and retried until five valid runs per mode are available; they are not task failures.

5. Use a maximum of two recovery rounds and increase the cumulative Agent step ceiling by `MAX_RECOVERY_STEPS` per round.
   Browser Use retains its cumulative Agent step counter across `add_new_task()` calls. The old recovery call used a ceiling of five, so a three-to-four-step initial run often left one or two actions for recovery. Round one uses `MAX_INITIAL_STEPS + MAX_RECOVERY_STEPS`, and round two uses `MAX_INITIAL_STEPS + 2 * MAX_RECOVERY_STEPS`. SQLite is checked after every round; success stops immediately, and failure after round two is recorded as exhausted.

6. Separate observed metrics at their direct boundary rather than deriving them from page visits.
   `form_load_count` increments in the purchase-form GET. `submit_attempts` increments at the valid `/purchase` POST boundary. `backend_write_attempts` increments when that POST logically attempts an SQLite write, including the intentionally failed first `FALSE-ACK-V1` attempt. `backend_write_successes` increments only after `ProcurementStore.create_purchase_request` returns.

The recovery helper only creates a fact-only instruction and asks the existing Agent to run. It has no browser, HTTP, or SQLite mutation code. The live runner owns world-state retrieval and verification.

## Risks / Trade-offs

- [Pinned Browser Use continuation behavior changes upstream] → lock verification to the audited commit and test real Chromium.
- [Model may still choose not to resubmit] → report the observed live outcome without changing model instructions or world behavior.
- [A retained browser leaks if a run aborts] → retain the existing outer `finally: await browser.close()` as the sole terminal cleanup.
