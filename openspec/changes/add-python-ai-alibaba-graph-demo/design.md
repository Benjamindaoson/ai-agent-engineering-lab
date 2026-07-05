## Design

`python-ai-alibaba-graph-demo` mirrors the Java module:

- `graph_application.py`: creates graph config, memory saver, memory store, and controller.
- `graph_config.py`: builds simple, conditional, hello, interrupt-before, interrupt, parallel, and subgraph demos.
- `graph_controller.py`: Python methods matching Java controller endpoints.
- `simple_graph.py`: small in-memory graph, memory, store, interruption, and compile config primitives.
- `blog/title_node_action.py` and `blog/content_node_action.py`: deterministic replacements for model-backed blog generation nodes.
- `interrupt/interruptable_node_action.py`: node-level interruption behavior.
- `graph_observation_*`: tiny observation config equivalents.

The Python module stays offline-first. Streams are represented as lists of strings.

## Verification

Unit tests cover provider config, simple graph, stream output, conditional routing, memory/checkpoints, interrupt/resume, parallel executor state, subgraph merge, node actions, and observation config.
