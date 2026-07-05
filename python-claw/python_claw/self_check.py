from __future__ import annotations

import json

from .feishu_message_receiver import FeishuMessageReceiver
from .java_claw_application import create_application
from .web_socket_handler import WebSocketHandler


def main() -> None:
    app = create_application()
    assert app.skill_loader.has_skill("agent-browser")
    reply = json.loads(WebSocketHandler(app.claw_agent).on_message(json.dumps({"message": "你好"})))
    assert reply["type"] == "reply"
    event = {
        "event_id": "check-1",
        "message_id": "msg-1",
        "chat_type": "group",
        "content": json.dumps({"text": "你好"}),
    }
    assert FeishuMessageReceiver(app.claw_agent).handle_event(event)["reply_type"] == "group"
    print("python-claw self check passed")


if __name__ == "__main__":
    main()
