## Why

`ai-data` is the next course module after DeepResearch. It teaches a different Agent pattern: Text-to-SQL over structured data, with schema recall, planning, SQL execution, SQL repair, and report generation.

## What Changes

- Add `python-ai-data/` without modifying `ai-data/`.
- Mirror Java DTOs, nodes, utilities, app/controller/init-controller shape.
- Use SQLite and in-memory schema recall for offline classroom demos instead of requiring MySQL and Elasticsearch.
- Keep OpenAI-compatible live config available for model-backed runs.

## Impact

- New Python module under `python-ai-data/`.
- New OpenSpec change under `openspec/changes/add-python-ai-data/`.
