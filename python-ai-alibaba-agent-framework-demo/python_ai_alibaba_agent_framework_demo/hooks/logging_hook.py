class LoggingHook:
    def get_name(self) -> str:
        return "logging"

    def before_agent(self, state: dict[str, object]) -> dict[str, object]:
        state.setdefault("events", []).append("Agent 开始执行")
        return {}

    def after_agent(self, state: dict[str, object]) -> dict[str, object]:
        state.setdefault("events", []).append("Agent 执行完成")
        return {}
