## Design

The Python port intentionally does not depend on the Java AgentScope runtime. Instead, it mirrors the concepts needed for classroom demonstrations:

- `core.py` provides `Msg`, `FakeChatModel`, `ReActAgent`, `Toolkit`, hooks, memory/session JSONL persistence, `MsgHub`, and pipeline helpers.
- Small files such as `tool_demo.py`, `short_memory_demo.py`, and `fanout_pipeline_demo.py` map to the Java class names.
- `tools/`, `hooks/`, `context/`, and `product/` mirror the Java package structure.
- `demos.py` groups external-service style entries such as RAG, MCP, Vision, image generation, and Studio into deterministic offline functions.

Live model calls are intentionally separated behind `model_config.py` and are not required by tests or classroom smoke demos.
