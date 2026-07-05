import json
import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from python_claw.claw_agent import ClawAgent
from python_claw.feishu_message_receiver import FeishuMessageReceiver
from python_claw.feishu_tools import FeishuTools
from python_claw.claw_application import create_application
from python_claw.claw_properties import ClawProperties
from python_claw.memory.memory_service import MemoryService
from python_claw.memory.session_startup import SessionStartup
from python_claw.skill.skill_loader import SkillLoader
from python_claw.tool.memory.update_memory_tool import UpdateMemoryTool
from python_claw.web_socket_handler import WebSocketHandler


class PythonClawTests(unittest.TestCase):
    def test_workspace_templates_skills_and_prompt_are_initialized(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            props = ClawProperties(workspace_dir=root / "workspace")
            loader = SkillLoader()
            memory = MemoryService(props.workspace_dir, today=lambda: date(2026, 7, 4), now=lambda: datetime(2026, 7, 4, 9))
            startup = SessionStartup(props.workspace_dir)
            agent = ClawAgent(props, memory, startup, loader, template_dir=PROJECT_ROOT / "resources" / "template")

            agent.init()

            self.assertTrue((props.workspace_dir / "SOUL.md").exists())
            self.assertFalse((props.workspace_dir / "SOUL_CN.md").exists())
            self.assertTrue(loader.has_skill("agent-browser"))
            self.assertIn("# 引导任务", startup.get_system_prompt())
            self.assertIn("main_session", agent.agent_map)
            self.assertIn("feishu_session", agent.agent_map)

    def test_memory_service_and_update_memory_tool_write_notes(self):
        with tempfile.TemporaryDirectory() as temp:
            memory = MemoryService(Path(temp), today=lambda: date(2026, 7, 4), now=lambda: datetime(2026, 7, 4, 10, 30))
            tool = UpdateMemoryTool(memory)

            memory.ensure_today_note_exists()
            memory.log_conversation("用户", "你好")
            reply = tool.update_memory("喜欢离线演示", "preference")

            self.assertIn("# 2026-07-04", memory.read_today_note())
            self.assertIn("### 用户", memory.read_today_note())
            self.assertIn("记忆已更新", reply)
            self.assertIn("用户偏好：喜欢离线演示", memory.read_memory_md())

    def test_websocket_protocol_main_chat_and_new_session(self):
        app = create_application(workspace_dir=Path(tempfile.mkdtemp()))
        handler = WebSocketHandler(app.claw_agent)

        reply = json.loads(handler.on_message(json.dumps({"message": "你好"})))
        reset = json.loads(handler.on_message(json.dumps({"message": "/new"})))

        self.assertEqual(reply["type"], "reply")
        self.assertIn("网页助手", reply["message"])
        self.assertEqual(reset["message"], "已重置会话，我们可以开始新的对话了！")

    def test_feishu_receiver_parses_text_deduplicates_and_routes_reply_type(self):
        app = create_application(workspace_dir=Path(tempfile.mkdtemp()))
        receiver = FeishuMessageReceiver(app.claw_agent)
        event = {
            "event_id": "evt-1",
            "message_id": "msg-1",
            "chat_type": "group",
            "content": json.dumps({"text": "你好"}),
            "sender_open_id": "ou_1",
            "sender_user_id": "u_1",
        }

        first = receiver.handle_event(event)
        second = receiver.handle_event(event)

        self.assertEqual(first["reply_type"], "group")
        self.assertIn("飞书助手", first["text"])
        self.assertEqual(second["status"], "duplicate")
        self.assertEqual(receiver.parse_text_content("{bad"), "[无法解析的内容]")

    def test_feishu_tools_and_skill_loader(self):
        with tempfile.TemporaryDirectory() as temp:
            skills = Path(temp) / "skills"
            (skills / "demo").mkdir(parents=True)
            (skills / "demo" / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
            loader = SkillLoader()
            loader.initialize_skill_repository(skills)
            loaded = loader.load_all_skills()
            tools = FeishuTools(random_func=lambda low, high: low)

            self.assertEqual(loaded, ["demo"])
            self.assertIn("计算结果: 7.0", tools.calculate("3+4"))
            self.assertIn("北京 的天气", tools.get_weather("北京"))
            self.assertEqual(tools.generate_random_number(5, 3), "错误：最小值不能大于最大值")
            self.assertIn("英文", tools.translate("你好", "英文"))


if __name__ == "__main__":
    unittest.main()
