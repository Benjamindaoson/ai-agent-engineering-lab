# AgentLab Engineering Docs

This folder contains the pre-implementation documents for AgentLab by TIAI.

## Documents

```text
00-mvp-v0.1-scope.md
Defines the first vertical slice and what is intentionally out of scope.

01-data-model.md
Defines the core database entities and seed data.

02-api-contract.md
Defines the FastAPI domain endpoints and payloads.

03-review-evidence-schema.md
Defines Review JSON, Evidence rules, and MVP rubric.

04-local-dev-test-plan.md
Defines local setup goals, mock mode, tests, and CI requirements.

05-data-flow-and-frontend-contract.md
Defines API read/write ownership, frontend fetching, async status, storage locations, and data handoff between services.

06-technology-selection.md
Defines the full v0.1 technology selection, alternatives considered, tradeoffs, and final architecture decision.
```

## Implementation Rule

Start with the smallest runnable vertical slice:

```text
Target Job
→ RAG Project Submission
→ Mock Review
→ Evidence
→ Skill Score
→ Hiring Passport
```

Do not start by building all pages or all projects.

## Technical Kernel

```text
Claude Agent SDK
+ Sandbox
+ Rubric Engine
+ Evidence Pipeline
```

Claude Agent SDK is the project-level review runtime. The full product kernel is the evidence-driven proof-of-work loop.
