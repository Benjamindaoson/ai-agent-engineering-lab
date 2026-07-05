# Agent Runner

This service will host Claude Agent SDK review execution.

Current v0.1 status:

```text
Mock review is implemented in apps/api/app/mock_review.py.
Claude Agent SDK integration is intentionally deferred until the mock vertical slice is stable.
```

Run mock mode:

```powershell
cd apps/agent-runner
..\..\.venv\Scripts\python -m agent_runner.main --mode mock
```

Boundary:

```text
Agent Runner returns structured ReviewResult JSON.
It does not write Evidence, Skill Scores, or Passport snapshots directly.
```
