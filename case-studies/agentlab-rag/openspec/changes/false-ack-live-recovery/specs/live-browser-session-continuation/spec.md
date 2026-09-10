## ADDED Requirements

### Requirement: Preserve live BrowserSession for recovery continuation
When a live fixed run detects that an agent-reported completion lacks the expected SQLite purchase request, the system SHALL retain the original BrowserSession and Chromium page while it asks the same Agent instance to continue.

#### Scenario: False acknowledgement triggers continuation
- **WHEN** the first live submission reports done but SQLite lacks the expected purchase request
- **THEN** the fixed run SHALL set recovery-triggered facts and call the pinned same-Agent continuation mechanism without creating or closing a replacement BrowserSession

#### Scenario: Baseline does not continue
- **WHEN** a baseline live submission reports done but SQLite lacks the expected purchase request
- **THEN** the run SHALL record false success and SHALL NOT start a continuation

### Requirement: Demonstrate same-session browser continuity
The project SHALL have a real Chromium regression test that ends a first Agent phase, retains the BrowserSession, and proves the continuation can read the current page and execute a subsequent browser action through the same stable session run id.

#### Scenario: Retained browser can be read and acted upon
- **WHEN** a keep-alive Agent phase has ended without closing Chromium
- **THEN** a same-Agent continuation SHALL read the current page state and perform a browser action using the original BrowserSession

### Requirement: Evidence records bounded continuation facts
New false-ack live evidence SHALL record `browser_session_reused`, `browser_session_run_id`, `recovery_triggered`, `recovery_reason`, `resume_started`, `resume_completed`, `submit_attempts`, `page_reported_success`, `business_state_success`, `task_success`, and `false_success` without recording API keys, cookies, credentials, or Python object addresses.

#### Scenario: Fixed live evidence is secret-free and auditable
- **WHEN** a fixed false-ack live run writes its result bundle
- **THEN** the result SHALL expose the required continuation and outcome facts while excluding secrets and browser-private content

### Requirement: Publish independent final validation results
The system SHALL write five valid Baseline and five valid Fixed `FALSE-ACK-V1` DeepSeek runs to a new evidence root. Each valid run SHALL use a fresh controlled world and BrowserSession run id, and final success SHALL be derived from the SQLite business state only.

#### Scenario: Infrastructure errors are not task failures
- **WHEN** a provider, authentication, rate-limit, or unrelated network failure prevents a live attempt from completing
- **THEN** the report SHALL count it as an infrastructure error and SHALL NOT count it as a Baseline or Fixed task result

#### Scenario: Final report aggregates all valid runs
- **WHEN** five valid runs exist for each mode
- **THEN** `report.json` and `report.html` SHALL present per-run outcomes and averages for submissions, steps, model calls, duration, and estimated cost

### Requirement: Recovery uses a bounded SQLite-verified loop
When a fixed live run detects that an agent-reported completion lacks the expected SQLite purchase request, the system SHALL perform at most two same-Agent recovery rounds. After every continuation it SHALL re-check SQLite and stop immediately upon a correct purchase request; otherwise it SHALL mark recovery exhausted after the second failed round.

#### Scenario: First recovery fails and second recovery is attempted
- **WHEN** the first same-Agent continuation leaves SQLite without the expected purchase request
- **THEN** the system SHALL send a second fact-only continuation through the original BrowserSession before declaring exhaustion

#### Scenario: A recovery creates the expected purchase request
- **WHEN** SQLite contains the expected purchase request after a recovery round
- **THEN** the system SHALL stop further recovery and record `recovery_rounds=1`, `recovery_success=true`, and `recovery_exhausted=false` when it succeeded on the first round

### Requirement: World-state metrics distinguish browser actions and writes
The controlled procurement world SHALL expose `form_load_count`, `submit_attempts`, `backend_write_attempts`, and `backend_write_successes`. Form loads SHALL increment only on the purchase-form GET; submits SHALL increment only on valid purchase-form POST; write attempts SHALL increment before each intended SQLite write; write successes SHALL increment only after a successful SQLite write.

#### Scenario: False acknowledgement followed by a real retry
- **WHEN** `FALSE-ACK-V1` receives its first valid POST
- **THEN** the world state SHALL show `submit_attempts=1`, `backend_write_attempts=1`, and `backend_write_successes=0` with no purchase record
- **WHEN** it receives a second valid POST
- **THEN** the world state SHALL show `submit_attempts=2`, `backend_write_attempts=2`, and `backend_write_successes=1` with the expected purchase record
