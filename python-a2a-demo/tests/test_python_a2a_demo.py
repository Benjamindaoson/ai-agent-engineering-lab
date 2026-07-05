import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from python_a2a_demo.client.agent_config import AgentConfig
from python_a2a_demo.client.client_controller import ClientController
from python_a2a_demo.common import AgentCard, AgentRegistry
from python_a2a_demo.server.a2a_server_application import A2AServerApplication
from python_a2a_demo.server.zhouyu_tools import ZhouyuTools


class PythonA2ADemoTests(unittest.TestCase):
    def test_server_weather_tool_returns_sunny(self):
        self.assertEqual("天晴", ZhouyuTools().get_weather("上海"))
        self.assertEqual("天晴", ZhouyuTools().get_weather("北京"))

    def test_server_registers_weather_agent_card_and_invokes_agent(self):
        registry = AgentRegistry()
        app = A2AServerApplication(registry)

        app.start()
        card = registry.get_card("weatherAgent")
        result = registry.invoke("weatherAgent", "上海天气怎么样？")

        self.assertEqual("weatherAgent", card.name)
        self.assertEqual("专门用于获取天气的智能体", card.description)
        self.assertEqual(False, card.capabilities["streaming"])
        self.assertEqual("天晴", result["weatherResult"])

    def test_client_remote_agent_discovers_and_invokes_server_agent(self):
        registry = AgentRegistry()
        A2AServerApplication(registry).start()
        remote_agent = AgentConfig(registry).a2a_remote_agent()

        result = remote_agent.invoke("帮我查上海天气")

        self.assertEqual("天晴", result["weatherResult"])
        self.assertEqual("weatherAgent", remote_agent.card.name)

    def test_sequential_agent_runs_remote_agent_then_react_agent(self):
        registry = AgentRegistry()
        A2AServerApplication(registry).start()
        sequential_agent = AgentConfig(registry).sequential_agent()

        result = sequential_agent.invoke("上海天气")

        self.assertEqual("天晴", result["weatherResult"])
        self.assertIn("诗", result["reactAgentResult"])

    def test_client_controller_hello_returns_state_data(self):
        registry = AgentRegistry()
        A2AServerApplication(registry).start()
        controller = ClientController(AgentConfig(registry).a2a_remote_agent(), AgentConfig(registry).sequential_agent())

        result = controller.hello("上海天气")

        self.assertIn("weatherResult", result)
        self.assertIn("reactAgentResult", result)

    def test_agent_registry_errors_when_agent_missing(self):
        with self.assertRaises(KeyError):
            AgentRegistry().invoke("missing", "hello")


if __name__ == "__main__":
    unittest.main()
