## 1. Connector safety and preflight

- [x] 1.1 Add a tested model connector module for normalized public HTTPS OpenAI-compatible endpoints and non-secret provenance.
- [x] 1.2 Add a tested bounded preflight that checks model access and Chat Completions response shape without recording a key.

## 2. Real-run integration

- [x] 2.1 Extend the frozen live adapter's provider configuration to accept an in-memory custom API key while preserving the official default provider path.
- [x] 2.2 Pass validated connector data through the run manager and live executor without persisting a key, and write open-run provenance and untrusted cost state to Evidence.

## 3. Product API and UI

- [x] 3.1 Add session-scoped connector preflight and run-start API contracts with secret-safe error responses.
- [x] 3.2 Add an official/custom model selector, preflight feedback, external-model disclosure, and open-run provenance display to the workbench.

## 4. Verification and documentation

- [x] 4.1 Add API, run-manager, connector, and UI source-contract tests for custom connector behavior and key non-persistence.
- [x] 4.2 Run the Python suite, frontend typecheck/build, strict OpenSpec validation, API health check, and browser smoke flow.
