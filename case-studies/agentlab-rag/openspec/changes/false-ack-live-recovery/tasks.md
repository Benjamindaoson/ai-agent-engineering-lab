## 1. Lifecycle regression

- [x] 1.1 Add a deterministic real-Chromium test that proves one keep-alive Agent can continue through the original BrowserSession after its first run ends.
- [x] 1.2 Run the isolated continuation test and confirm it fails before the live runner lifecycle change.

## 2. Live continuation

- [x] 2.1 Configure the live BrowserSession for the pinned keep-alive same-Agent continuation mechanism.
- [x] 2.2 Add stable, secret-free continuation and business-state facts to the live run and evidence bundle.
- [x] 2.3 Add unit tests for baseline non-continuation, fixed continuation facts, recovery boundary, and evidence safety.

## 3. Verification

- [x] 3.1 Run the real Chromium continuation test and relevant pytest suite.
- [x] 3.2 Validate the OpenSpec change strictly.
- [x] 3.3 Run DeepSeek Baseline ×1 and Fixed ×1 against `FALSE-ACK-V1` in a new evidence directory, only after the continuation test passes.

## 4. Final independent validation

- [x] 4.1 Add final-run evidence fields and aggregation for AgentLab commit, steps, averages, and infrastructure-error count.
- [x] 4.2 Test final aggregation without live model calls.
- [x] 4.3 Run fresh DeepSeek Baseline ×5 and Fixed ×5 evidence in `evidence/live-false-ack-final-v2/`.
- [x] 4.4 Run pytest and strict OpenSpec validation; commit final code and evidence. The local `proof-live-recovery-passed` tag is not eligible because Fixed produced only 2/5 SQLite-confirmed successes.

## 5. Bounded recovery and accurate metrics

- [x] 5.1 Add failing deterministic tests for true POST/write metrics and the false-ack first/second submit states.
- [x] 5.2 Add failing deterministic tests for a maximum-two-round SQLite-verified same-Agent recovery loop, including exhaustion and immediate-success stop behavior.
- [x] 5.3 Implement the four world-state counters without changing `FALSE-ACK-V1` behavior.
- [x] 5.4 Implement fact-only bounded recovery on the retained Agent and BrowserSession, with per-round SQLite verification and evidence facts.
- [x] 5.5 Update evidence aggregation and secret-free evidence tests for the new counters and recovery facts.
- [x] 5.6 Run the focused and full pytest suites plus strict OpenSpec validation.
- [x] 5.7 Run new-evidence Baseline ×1 and Fixed ×1, then at most Fixed ×2 if the first Fixed run succeeds; commit code and evidence without rerunning formal 5+5.

## 6. Frozen formal stability validation

- [x] 6.1 Add a deterministic report test for normal-Chinese explanation and recovery-exhaustion reporting.
- [x] 6.2 Run five valid DeepSeek Baseline and five valid DeepSeek Fixed `FALSE-ACK-V1` worlds into `evidence/live-false-ack-final-v3/`, preserving all frozen settings and historical evidence.
- [x] 6.3 Run full pytest and strict OpenSpec validation; commit the formal evidence and create `proof-live-recovery-passed` only when the frozen threshold is met.
