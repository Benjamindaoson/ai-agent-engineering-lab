class WeatherService:
    def get_weather(self, city: str) -> str:
        return f"{city} 的天气：晴天，25°C"

    def generate(self, count: int, emit) -> str:
        for index in range(count):
            emit(f"进度 {index}")
        return "完成"
