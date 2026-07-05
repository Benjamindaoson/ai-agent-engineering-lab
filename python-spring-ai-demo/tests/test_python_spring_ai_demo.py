import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from python_spring_ai_demo.alarm_request import AlarmRequest
from python_spring_ai_demo.cosine_similarity import CosineSimilarity
from python_spring_ai_demo.mcp_controller import McpController
from python_spring_ai_demo.simple_ai import Document, SimpleEmbeddingModel, SimpleVectorStore
from python_spring_ai_demo.tool_controller import ToolController
from python_spring_ai_demo.zhouyu_controller import Poem, ZhouyuController, ZhouyuTextSplitter
from python_spring_ai_demo.zhouyu_tools import ZhouyuTools


class FakeChatClient:
    def __init__(self):
        self.calls = []

    def complete(self, prompt: str, system: str | None = None) -> str:
        self.calls.append((system, prompt))
        if "七言绝句" in prompt:
            return '{"title":"春江","author":"AI","content":"春江潮水连海平"}'
        return f"{system + ': ' if system else ''}answer:{prompt}"

    def stream(self, prompt: str, system: str | None = None):
        for token in self.complete(prompt, system).split(":"):
            yield token


class FakeMcpClient:
    def list_prompts(self):
        return ["greeting(name)"]

    def read_resource(self, uri: str):
        return f"resource:{uri}=zhouyu"


class PythonSpringAiDemoTests(unittest.TestCase):
    def test_cosine_similarity_matches_expected_math(self):
        self.assertEqual(14, CosineSimilarity.dot_product([1, 2, 3], [1, 2, 3]))
        self.assertAlmostEqual(1.0, CosineSimilarity.cosine_similarity([1, 2, 3], [1, 2, 3]))
        self.assertEqual(0, CosineSimilarity.cosine_similarity([0, 0], [1, 2]))

    def test_text_splitter_splits_blank_line_blocks(self):
        parts = ZhouyuTextSplitter().split("A\r\n\r\nB\n\n C")

        self.assertEqual(["A", "B", " C"], parts)

    def test_zhouyu_controller_covers_chat_memory_output_and_rag(self):
        store = SimpleVectorStore()
        controller = ZhouyuController(FakeChatClient(), SimpleEmbeddingModel(), store)

        self.assertIn("answer:hello", controller.chat("hello"))
        self.assertIn("你是周瑜老师", controller.system("你是谁"))
        self.assertIn("first", controller.memory("c1", "first"))
        self.assertIn("first", controller.memory("c1", "second"))
        self.assertIsInstance(controller.output("春天"), Poem)
        self.assertEqual(3, len(controller.embedding("abc")))
        stored = controller.store("Q：API-KEY？\nA：鉴权。\n\nQ：上限？\nA：3个。")
        self.assertEqual(2, len(stored))
        self.assertEqual("Q：API-KEY？\nA：鉴权。", controller.search("API-KEY", top_k=1)[0].text)
        self.assertIn("用以下信息回答问题", controller.rag_chat("API-KEY"))
        self.assertTrue(controller.evaluation("API-KEY").passing)
        self.assertEqual("metric", controller.test_metric())

    def test_tools_and_tool_controller_execute_tool_paths(self):
        tools = ZhouyuTools()
        controller = ToolController(FakeChatClient(), tools)

        alarm = AlarmRequest(time="2026年7月4日", address="长沙")
        self.assertIn("answer", controller.tool("现在几点"))
        self.assertIn("answer", controller.user_controlled_tool("保存代码"))
        self.assertIn("2026年7月4日", tools.set_alarm(alarm))
        self.assertIn("print", tools.save_code("print('hi')"))
        self.assertTrue(list(controller.stream_tool("现在几点")))

    def test_mcp_controller_uses_prompt_resource_and_tool_callbacks(self):
        controller = McpController(FakeChatClient(), [lambda message: f"tool:{message}"], [FakeMcpClient()])

        self.assertIn("answer", controller.mcp("hello"))
        self.assertEqual("greeting(name)", controller.mcp_prompt("unused"))
        self.assertEqual("resource:config://username=zhouyu", controller.mcp_resource("unused"))


if __name__ == "__main__":
    unittest.main()
