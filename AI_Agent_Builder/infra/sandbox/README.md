# AgentLab Sandbox

This folder contains the future Docker sandbox baseline.

Current v0.1 behavior:

```text
The API records sandbox_runs with status=skipped.
No learner code is executed yet.
```

Build the baseline image:

```powershell
docker build -t agentlab-sandbox:local infra/sandbox
```

Security rules for real execution:

```text
no production secrets
restricted network
restricted CPU and memory
timeout every command
mount only current submission workspace
persist stdout/stderr as artifacts
destroy container after run
```
