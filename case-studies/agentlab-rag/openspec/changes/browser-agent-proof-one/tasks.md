## 1. Repository and provenance setup

- [x] 1.1 Add the AgentLab Python project, local Browser Use source dependency, and development test command.
- [x] 1.2 Add the Browser Use provenance guard and Project Pack manifest for the audited commit.
- [x] 1.3 Add repository ignore rules that keep environments, evidence runs, and Browser Use local artifacts out of AgentLab commits.

## 2. Controlled procurement world

- [x] 2.1 Implement the minimal SQLite-backed procurement data model and deterministic task-state snapshot.
- [x] 2.2 Implement the login, product, purchase form, and confirmation pages required by `PROC-001`.
- [x] 2.3 Add baseline and DOM-change page variants plus tests for the stored purchase-request state.

## 3. Project Pack integration runtime

- [x] 3.1 Create the learner workspace configuration, tool policy, completion verifier, recovery policy, budget policy, and runner.
- [x] 3.2 Add a scripted Browser Use-compatible model for deterministic automated proof runs and an explicit live-model configuration boundary.
- [x] 3.3 Restrict Proof #1 tools and verify the runner never treats an Agent `done` response as business completion.

## 4. Evidence and deterministic scoring

- [x] 4.1 Implement task-success, false-success, step, call, latency, and versioned-cost scorers.
- [x] 4.2 Write a complete per-run evidence bundle with source revisions, trace, metrics, world states, and result.
- [x] 4.3 Add tests for failed and successful evidence bundles.

## 5. DOM-change proof

- [x] 5.1 Implement `PROC-001` baseline execution against the procurement world.
- [x] 5.2 Implement the DOM-change scenario and demonstrate deterministic baseline failure.
- [x] 5.3 Implement the repaired integration and demonstrate a verified before/after improvement with two evidence bundles.

## 6. Verification and handoff

- [x] 6.1 Run the focused test suite, provenance guard, and local proof command from a clean environment.
- [x] 6.2 Document the Proof #1 run command, evidence bundle contract, safety limits, and live-model prerequisite.
