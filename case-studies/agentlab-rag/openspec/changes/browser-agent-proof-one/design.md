## Context

The Browser Use audit passed at commit `32601887cfbc9f4f1e3cad3e2b678e56aeaeaae4`. Its Agent, Chromium/CDP session, tools, action history, token accounting, and browser traces are useful runtime capabilities, but Browser Use does not provide AgentLab's controlled business world, deterministic business scoring, versioned cost policy, or cross-run evidence chain.

Proof #1 is deliberately narrow: one procurement site, `PROC-001`, one DOM-change scenario, and one before/after repair. Browser Use remains a separately versioned source checkout under `sources/browser-use`; AgentLab code never modifies it.

## Goals / Non-Goals

**Goals:**

- Run a real Browser Use session against a local controlled procurement web application.
- Make task completion depend on the purchase-request state, not an Agent `done` response.
- Persist an immutable-looking run bundle with exact input, source revisions, trace, metrics, and before/after world states.
- Make the initial DOM-change failure reproducible and repairable by changing only the learner integration layer.
- Keep all secrets out of the Browser Use process and use a versioned local price card for cost calculation.

**Non-Goals:**

- A general GitHub-to-Project-Pack converter, multi-user UI, browser IDE, agent mentor, task graph, prompt-injection scenario, or cost-optimization scenario.
- Editing or patching Browser Use source code.
- Claiming that a scripted acceptance run measures LLM intelligence. A live model run is an additional demonstration once a model credential is deliberately configured.

## Decisions

### Separate product code from the pinned runtime

AgentLab owns `project_packs/`, `controlled_world/`, `runtime/`, `evidence/`, and `tests/`. Browser Use remains under `sources/browser-use` at the audited commit. The AgentLab Python project references that local source through `uv` rather than copying it into product modules.

Alternative: fork Browser Use and teach changes inside its internals. Rejected because it couples the product to a large moving upstream codebase and turns Project Pack tasks into upstream maintenance.

### Use one FastAPI procurement service with SQLite

The controlled world is a local FastAPI service backed by a temporary SQLite database. It exposes the five small user-facing routes from the PRD and an internal state snapshot endpoint used only by deterministic scorers. The first task creates a purchase request for `SKU-1024` with quantity 20 and the cheapest valid supplier.

Alternative: build a React app plus separate API. Rejected because the proof needs a real dynamic browser surface, not a production frontend stack.

### Keep learner changes inside a narrow integration layer

The pack's `workspace/` contains `agent_config.py`, `tool_policy.py`, `completion.py`, `recovery.py`, `budget.py`, and `runner.py`. The runner constructs Browser Use's `Agent`, `BrowserProfile`, and restricted `Tools`, executes it, and passes execution facts to scorers. `completion.py` checks controlled world state; it never trusts `AgentHistory.is_successful()` alone.

Alternative: ask learners to change `browser_use/agent/service.py` or `browser_use/tools/service.py`. Rejected because those modules are too broad for a bounded Project Pack and would mutate third-party source.

### Make proof acceptance deterministic while retaining a real browser runtime

The automated proof path uses a local scripted chat model that emits a fixed sequence of Browser Use actions. Browser Use still launches Chromium, reads the actual DOM, invokes registered tools, and changes the actual procurement database. This prevents LLM randomness from invalidating a reproducibility claim. The runner also supports a configured live Browser Use-compatible model for the later presentation run.

Alternative: use an LLM judge or a live LLM for all acceptance. Rejected because neither produces repeatable proof.

### Treat DOM change as a runtime variant

The procurement service serves a V1 one-submit workflow and a V2 workflow where the first submit opens a second confirmation page. In V2, no purchase request exists until that confirmation is submitted. The baseline integration trusts the Agent's `done` signal; the repaired `recovery.py` checks business state and completes the pending confirmation. The scenario is selected through a declared scenario file and recorded in every run bundle.

Alternative: describe the DOM change in task text. Rejected because it produces no execution evidence.

### Store evidence as a directory bundle

Each run writes `evidence/runs/<run-id>/` with metadata, task, scenario, submission revision, JSONL trace, metrics, world state before/after, and result. Files are written only after the corresponding fact is collected. Graph storage is deferred; the bundle IDs form the initial evidence relation.

### Freeze pricing locally

`pricing.yaml` supplies a version and per-million-token rates. The runner persists raw token counts and calculates estimated cost with that card. Browser Use's mutable remote pricing cache is not an evidence source.

### Defense in depth for the controlled world

The runner restricts Browser Use to the controlled host and removes file-reading, file-writing, search, and upload actions for Proof #1. It uses no sensitive data. Container isolation and deny-by-default network policy remain a subsequent deployment task; local development does not claim production sandbox isolation.

## Risks / Trade-offs

- [A local hostname can resolve to loopback, which conflicts with generic IP blocking] → Use a dedicated controlled hostname in the Browser allowlist and scope network isolation to the later container runtime; do not enable blanket IP blocking in the local proof without an explicit resolver design.
- [Live model calls need a credential and are stochastic] → Tests use the scripted model; live baseline evidence is marked unavailable until a credential is intentionally supplied.
- [The DOM variant might teach selector patching rather than reliability] → V2 changes timing and nesting but preserves semantic labels; the repair must use robust state/retry logic plus world-state verification.
- [Evidence files could contain secrets] → Proof #1 has no real secrets; traces redact configured sensitive values and the run writer rejects unexpected secret-bearing configuration fields.
- [The vendor clone contains local development artifacts] → AgentLab never commits files under `sources/browser-use`; a provenance check verifies its exact HEAD before each pack run.

## Migration Plan

1. Preserve the current Browser Use audit checkout at `sources/browser-use` and verify its HEAD before creating code.
2. Add the AgentLab root Python project and the smallest controlled procurement service.
3. Add the project pack, deterministic scorer, run bundle writer, and scripted proof test.
4. Run baseline and repaired DOM-change evidence bundles locally.
5. Add a live-model configuration only after the deterministic proof passes; a missing credential is a visible, non-fatal demo configuration state.

Rollback is deletion of AgentLab-owned uncommitted files only; Browser Use remains untouched and independently clonable from its pinned commit.

## Open Questions

- Which model provider and fixed model/version will be used for the live demonstration? This does not block deterministic Proof #1.
- Will the presentation environment map the controlled hostname through Docker DNS or a local browser resolver rule? This is required before containerized deployment, not before the local proof.
