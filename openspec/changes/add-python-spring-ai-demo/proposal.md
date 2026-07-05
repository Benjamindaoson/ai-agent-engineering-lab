## Why

`spring-ai-demo` starts the next course stage: framework-level Spring AI capabilities rather than a single business Agent. It demonstrates chat, streaming, system prompts, memory, advisors, structured output, embeddings, vector search, RAG, evaluation, tool calling, MCP, and metrics.

## What Changes

- Add `python-spring-ai-demo/` without modifying `spring-ai-demo/`.
- Mirror Java `AlarmRequest`, `CosineSimilarity`, `ZhouyuTools`, `ToolController`, `McpController`, `ZhouyuController`, and application wiring.
- Replace JDBC, Elasticsearch, Micrometer, and MCP server dependencies with stdlib in-memory equivalents for offline classroom use.
- Keep OpenAI-compatible live config available for model-backed runs.

## Impact

- New Python module under `python-spring-ai-demo/`.
- New OpenSpec change under `openspec/changes/add-python-spring-ai-demo/`.
