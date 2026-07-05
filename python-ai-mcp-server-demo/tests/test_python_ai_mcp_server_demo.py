import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from python_ai_mcp_server_demo.mcp_server_application import McpServerApplication
from python_ai_mcp_server_demo.weather_service import WeatherService


class PythonAiMcpServerDemoTests(unittest.TestCase):
    def test_weather_service_exposes_weather_tool(self):
        service = WeatherService()

        self.assertEqual("天晴", service.get_weather("上海"))
        self.assertEqual("下雨", service.get_weather("北京"))
        self.assertEqual("不知道", service.get_weather("长沙"))

    def test_weather_service_exposes_prompt_and_resource(self):
        service = WeatherService({"username": "zhouyu"})

        prompt = service.greeting("周瑜")

        self.assertEqual("Greeting", prompt.description)
        self.assertIn("你好, 周瑜", prompt.messages[0]["content"]["text"])
        self.assertEqual("zhouyu", service.get_config("username"))
        self.assertEqual("123", service.get_config("missing"))

    def test_application_lists_and_calls_mcp_capabilities(self):
        app = McpServerApplication(WeatherService({"username": "zhouyu"}))

        tools = app.list_tools()
        prompts = app.list_prompts()
        resources = app.list_resources()

        self.assertEqual("getWeather", tools[0]["name"])
        self.assertEqual("greeting", prompts[0]["name"])
        self.assertEqual("config://{key}", resources[0]["uri"])
        self.assertEqual("天晴", app.call_tool("getWeather", {"cityName": "上海"}))
        self.assertIn("你好, 周瑜", app.get_prompt("greeting", {"name": "周瑜"}).messages[0]["content"]["text"])
        self.assertEqual("zhouyu", app.read_resource("config://username"))

    def test_application_handles_json_rpc_style_requests(self):
        app = McpServerApplication(WeatherService({"username": "zhouyu"}))

        response = app.handle_json(
            json.dumps({"method": "tools/call", "params": {"name": "getWeather", "arguments": {"cityName": "北京"}}})
        )

        self.assertEqual({"result": "下雨"}, json.loads(response))


if __name__ == "__main__":
    unittest.main()
