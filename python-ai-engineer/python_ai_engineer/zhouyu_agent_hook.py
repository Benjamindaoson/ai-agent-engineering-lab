class ZhouyuAgentHook:
    DISPLAY_NAMES = {
        "architectAgent": "Architect",
        "backendAgent": "Backend",
        "frontendAgent": "Frontend",
        "reviewAgent": "Review",
        "plannerAgent": "Planner",
    }

    def __init__(self):
        self.events: list[str] = []

    def before_agent(self, agent_name: str) -> None:
        self.events.append(f"{self._display_name(agent_name)} Agent started")

    def after_agent(self, agent_name: str) -> None:
        self.events.append(f"{self._display_name(agent_name)} Agent finished")

    def _display_name(self, agent_name: str) -> str:
        for key, value in self.DISPLAY_NAMES.items():
            if key in agent_name:
                return value
        return agent_name
