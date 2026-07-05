class ConsultationQueryExpander:
    def expand(self, query: str, history: list[dict] | None = None) -> list[str]:
        return [message.get("content", "") for message in history or [] if message.get("role") == "user"]
