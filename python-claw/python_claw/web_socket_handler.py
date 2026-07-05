from __future__ import annotations

import json

from .claw_agent import ClawAgent, MAIN_SESSION_ID


class WebSocketHandler:
    def __init__(self, claw_agent: ClawAgent) -> None:
        self.claw_agent = claw_agent

    def on_message(self, message: str) -> str:
        try:
            user_message = json.loads(message).get("message", "")
            if user_message.strip() == "/new":
                self.claw_agent.new_session(MAIN_SESSION_ID)
                reply = "已重置会话，我们可以开始新的对话了！"
            else:
                reply = self.claw_agent.main_chat(user_message)
            return json.dumps({"type": "reply", "message": reply}, ensure_ascii=False)
        except Exception as exc:
            # ponytail: websocket boundary returns JSON errors instead of crashing the demo server.
            return json.dumps({"type": "error", "message": f"处理失败：{exc}"}, ensure_ascii=False)
