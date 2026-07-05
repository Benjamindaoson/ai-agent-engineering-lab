class ObservationRegistry:
    def __init__(self):
        self.events: list[dict] = []

    def on_tool_start(self, tool_name: str, arguments: dict) -> None:
        self.events.append({"event": "start", "tool": tool_name, "arguments": arguments})

    def on_tool_stop(self, tool_name: str, result) -> None:
        self.events.append({"event": "stop", "tool": tool_name, "result": result})
