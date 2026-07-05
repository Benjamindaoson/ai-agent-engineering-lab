import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from python_ai_alibaba_graph_demo.blog.content_node_action import ContentNodeAction
from python_ai_alibaba_graph_demo.blog.title_node_action import TitleNodeAction
from python_ai_alibaba_graph_demo.graph_application import create_application
from python_ai_alibaba_graph_demo.graph_config import GraphConfig
from python_ai_alibaba_graph_demo.graph_observation_auto_configuration import (
    GraphObservationAutoConfiguration,
)
from python_ai_alibaba_graph_demo.graph_observation_properties import GraphObservationProperties
from python_ai_alibaba_graph_demo.interrupt.interruptable_node_action import (
    InterruptableNodeAction,
)
from python_ai_alibaba_graph_demo.model_config import ModelConfig


class GraphDemoTests(unittest.TestCase):
    def test_provider_config_defaults_to_dashscope_graph_model(self):
        config = ModelConfig.from_env({"PROVIDER": "dashscope", "DASHSCOPE_API_KEY": "d-key"})

        self.assertEqual(config.model, "qwen3-max")
        self.assertIn("dashscope", config.base_url)

    def test_simple_graph_generates_title_then_content_and_streams_content(self):
        app = create_application()

        result = app.controller.simple("AI Agent")
        stream = app.controller.stream("AI Agent")

        self.assertIn("title", result)
        self.assertIn("content", result)
        self.assertIn("AI Agent", result["title"])
        self.assertTrue(all(chunk.startswith("content:") for chunk in stream))

    def test_conditional_graph_routes_poem_or_code(self):
        controller = create_application().controller

        poem = controller.conditional("写一首诗")
        code = controller.conditional("写Java代码")

        self.assertEqual(poem["intentionResult"], "1")
        self.assertIn("七言绝句", poem["result"])
        self.assertEqual(code["intentionResult"], "2")
        self.assertIn("Java代码", code["result"])

    def test_thread_and_memory_saver_use_store_and_checkpoints(self):
        app = create_application()

        first = app.controller.thread("class-1", "你好")
        second = app.controller.memory_saver_endpoint("class-1", "继续")

        self.assertIn("周瑜", first)
        self.assertIn("继续", second)
        self.assertEqual(len(app.memory_saver.list("class-1")), 2)

    def test_interrupt_before_and_inside_can_pause_then_continue(self):
        controller = create_application().controller

        paused = controller.interrupt_before_state_graph("before-1")
        repaused = controller.continue_before_state_graph("before-1", "unknown")
        resumed = controller.continue_before_state_graph("before-1", "next")
        inside_paused = controller.interrupt_state_graph("inside-1")
        inside_resumed = controller.continue_state_graph("inside-1", "next")

        self.assertIn("中断了，请提供用户的年龄", paused)
        self.assertIn("再次中断了，请提供用户的年龄", repaused)
        self.assertIn("我是节点3", "".join(resumed))
        self.assertIn("中断了，请提供用户的年龄", inside_paused)
        self.assertIn("我是节点3", "".join(inside_resumed))

    def test_parallel_subgraph_and_node_actions_are_visible(self):
        app = create_application()

        self.assertEqual(app.controller.parallel()["next_node"], "__END__")
        self.assertEqual(app.controller.sub_graph()["ids"], {"a": "A", "b1": "B1", "b2": "B2", "c": "C"})
        self.assertIn("爆款文章标题", TitleNodeAction().apply({"subject": "课程"})["title"])
        self.assertIn("爆款文章", ContentNodeAction().apply({"title": "标题"})["content"])
        self.assertTrue(InterruptableNodeAction().interrupt("node2", {}, {})["interrupted"])

    def test_observation_properties_build_compile_config(self):
        properties = GraphObservationProperties(enabled=True)
        config = GraphObservationAutoConfiguration(properties).observation_graph_compile_config()

        self.assertTrue(config.observation_enabled)
        self.assertIn("graphObservationLifecycleListener", config.lifecycle_listeners)


if __name__ == "__main__":
    unittest.main()
