## Why

`ai-consultation` is the vertical RAG consultation module in the course story. It demonstrates how an Agent uses department knowledge, conversation history, and a registration tool to guide a user toward a department without pretending to diagnose disease.

## What Changes

- Add `python-ai-consultation/` without modifying `ai-consultation/`.
- Mirror Java `ConsultationController`, `ConsultationTools`, `ConsultationQueryExpander`, `DepartmentScraper`, `DepartmentSummaryJob`, `DepartmentSummaryVectorStoreJob`, and application wiring.
- Replace Elasticsearch, JDBC memory, and Playwright smoke requirements with offline stdlib equivalents for classroom use.
- Keep OpenAI-compatible live config available for model-backed runs.

## Impact

- New Python module under `python-ai-consultation/`.
- New OpenSpec change under `openspec/changes/add-python-ai-consultation/`.
