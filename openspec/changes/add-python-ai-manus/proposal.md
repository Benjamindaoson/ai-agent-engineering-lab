## Why

`ai-manus` is the next module after the minimal ReAct demo. A Python version lets the course show the upgrade from a single hand-written tool loop to a Manus-style agent with OpenAI-compatible tool calls, memory, relevance filtering, browser/search/file tools, and a Docker sandbox.

## What Changes

- Add `python-ai-manus/` without modifying `ai-manus/`.
- Keep Python files close to the Java package/class layout for side-by-side teaching.
- Implement model, memory, tool-call agent, Manus agent, and the five original tool families.
- Keep local self-checks offline by using fake model responses and local file/tool execution.

## Impact

- New Python module under `python-ai-manus/`.
- New OpenSpec change under `openspec/changes/add-python-ai-manus/`.
