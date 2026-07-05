# python-ai-alibaba-graph-demo

A Python teaching project for graph workflows: nodes, routing, checkpointing, interruption, and resume.

## Run order for class

```powershell
cd python-ai-alibaba-graph-demo
python -m unittest discover -s tests -v
python -m python_ai_alibaba_graph_demo.self_check
python -m python_ai_alibaba_graph_demo.offline_demo
python -m python_ai_alibaba_graph_demo
```

The first three commands are offline. Spring Boot, Reactor, Micrometer, OpenTelemetry, DashScope, and Alibaba graph runtime are represented by small in-memory equivalents.

## Provider config

```powershell
$env:PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-key"
$env:LLM_NAME="deepseek-chat"
```

## Class storyline

1. Simple graph: title node -> content node.
2. Stream output from the content node.
3. Conditional graph: route to poem or code.
4. Thread memory and checkpoint saver.
5. Interrupt before a node, then resume.
6. Interrupt inside a node, then resume.
7. Parallel branch completion and subgraph state merge.
