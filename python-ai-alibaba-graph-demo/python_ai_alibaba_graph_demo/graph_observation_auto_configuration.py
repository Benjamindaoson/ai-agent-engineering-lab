from __future__ import annotations

from .graph_observation_properties import GraphObservationProperties
from .simple_graph import CompileConfig


class GraphObservationAutoConfiguration:
    def __init__(self, properties: GraphObservationProperties | None = None) -> None:
        self.properties = properties or GraphObservationProperties()

    def observation_graph_compile_config(self) -> CompileConfig:
        listeners = ["graphObservationLifecycleListener"] if self.properties.enabled else []
        return CompileConfig(
            observation_enabled=self.properties.enabled,
            lifecycle_listeners=listeners,
        )
