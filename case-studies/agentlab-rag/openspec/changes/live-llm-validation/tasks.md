## 1. Live runtime

- [x] 1.1 Add a metered, provider-configurable OpenAI-compatible model factory and validate selected-provider missing-key behavior.
- [x] 1.2 Add a live initial Agent phase and an optional recovery continuation with business-state feedback, without changing deterministic Proof #1 behavior.
- [x] 1.3 Enforce per-run step and output-token ceilings.

## 2. Evidence and reporting

- [x] 2.1 Persist provider, model, token, cost, latency, trace, and database-state facts in separate evidence bundles without API keys.
- [x] 2.2 Add a provider-selectable five-plus-five live runner and Chinese comparison report.

## 3. Verification

- [x] 3.1 Add non-billing tests for provider configuration, credential isolation, preflight failures, pricing, recovery identity, and evidence calculation.
- [x] 3.2 Run tests, pinned-runtime validation, a one-run live smoke test, and the five-plus-five validation.
- [x] 3.3 Document the live-model boundary and report the observed results without conflating them with deterministic Proof #1 or general model ability.
