## Why

`ai-weekly-report` is the next business automation module after `ai-data`. It teaches how an Agent uses tools to read Git history, generate a weekly report, ask for human confirmation, and send email.

## What Changes

- Add `python-ai-weekly-report/` without modifying `ai-weekly-report/`.
- Mirror Java `GitTool`, `EmailTool`, `WeeklyReportController`, and `WeeklyReportApplication`.
- Keep classroom demos offline-safe by default: Git uses a local repository, and email defaults to dry-run unless SMTP is explicitly enabled.
- Keep OpenAI-compatible live config available for model-backed report generation.

## Impact

- New Python module under `python-ai-weekly-report/`.
- New OpenSpec change under `openspec/changes/add-python-ai-weekly-report/`.
