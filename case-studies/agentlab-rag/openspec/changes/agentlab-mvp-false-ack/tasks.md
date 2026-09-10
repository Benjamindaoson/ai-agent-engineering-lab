## 1. Product contracts and session safety

- [x] 1.1 Add failing tests for session creation, workspace isolation, allowlisted reads/writes, path traversal, trial profile, fixed assignment, evidence/replay, and secret-safe payloads.
- [x] 1.2 Implement the session/task/evidence domain and FastAPI APIs.

## 2. Real run integration

- [x] 2.1 Add a background job manager that starts the existing DeepSeek/Browser Use/Chromium/SQLite runner, records evidence, supports status polling and cancellation, and derives acceptance programmatically.
- [x] 2.2 Add fixed reliability, prompt-injection, and cost-budget task contracts.

## 3. Web product

- [x] 3.1 Create the React TypeScript Vite application with Monaco and the six Chinese product views.
- [x] 3.2 Connect trial, workspace, run, result, delivery, and replay APIs with responsive product styling.

## 4. Delivery

- [x] 4.1 Add README, DEMO, startup command, frontend typecheck/build, backend tests, strict OpenSpec validation, and browser Golden Path verification.
- [x] 4.2 Commit the MVP and create `agentlab-mvp-v1` only after the Golden Path succeeds.
