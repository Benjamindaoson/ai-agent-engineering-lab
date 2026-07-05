# python-agentscope-demo

A Python teaching project for AgentScope-style capabilities: agents, toolkit, hooks, memory, pipelines, skills, RAG, MCP, vision, and Studio entries.

## Run order for class

```powershell
cd python-agentscope-demo
python -m unittest discover -s tests -v
python -m python_agentscope_demo.self_check
python -m python_agentscope_demo.offline_demo
python -m python_agentscope_demo
```

The first three commands are offline. AgentScope, DashScope live calls, Mem0, Elasticsearch, MCP server, Studio server, and image model calls are represented by deterministic Python equivalents.

## Class storyline

1. Start with a basic ReAct-style agent and deterministic model response.
2. Add tools, preset parameters, injected user context, and tool groups.
3. Show tool streaming and hooks, then pause sensitive tools for human confirmation.
4. Add short memory, JSONL session persistence, message hub, and pipelines.
5. Demonstrate structured output, skills, RAG, MCP, vision, image generation, Studio, and planning as offline classroom entries.
6. Use `model_config.py` only when moving from offline demos to live OpenAI-compatible providers.
