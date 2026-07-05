class ZhouyuModelHook:
    def get_name(self) -> str:
        return "zhouyuModelHook"

    def before_model(self, state: dict[str, object]) -> dict[str, object]:
        messages = state.get("messages", [])
        if len(messages) > 10:
            return {"messages": messages[-10:]}
        return {}

    def after_model(self, state: dict[str, object]) -> dict[str, object]:
        state.setdefault("events", []).append("Model 调用结束")
        return {}
