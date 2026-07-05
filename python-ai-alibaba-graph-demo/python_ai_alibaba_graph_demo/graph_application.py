from __future__ import annotations

from dataclasses import dataclass

from .graph_config import GraphConfig, create_graph_config
from .graph_controller import GraphController
from .simple_graph import MemorySaver


@dataclass
class GraphApplication:
    graph_config: GraphConfig
    controller: GraphController
    memory_saver: MemorySaver


def create_application() -> GraphApplication:
    graph_config = create_graph_config()
    controller = GraphController(
        simple_state_graph=graph_config.simple_state_graph(),
        conditional_state_graph=graph_config.conditional_state_graph(),
        hello_state_graph=graph_config.hello_state_graph(),
        interrupt_before_state_graph=graph_config.interrupt_before_state_graph(),
        interrupt_state_graph=graph_config.interrupt_state_graph(),
        parallel_executor_state_graph=graph_config.parallel_executor_state_graph(),
        sub_state_graph=graph_config.sub_state_graph(),
        memory_saver=graph_config.memory_saver,
    )
    return GraphApplication(graph_config, controller, graph_config.memory_saver)


def main() -> None:
    app = create_application()
    print(app.controller.simple("AI Agent"))
    print(app.controller.conditional("写Java代码"))


if __name__ == "__main__":
    main()
