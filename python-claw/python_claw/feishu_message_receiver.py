from __future__ import annotations

import json

from .claw_agent import ClawAgent, FEISHU_SESSION_ID


class FeishuMessageReceiver:
    def __init__(self, claw_agent: ClawAgent) -> None:
        self.claw_agent = claw_agent
        self.processed_event_ids: set[str] = set()

    def handle_event(self, event: dict[str, str]) -> dict[str, str]:
        event_id = event.get("event_id", "")
        if event_id and event_id in self.processed_event_ids:
            return {"status": "duplicate", "event_id": event_id}
        if event_id:
            self.processed_event_ids.add(event_id)
        try:
            return self.process_and_reply_message(event)
        except Exception:
            # ponytail: failed processing should allow retry instead of marking the event handled.
            if event_id:
                self.processed_event_ids.discard(event_id)
            raise

    def process_and_reply_message(self, event: dict[str, str]) -> dict[str, str]:
        text = self.parse_text_content(event.get("content", ""))
        if text.strip() == "/new":
            self.claw_agent.new_session(FEISHU_SESSION_ID)
            reply = "已重置会话，我们可以开始新的对话了！"
        else:
            reply = self.claw_agent.feishu_chat(text)
        chat_type = event.get("chat_type", "")
        if chat_type == "p2p":
            return {"reply_type": "private", "receive_id": event.get("sender_open_id", ""), "text": reply}
        if chat_type == "group":
            return {"reply_type": "group", "message_id": event.get("message_id", ""), "text": reply}
        return {"reply_type": "ignored", "text": reply}

    def parse_text_content(self, json_content: str) -> str:
        try:
            content = json.loads(json_content)
            return content.get("text", "[非文本消息]")
        except (json.JSONDecodeError, TypeError):
            return "[无法解析的内容]"
