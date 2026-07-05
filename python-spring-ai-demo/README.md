# python-spring-ai-demo

Python counterpart of the Java `spring-ai-demo` module.

## Run order for class

```powershell
cd python-spring-ai-demo
python -m unittest discover -s tests -v
python -m python_spring_ai_demo.self_check
python -m python_spring_ai_demo.offline_demo
python -m python_spring_ai_demo
```

The first three commands are offline. JDBC chat memory, Elasticsearch vector store, Micrometer, and MCP server calls are represented by in-memory or fake-client equivalents.

## Provider config

```powershell
$env:PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-key"
$env:LLM_NAME="deepseek-chat"
```

## Class storyline

1. Chat, stream, SSE, system prompt.
2. Chat memory and advisor.
3. Structured output and embedding.
4. Store/search/RAG/evaluation.
5. Tool calling and user-controlled tool execution.
6. MCP prompt/resource/tool callback shape.
