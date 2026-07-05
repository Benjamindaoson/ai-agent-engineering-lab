## Design

`python-ai-manus` mirrors `ai-manus/src/main/java/com/zhouyu`:

- `agent/`: `BaseAgent`, `ToolCallAgent`, `ManusAgent`
- `model/`: message, role, tool-call, model config/response, OpenAI-compatible client, relevance filters
- `tools/`: tool interface, base helper, result, collection
- `tools/impl/`: file read/write, Tavily search, browser, Docker sandbox, sandbox tool

The model client uses the existing course convention: `PROVIDER=dashscope|deepseek`, `DASHSCOPE_API_KEY`, `DEEPSEEK_API_KEY`, and `LLM_NAME`.

The browser tool treats Playwright as optional. If it is not installed, it returns a clear tool error instead of breaking module import. Docker sandbox uses the Docker CLI because it is the smallest Python equivalent of the Java Docker client for this lesson.

## Verification

Offline tests cover message serialization, model config, tool schemas, file tools, sandbox command building, relevance filtering, and one fake tool-call agent loop.
