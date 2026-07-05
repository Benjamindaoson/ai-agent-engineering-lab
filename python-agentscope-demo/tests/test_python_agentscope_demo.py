import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from python_agentscope_demo.agent_skill_demo1 import run_agent_skill_demo1
from python_agentscope_demo.agent_skill_demo2 import run_agent_skill_demo2
from python_agentscope_demo.agent_skill_demo3 import run_agent_skill_demo3
from python_agentscope_demo.core import (
    ConfirmationHook,
    FakeChatModel,
    InMemoryMemory,
    Msg,
    MsgHub,
    ReActAgent,
    Toolkit,
    fanout,
    sequential,
)
from python_agentscope_demo.demos import (
    run_human_in_the_loop_demo,
    run_mcp_demo,
    run_rag_demo,
    run_studio_demo,
    run_structured_output_demo,
    run_vision_demo,
)
from python_agentscope_demo.product.product_info import ProductInfo
from python_agentscope_demo.tools.email_service import EmailService
from python_agentscope_demo.tools.weather_service import WeatherService


class PythonAgentScopeDemoTests(unittest.TestCase):
    def test_agent_tool_preset_context_and_group_behaviors(self):
        toolkit = Toolkit()
        toolkit.create_tool_group("basic", "基础工具")
        toolkit.register_tool(WeatherService(), group="basic")
        toolkit.register_tool(EmailService(), preset_parameters={"send": {"apiKey": "secret-key"}})
        toolkit.register_context("user", "user-123")
        agent = ReActAgent("Assistant", "你是一个有帮助的 AI 助手。", FakeChatModel(), toolkit=toolkit)

        weather = agent.call(Msg.text("长沙什么天气"))
        data = agent.call(Msg.text("查询最近一个月的订单数据"))
        mail = agent.call(Msg.text("发邮件给zhouyu,主题为Java"))

        self.assertIn("长沙 的天气", weather.text)
        self.assertIn("user-123", data.text)
        self.assertEqual(mail.text, "已发送")
        self.assertNotIn("secret-key", mail.visible_tool_input)

        toolkit.update_tool_groups(["basic"], False)
        disabled = agent.call(Msg.text("上海什么天气"))
        self.assertIn("没有可用工具", disabled.text)

    def test_hook_emitter_and_human_confirmation(self):
        toolkit = Toolkit()
        toolkit.register_tool(WeatherService())
        chunks = []
        toolkit.set_chunk_callback(lambda use, result: chunks.append((use["name"], result)))

        agent = ReActAgent("Assistant", "你是一个有帮助的 AI 助手。", FakeChatModel(), toolkit=toolkit)
        generated = agent.call(Msg.text("生成3个数据"))
        self.assertEqual(generated.text, "完成")
        self.assertEqual([chunk[1] for chunk in chunks], ["进度 0", "进度 1", "进度 2", "完成"])

        guarded = ReActAgent(
            "Assistant",
            "你是一个有帮助的 AI 助手。",
            FakeChatModel(),
            toolkit=toolkit,
            hooks=[ConfirmationHook()],
        )
        pending = guarded.call(Msg.text("生成2个数据"))
        self.assertTrue(pending.pending_tools)
        self.assertEqual(run_human_in_the_loop_demo(confirm=False), "操作已取消")

    def test_memory_session_pipeline_and_message_hub(self):
        with tempfile.TemporaryDirectory() as temp:
            memory = InMemoryMemory()
            memory.add(Msg.text("我是周瑜", name="user"))
            memory.save_to(Path(temp), "session1")

            restored = InMemoryMemory()
            restored.load_from(Path(temp), "session1")
            self.assertEqual(len(restored.messages), 1)

        researcher = ReActAgent("Researcher", "你是一名研究员。", FakeChatModel())
        writer = ReActAgent("Writer", "你是一名作家。", FakeChatModel())
        editor = ReActAgent("Editor", "你是一名编辑。", FakeChatModel())
        final_msg = sequential([researcher, writer, editor], Msg.text("人工智能在医疗领域的应用"))
        self.assertEqual(final_msg.name, "Editor")
        self.assertIn("编辑", final_msg.text)

        views = fanout(
            [
                ReActAgent("Optimist", "你是一个乐观主义者。", FakeChatModel()),
                ReActAgent("Pessimist", "你是一个悲观主义者。", FakeChatModel()),
                ReActAgent("Realist", "你是一个现实主义者。", FakeChatModel()),
            ],
            Msg.text("如何提高自己的技能？"),
        )
        self.assertEqual([msg.name for msg in views], ["Optimist", "Pessimist", "Realist"])

        alice = ReActAgent("Alice", "你是 Alice，一位友好的老师。", FakeChatModel(), memory=InMemoryMemory())
        bob = ReActAgent("Bob", "你是 Bob，一位好奇的学生。", FakeChatModel(), memory=InMemoryMemory())
        with MsgHub([alice, bob], announcement=Msg.text("欢迎来到讨论！", name="system")) as hub:
            hub.enter()
        self.assertEqual(len(alice.memory.messages), 1)
        self.assertEqual(len(bob.memory.messages), 1)

    def test_structured_skill_rag_mcp_vision_and_studio_entries(self):
        product = run_structured_output_demo()
        self.assertIsInstance(product, ProductInfo)
        self.assertEqual(product.name, "课程演示产品")

        self.assertIn("日常生活", run_agent_skill_demo1())
        self.assertIn("Java", run_agent_skill_demo2())
        self.assertIn("解释代码", run_agent_skill_demo3())
        self.assertIn("API-KEY", run_rag_demo("什么是apikey"))
        self.assertIn("MCP", run_mcp_demo("上海什么天气"))
        self.assertIn("base64", run_vision_demo())
        self.assertIn("Studio", run_studio_demo(["你好", "exit"]))


if __name__ == "__main__":
    unittest.main()
