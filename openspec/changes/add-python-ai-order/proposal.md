## Why

`ai-order` is the transactional business-agent module in the course story. It shows how an Agent recommends products, creates orders, gates payment behind human confirmation, handles refunds, and searches customer-service knowledge.

## What Changes

- Add `python-ai-order/` without modifying `ai-order/`.
- Mirror Java controllers, DTOs, entities, enums, parser, service, tool, and application wiring.
- Replace Elasticsearch vector stores with in-memory keyword search for offline classroom use.
- Keep OpenAI-compatible live config available for model-backed runs.

## Impact

- New Python module under `python-ai-order/`.
- New OpenSpec change under `openspec/changes/add-python-ai-order/`.
