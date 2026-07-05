import json

from .mcp_server_application import McpServerApplication
from .weather_service import WeatherService


def main() -> None:
    app = McpServerApplication(WeatherService({"username": "zhouyu"}))

    print("1. tools/list")
    print(json.dumps(app.list_tools(), ensure_ascii=False, indent=2))

    print("\n2. tools/call")
    print(app.call_tool("getWeather", {"cityName": "上海"}))

    print("\n3. prompts/list + prompts/get")
    print(json.dumps(app.list_prompts(), ensure_ascii=False, indent=2))
    print(json.dumps(app.get_prompt("greeting", {"name": "周瑜"}).__dict__, ensure_ascii=False, indent=2))

    print("\n4. resources/list + resources/read")
    print(json.dumps(app.list_resources(), ensure_ascii=False, indent=2))
    print(app.read_resource("config://username"))

    print("\n5. JSON-style request")
    print(app.handle_json(json.dumps({"method": "tools/call", "params": {"name": "getWeather", "arguments": {"cityName": "北京"}}}, ensure_ascii=False)))


if __name__ == "__main__":
    main()
