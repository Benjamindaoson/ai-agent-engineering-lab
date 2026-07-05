from __future__ import annotations

from ..simple_graph import Interruption


class InterruptableNodeAction:
    def apply(self, state: dict[str, object], config=None) -> dict[str, object]:
        return {"node2Result": ["我是节点2"]}

    def interrupt(self, node_id: str, state: dict[str, object], config) -> dict[str, object]:
        if "humanFeedbackResult" not in state:
            return {"interrupted": True, "node": node_id, "message": "等待用户输入..."}
        return {"interrupted": False}

    def __call__(self, state: dict[str, object], config=None) -> dict[str, object]:
        if "humanFeedbackResult" not in state:
            state["_next_node"] = "node2"
            raise Interruption("node2", state)
        return self.apply(state, config)
