import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from python_agentscope_a2a_demo.a2a_client_application import A2AClientApplication
from python_agentscope_a2a_demo.a2a_server_spring_boot_application import create_server_application
from python_agentscope_a2a_demo.nacos_registry import InMemoryNacosRegistry
from python_agentscope_a2a_demo.weather_service import WeatherService


class PythonAgentScopeA2ADemoTests(unittest.TestCase):
    def test_server_registers_agent_card_with_weather_and_generate_skills(self):
        registry = InMemoryNacosRegistry()
        server = create_server_application(registry)

        card = registry.resolve("my-assistant")

        self.assertEqual(server.agent.name, "my-assistant")
        self.assertEqual(card["name"], "my-assistant")
        self.assertEqual([skill["id"] for skill in card["skills"]], ["getWeather", "generate"])

    def test_client_discovers_agent_and_streams_weather_response(self):
        registry = InMemoryNacosRegistry()
        create_server_application(registry)
        client = A2AClientApplication(registry)

        events = list(client.stream("my-assistant", "上海什么天气"))

        self.assertEqual([event["type"] for event in events], ["TASK_STARTED", "MESSAGE", "TASK_FINISHED"])
        self.assertIn("上海 的天气：晴天，25°C", events[1]["message"]["content"])

    def test_generate_tool_streams_progress_and_completion(self):
        registry = InMemoryNacosRegistry()
        create_server_application(registry)
        client = A2AClientApplication(registry)

        events = list(client.stream("my-assistant", "生成3个数据"))

        progress = [event["message"]["content"] for event in events if event["type"] == "MESSAGE"]
        self.assertEqual(progress, ["进度 0", "进度 1", "进度 2", "完成"])

    def test_weather_service_returns_demo_response(self):
        service = WeatherService()

        chunks = []
        result = service.generate(2, chunks.append)

        self.assertEqual(service.get_weather("长沙"), "长沙 的天气：晴天，25°C")
        self.assertEqual(chunks, ["进度 0", "进度 1"])
        self.assertEqual(result, "完成")


if __name__ == "__main__":
    unittest.main()
