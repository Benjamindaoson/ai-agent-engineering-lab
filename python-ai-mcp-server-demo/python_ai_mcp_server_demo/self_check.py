from .mcp_server_application import McpServerApplication
from .weather_service import WeatherService


def main() -> None:
    app = McpServerApplication(WeatherService({"username": "zhouyu"}))
    assert app.call_tool("getWeather", {"cityName": "上海"}) == "天晴"
    assert "你好, 周瑜" in app.get_prompt("greeting", {"name": "周瑜"}).messages[0]["content"]["text"]
    assert app.read_resource("config://username") == "zhouyu"
    assert "下雨" in app.handle_json('{"method":"tools/call","params":{"name":"getWeather","arguments":{"cityName":"北京"}}}')
    print("python-ai-mcp-server-demo self check passed")


if __name__ == "__main__":
    main()
