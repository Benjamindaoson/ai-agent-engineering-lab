import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from python_ai_alibaba_agent_framework_demo.agent_application import create_application
from python_ai_alibaba_agent_framework_demo.hooks.zhouyu_model_hook import ZhouyuModelHook
from python_ai_alibaba_agent_framework_demo.interceptor.zhouyu_model_interceptor import (
    ZhouyuModelInterceptor,
)
from python_ai_alibaba_agent_framework_demo.model_config import ModelConfig
from python_ai_alibaba_agent_framework_demo.tools.date_tool import DateRequest, DateTool


class AgentFrameworkDemoTests(unittest.TestCase):
    def test_provider_config_supports_dashscope_and_deepseek(self):
        dashscope = ModelConfig.from_env({"PROVIDER": "dashscope", "DASHSCOPE_API_KEY": "d-key"})
        deepseek = ModelConfig.from_env({"PROVIDER": "deepseek", "DEEPSEEK_API_KEY": "s-key"})

        self.assertEqual(dashscope.model, "qwen3-max")
        self.assertEqual(deepseek.base_url, "https://api.deepseek.com")

    def test_hello_memory_hook_and_store_controller_flows(self):
        app = create_application()
        controller = app.controller

        self.assertIn("helloAgent", controller.hello("杭州天气"))
        self.assertIn("chunk:", "".join(controller.stream("杭州天气")))

        first = controller.memory("记住我叫周瑜", "class-1")
        second = controller.memory("我叫什么", "class-1")
        self.assertIn("history=2", second)
        self.assertEqual(len(app.memory_saver.list("class-1")), 2)
        self.assertIn("天晴", controller.store("上海天气", "store-1"))
        self.assertIn("Agent 开始执行", controller.hook("普通问题"))

    def test_human_feedback_pause_and_resume(self):
        controller = create_application().controller

        approval = controller.human_hook("查询天气", "thread-1")
        final = controller.human_agent_feedback("thread-1")

        self.assertIn("请确认是否执行工具", approval)
        self.assertIn("APPROVED", final)

    def test_multi_agent_and_agent_as_tool_flows(self):
        app = create_application()

        self.assertIn("planResult", app.sequential_agent.invoke("写一个计划"))
        self.assertIn("backendCode", app.parallel_agent.invoke("写代码"))
        self.assertEqual(app.llm_routing_agent.invoke("写python代码")["route"], "agent1")
        self.assertEqual(app.llm_routing_agent.invoke("写诗")["route"], "agent2")
        self.assertIn("executeAgent", app.zhouyu_agent.invoke("先计划再执行")["messages"][-1])
        self.assertIn("research_result", app.complex_workflow.invoke("创作主题"))
        self.assertIn("planAgent", app.tool_agent.call("制定计划").text)
        self.assertIn("api_key", app.controller.multi_agent("api_key 怎么查")["rag"])

    def test_hooks_interceptors_and_tools_are_visible(self):
        hook = ZhouyuModelHook()
        messages = [f"m{i}" for i in range(12)]
        self.assertEqual(hook.before_model({"messages": messages})["messages"], messages[-10:])

        interceptor = ZhouyuModelInterceptor()
        self.assertEqual(interceptor.intercept(["这涉及死亡"], lambda: "ok"), "输入有不适当的内容")

        result = DateTool().apply(DateRequest("北京"), {"input": "北京现在几点"})
        self.assertIn("北京", result)


if __name__ == "__main__":
    unittest.main()
