## Design

`python-spring-ai-demo` mirrors the Java module:

- `alarm_request.py`: tool parameter object.
- `cosine_similarity.py`: vector math helper.
- `zhouyu_tools.py`: current-time, alarm, and save-code tools.
- `tool_controller.py`: automatic and user-controlled tool calling demos.
- `mcp_controller.py`: MCP tool, prompt, and resource demo using injected fake clients/providers offline.
- `zhouyu_controller.py`: chat, stream, SSE, system prompt, memory, advisor, structured output, embedding, store/search/RAG, RAG advisor, evaluation, and metric demos.
- `simple_ai.py`: tiny stdlib equivalents for documents, embeddings, vector store, and evaluation response.

The Python port keeps external integrations injectable. Offline tests and demos use fake chat clients and in-memory vector search.

## Verification

Tests cover cosine similarity, text splitting, chat/memory/output/RAG/evaluation, tool calling, and MCP prompt/resource flows.
