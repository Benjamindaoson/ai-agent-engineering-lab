class WeatherService:
    def get_weather(self, city: str) -> str:
        return f"{city} 的天气：晴天，25°C"

    def generate(self, count: int, emit) -> str:
        for index in range(count):
            emit(f"进度 {index}")
        return "完成"

    def query(self, sql: str, ctx) -> str:
        user_id = getattr(ctx, "user_id", None) or str(ctx or "unknown")
        return f"用户 {user_id} 的数据"
