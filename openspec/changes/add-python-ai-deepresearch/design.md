## Design

`python-ai-deepresearch` mirrors the Java module:

- `dto/plan.py`, `dto/step.py`
- `node/coordinator_node.py`, `planner_node.py`, `researcher_node.py`, `reporter_node.py`
- `util/constant.py`, `util/prompt_util.py`
- `deep_research_application.py`, `deep_research_controller.py`
- `observation_configuration.py`, `parallel_streaming_example.py`

The workflow keeps the Java state keys: `input`, `coordinatorResult`, `plannerResult`, `researcherResult_0`, and `reporterResult`.

The Python graph is deliberately small. It runs coordinator first, conditionally runs planner, executes researcher nodes for each planned step, and then runs reporter. Parallel execution uses `ThreadPoolExecutor`, matching the Java module's intent without introducing a graph framework dependency.

## Verification

Tests use fake clients and fake search tools. They cover parsing, routing, node behavior, full workflow, observation events, and parallel streaming summary.
