class ZhouyuTools:
    def get_weather(self, city_name: str) -> str:
        return f"{city_name} 天晴"

    def __call__(self, input_text: str, tool_context: dict[str, object]) -> str:
        return self.get_weather(input_text)
