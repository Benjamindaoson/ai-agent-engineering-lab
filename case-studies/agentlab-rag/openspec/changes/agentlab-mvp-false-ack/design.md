## Context

The frozen proof stack already provides a controlled FastAPI procurement world, a real DeepSeek/Browser Use/Chromium live runner, SQLite business verification, and portable evidence bundles. The product must expose those facilities without allowing users to alter scorers, upstream source, or host files.

## Decisions

1. Use one FastAPI process for the product API and static frontend. A `RunManager` owns in-process asyncio jobs; polling replaces queues and realtime infrastructure.
2. Create a session workspace from generated, allowlisted configuration files. The backend parses only safe Python literal assignments, never imports or executes learner code. Those settings choose fixed recovery and budget contracts for a real existing live runner.
3. Persist all session metadata, run bundles, screenshots, reports, and diffs beneath `.agentlab/sessions/<id>/`. The UI reads backend APIs; evidence remains the factual basis for outcomes.
4. Use a fixed task graph. The trial maps the lowest of reliability, safety, and efficiency scores to a deterministic task order.
5. Add prompt-injection and cost contracts as controlled scenario metadata and programmatic post-run checks. No LLM judge evaluates safety or acceptance.
6. Replay only reads allowlisted historical evidence roots and labels them explicitly.

## Risks

- Live runs require `DEEPSEEK_API_KEY`, network access, and a local Chromium-capable environment. A missing key is an infrastructure result and replay remains usable.
- The default live runner remains stochastic and can be expensive; the product surfaces measured cost and exposes a cancellation state, but does not claim production-grade scheduling.
- Windows browser cleanup warnings remain non-blocking because changing Browser Use lifecycle is out of scope.
